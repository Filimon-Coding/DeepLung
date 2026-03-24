import os
import re
import pandas as pd
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchio as tio
import SimpleITK as sitk
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from pathlib import Path
from tqdm import tqdm

############################################
# CONFIGURATION
############################################
random.seed(42)
torch.manual_seed(42)

CSV_PATH = "list3.2.csv"         
BASE_DIR = Path(os.getcwd())
DATA_DIR = BASE_DIR / "Data"
MODEL_DIR = BASE_DIR / "checkpoints"
MODEL_DIR.mkdir(exist_ok=True)

NUM_EPOCHS = 40
BATCH_SIZE = 4 
LR = 1e-4

# CHECK DEVICE
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"--- SYSTEM INFO ---")
print(f"Target Device: {device}")

############################################
# DATASET DEFINITION
############################################

class NiiDataset(Dataset):
    def __init__(self, stage, root_dir, csv_path, transform=None):
        self.samples = []
        self.transform = transform
        try:
            df = pd.read_csv(csv_path)
        except:
            df = pd.DataFrame()

        categories = ["Benign", "Malignancy"]
        for label_idx, cat in enumerate(categories):
            folder_path = Path(root_dir) / stage / cat
            if not folder_path.exists(): continue
            for img_path in folder_path.glob("*.nii.gz"):
                numbers = re.findall(r'\d+', img_path.name)
                case_id = int(numbers[-1]) if numbers else -1
                coords = None
                if not df.empty and case_id != -1:
                    match = df[df['case'] == case_id]
                    if not match.empty:
                        coords = (float(match['x loc.'].values[0]), 
                                  float(match['y loc.'].values[0]), 
                                  float(match['sliceno'].values[0]))
                self.samples.append((img_path, label_idx, coords))

    def __len__(self): return len(self.samples)

    def __getitem__(self, idx):
        img_path, label, coords = self.samples[idx]
        full_img = sitk.ReadImage(str(img_path))
        full_size = np.array(full_img.GetSize()) 
        
        if np.any(full_size < 128):
            pad = np.maximum(0, 128 - full_size)
            full_img = sitk.ConstantPad(full_img, [0,0,0], pad.tolist(), 0)
            full_size = np.array(full_img.GetSize())

        cx, cy, cz = coords if coords else full_size // 2
        start_index = [
            int(max(0, min(cx - 64, full_size[0] - 128))),
            int(max(0, min(cy - 64, full_size[1] - 128))),
            int(max(0, min(cz - 64, full_size[2] - 128)))
        ]

        roi = sitk.RegionOfInterest(full_img, [128, 128, 128], start_index)
        image_array = sitk.GetArrayFromImage(roi)
        image_tensor = torch.from_numpy(image_array).float().unsqueeze(0)
        
        subject = tio.Subject(mri=tio.ScalarImage(tensor=image_tensor))
        if self.transform: subject = self.transform(subject)
            
        return subject.mri.data, label, str(img_path), np.array(start_index)

############################################
# MODEL & HEATMAP ENGINE
############################################

class BasicBlock3D(nn.Module):
    def __init__(self, in_c, out_c, stride=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(in_c, out_c, 3, stride=stride, padding=1, bias=False),
            nn.BatchNorm3d(out_c), nn.ReLU(inplace=True),
            nn.Conv3d(out_c, out_c, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm3d(out_c)
        )
        self.shortcut = nn.Sequential()
        if stride != 1 or in_c != out_c:
            self.shortcut = nn.Sequential(nn.Conv3d(in_c, out_c, 1, stride=stride, bias=False), nn.BatchNorm3d(out_c))
    def forward(self, x): return F.relu(self.conv(x) + self.shortcut(x))

class ResNet3D(nn.Module):
    def __init__(self):
        super().__init__()
        self.prep = nn.Sequential(nn.Conv3d(1, 32, 7, stride=2, padding=3, bias=False), nn.BatchNorm3d(32), nn.ReLU(inplace=True), nn.MaxPool3d(3, stride=2, padding=1))
        self.layer1 = BasicBlock3D(32, 64); self.layer2 = BasicBlock3D(64, 128, stride=2); self.layer3 = BasicBlock3D(128, 256, stride=2)
        self.avgpool = nn.AdaptiveAvgPool3d(1); self.classifier = nn.Linear(256, 2)
    def forward(self, x):
        x = self.prep(x); x = self.layer1(x); x = self.layer2(x); x = self.layer3(x)
        return self.classifier(self.avgpool(x).flatten(1))

def get_heatmap(model, img_tensor, target_label):
    model.eval()
    activations, gradients = [], []
    def save_act(m, i, o): activations.append(o)
    def save_grad(m, gi, go): gradients.append(go[0])
    h1 = model.layer3.register_forward_hook(save_act)
    h2 = model.layer3.register_full_backward_hook(save_grad)
    output = model(img_tensor.to(device))
    model.zero_grad()
    output[0, target_label].backward()
    weights = torch.mean(gradients[0], dim=(2, 3, 4), keepdim=True)
    cam = F.relu(torch.sum(weights * activations[0], dim=1).squeeze())
    cam_resized = F.interpolate(cam.detach().cpu().unsqueeze(0).unsqueeze(0), size=(128, 128, 128), mode='trilinear').squeeze()
    h1.remove(); h2.remove()
    return cam_resized.numpy()

############################################
# DATA LOADERS & COUNTS
############################################

train_ds = NiiDataset("Train", DATA_DIR, CSV_PATH, tio.RescaleIntensity(out_min_max=(0,1)))
test_ds = NiiDataset("Test", DATA_DIR, CSV_PATH, tio.RescaleIntensity(out_min_max=(0,1)))

train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_ds, batch_size=BATCH_SIZE, shuffle=False)

print(f"--- DATASET INFO ---")
print(f"Total Training Images: {len(train_ds)}")
print(f"Total Test Images: {len(test_ds)}")

model = ResNet3D().to(device)
optimizer = optim.Adam(model.parameters(), lr=LR)
criterion = nn.CrossEntropyLoss()

history = {'train_loss': [], 'train_acc': [], 'test_loss': [], 'test_acc': []}

############################################
# TRAINING LOOP (EPOCH STATS)
############################################

for epoch in range(NUM_EPOCHS):
    model.train()
    r_loss, t_correct, t_total = 0, 0, 0
    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}")
    
    for imgs, lbls, paths, starts in pbar:
        imgs, lbls = imgs.to(device), lbls.to(device)
        optimizer.zero_grad()
        out = model(imgs); loss = criterion(out, lbls)
        loss.backward(); optimizer.step()
        
        r_loss += loss.item()
        t_correct += (out.argmax(1)==lbls).sum().item()
        t_total += lbls.size(0)

    # EVALUATION PER EPOCH
    model.eval()
    v_loss, v_correct, v_total = 0, 0, 0
    with torch.no_grad():
        for imgs, lbls, paths, starts in test_loader:
            imgs, lbls = imgs.to(device), lbls.to(device)
            out = model(imgs)
            loss = criterion(out, lbls)
            v_loss += loss.item()
            v_correct += (out.argmax(1)==lbls).sum().item()
            v_total += lbls.size(0)

    history['train_loss'].append(r_loss/len(train_loader))
    history['train_acc'].append(100*t_correct/t_total)
    history['test_loss'].append(v_loss/len(test_loader))
    history['test_acc'].append(100*v_correct/v_total)

    print(f"\n--- Epoch {epoch+1} Results ---")
    print(f"Train Loss: {history['train_loss'][-1]:.4f} | Train Acc: {history['train_acc'][-1]:.2f}%")
    print(f"Test Loss: {history['test_loss'][-1]:.4f}  | Test Acc: {history['test_acc'][-1]:.2f}%")

############################################
# FINAL GLOBAL AUDIT (RECONSTRUCTING SLICE 43)
############################################

TARGET_ID = "0001" # Target Case
found = None
for imgs, lbls, paths, starts in test_loader:
    for i, p in enumerate(paths):
        if TARGET_ID in p: found = (imgs[i:i+1], lbls[i], paths[i], starts[i]); break
    if found: break

if found:
    img_t, lbl_t, path_t, start_pt = found
    heatmap = get_heatmap(model, img_t, target_label=1)
    
    # 1. Load FULL 512x512 array
    full_img = sitk.ReadImage(path_t)
    full_arr = sitk.GetArrayFromImage(full_img)
    
    # 2. Get the global slice number
    sx, sy, sz = start_pt.numpy()
    rel_z = np.unravel_index(np.argmax(heatmap), heatmap.shape)[0]
    physical_z = sz + rel_z # This should now be 43!
    
    # 3. Project 128 heatmap to 512 space
    full_hm = np.zeros_like(full_arr, dtype=np.float32)
    full_hm[sz:sz+128, sy:sy+128, sx:sx+128] = heatmap

    plt.figure(figsize=(20, 6))
    
    # LOSS CURVE
    plt.subplot(1, 4, 1); plt.plot(history['train_loss'], label='Train'); plt.plot(history['test_loss'], label='Test'); plt.legend(); plt.title("Loss Curve")
    
    # ACCURACY CURVE
    plt.subplot(1, 4, 2); plt.plot(history['train_acc'], label='Train'); plt.plot(history['test_acc'], label='Test'); plt.legend(); plt.title("Accuracy Curve")

    # GLOBAL ORIGINAL SLICE
    plt.subplot(1, 4, 3)
    plt.imshow(full_arr[physical_z], cmap='bone')
    plt.title(f"GLOBAL SLICE: {physical_z}") # Check this title!
    plt.axis('off')

    # GLOBAL HEATMAP
    plt.subplot(1, 4, 4)
    plt.imshow(full_arr[physical_z], cmap='bone')
    plt.imshow(full_hm[physical_z], cmap='jet', alpha=0.45)
    plt.title(f"Heatmap on Global Slice")
    plt.axis('off')

    plt.show()
    print(f"\nFinal Audit: Model detected nodule at Physical Slice {physical_z}")