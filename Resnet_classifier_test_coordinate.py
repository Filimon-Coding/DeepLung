import os
import pandas as pd
import time
import random
import numpy as np
from pathlib import Path
from tqdm import tqdm

import torch
import torch.nn as nn
import torch.optim as optim
import torchio as tio
import SimpleITK as sitk
from torch.utils.data import Dataset, DataLoader

# Metrics imports
from sklearn.metrics import confusion_matrix, precision_score, recall_score, f1_score

# Seeds for reproducibility
random.seed(42)
torch.manual_seed(42)
np.random.seed(42)

############################################
# PATHS AND CONFIGURATION
############################################
CSV_PATH = "list3.2.csv"
DATA_DIR = Path(r"D:\Oslomet\bachlor\Bachelor-CRAI\Data") 
MODEL_DIR = Path("checkpoints")
MODEL_DIR.mkdir(exist_ok=True)

LATEST_MODEL_PATH = MODEL_DIR / "resnet3d_latest.pth"

############################################
# DATASET & LOADERS
############################################

class NiiDataset(Dataset):
    def __init__(self, csv_path, root_dir, transform=None):
        self.root_dir = Path(root_dir)
        self.transform = transform
        self.samples = []
        
        if not self.root_dir.exists():
            print(f"ERROR: Directory {self.root_dir} not found.")
            return

        # 1. Match Malignant files using CSV coordinates
        df = pd.read_csv(csv_path)
        mal_dir = self.root_dir / "Malignancy"
        if mal_dir.exists():
            all_mal_files = {f.name: f for f in mal_dir.rglob("*.nii.gz")}
            for _, row in df.iterrows():
                case_id = str(int(row['case'])).zfill(4)
                expected_filename = f"LIDC-IDRI-{case_id}_CT.nii.gz"
                
                if expected_filename in all_mal_files:
                    self.samples.append({
                        'path': all_mal_files[expected_filename],
                        'label': 1,
                        'x': row['x loc.'], 'y': row['y loc.'], 'z': row['sliceno'],
                        'is_centric': True
                    })

        # 2. Add Benign files (even if not in CSV)
        ben_dir = self.root_dir / "Benign"
        if ben_dir.exists():
            for ben_file in ben_dir.rglob("*.nii.gz"):
                self.samples.append({
                    'path': ben_file,
                    'label': 0,
                    'x': None, 'y': None, 'z': None,
                    'is_centric': False
                })

        # Summary statistics
        mal_count = sum(1 for s in self.samples if s['label'] == 1)
        ben_count = sum(1 for s in self.samples if s['label'] == 0)
        print(f"--- Dataset Loaded: {len(self.samples)} total samples ---")
        print(f"--- [Malignant: {mal_count}] [Benign: {ben_count}] ---")

    def extract_centric_patch(self, tensor, x, y, z, size=128):
        half = size // 2
        padded = torch.nn.functional.pad(tensor, (half, half, half, half, half, half))
        z_idx, y_idx, x_idx = int(z) + half, int(y) + half, int(x) + half
        return padded[:, z_idx-half:z_idx+half, y_idx-half:y_idx+half, x_idx-half:x_idx+half]

    def extract_center_patch(self, tensor, size=128):
        _, d, h, w = tensor.shape
        z_mid, y_mid, x_mid = d // 2, h // 2, w // 2
        half = size // 2
        return tensor[:, z_mid-half:z_mid+half, y_mid-half:y_mid+half, x_mid-half:x_mid+half]

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        sample = self.samples[idx]
        image = sitk.ReadImage(str(sample['path']))
        img_array = sitk.GetArrayFromImage(image)
        img_tensor = torch.from_numpy(img_array).float().unsqueeze(0)
        
        if sample['is_centric']:
            img_tensor = self.extract_centric_patch(img_tensor, sample['x'], sample['y'], sample['z'])
        else:
            img_tensor = self.extract_center_patch(img_tensor)
            
        # Ensure correct size (some scans might be smaller than 128)
        if img_tensor.shape[1:] != (128, 128, 128):
            img_tensor = torch.nn.functional.interpolate(
                img_tensor.unsqueeze(0), size=(128, 128, 128), mode='trilinear', align_corners=False
            ).squeeze(0)
        
        subject = tio.Subject(mri=tio.ScalarImage(tensor=img_tensor))
        if self.transform:
            subject = self.transform(subject)
        return subject.mri.data, sample['label']

# Augmentations
train_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.RandomFlip(axes=(0, 1, 2)),
    tio.RandomGamma(log_gamma=(-0.1, 0.1)),
    tio.RandomNoise(std=(0, 0.01)),
])
test_transform = tio.Compose([tio.RescaleIntensity(out_min_max=(0, 1))])

train_dataset = NiiDataset(CSV_PATH, DATA_DIR / "Train", transform=train_transform)
test_dataset  = NiiDataset(CSV_PATH, DATA_DIR / "Test", transform=test_transform)

train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
test_loader  = DataLoader(test_dataset, batch_size=2, shuffle=False)

############################################
# MODEL ARCHITECTURE (ResNet-3D)
############################################

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        mid = out_channels // 2
        self.conv = nn.Sequential(
            nn.Conv3d(in_channels, mid, 1), nn.BatchNorm3d(mid), nn.ReLU(),
            nn.Conv3d(mid, mid, 3, stride=stride, padding=1), nn.BatchNorm3d(mid), nn.ReLU(),
            nn.Conv3d(mid, out_channels, 1), nn.BatchNorm3d(out_channels)
        )
        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv3d(in_channels, out_channels, 1, stride=stride),
                nn.BatchNorm3d(out_channels)
            )
    def forward(self, x): return torch.relu(self.conv(x) + self.shortcut(x))

class ResNetShort(nn.Module):
    def __init__(self):
        super().__init__()
        self.prep = nn.Sequential(nn.Conv3d(1, 32, 3, padding=1), nn.BatchNorm3d(32), nn.ReLU())
        self.layer1 = ResidualBlock(32, 64, stride=2)
        self.layer2 = ResidualBlock(64, 128, stride=2)
        self.layer3 = ResidualBlock(128, 256, stride=2)
        self.avgpool = nn.AdaptiveAvgPool3d(1)
        self.dropout = nn.Dropout(p=0.4)
        self.classifier = nn.Linear(256, 2)

    def forward(self, x):
        x = self.prep(x); x = self.layer1(x); x = self.layer2(x); x = self.layer3(x)
        x = self.avgpool(x).flatten(1); x = self.dropout(x)
        return self.classifier(x)

############################################
# EXECUTION & TRAINING LOOP
############################################

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ResNetShort().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=5e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', patience=3, factor=0.5)

num_epochs = 2
best_accuracy = 0.0

if len(train_dataset) > 0:
    print(f"--- Training running on: {device} ---")
    
    for epoch in range(num_epochs):
        # --- TRAINING ---
        model.train()
        train_pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Train]")
        for images, labels in train_pbar:
            images, labels = images.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            train_pbar.set_postfix(loss=f"{loss.item():.4f}")

        # --- VALIDATION & METRICS ---
        model.eval()
        all_preds, all_labels = [], []
        val_pbar = tqdm(test_loader, desc=f"Epoch {epoch+1}/{num_epochs} [Val]")
        
        with torch.no_grad():
            for images, labels in val_pbar:
                images = images.to(device)
                outputs = model(images)
                preds = outputs.argmax(dim=1).cpu().numpy()
                all_preds.extend(preds)
                all_labels.extend(labels.numpy())

        # Finalize Metrics
        all_preds, all_labels = np.array(all_preds), np.array(all_labels)
        epoch_acc = 100 * (all_preds == all_labels).mean()
        prec = precision_score(all_labels, all_preds, zero_division=0)
        rec = recall_score(all_labels, all_preds, zero_division=0)
        f1 = f1_score(all_labels, all_preds, zero_division=0)
        cm = confusion_matrix(all_labels, all_preds, labels=[0, 1])

        print(f"\n--- Epoch {epoch+1} Metrics ---")
        print(f"Accuracy: {epoch_acc:.2f}% | Precision: {prec:.4f} | Recall: {rec:.4f} | F1: {f1:.4f}")
        print(f"Confusion Matrix:\n{cm}")
        print("---------------------------\n")

        scheduler.step(epoch_acc)

        if epoch_acc > best_accuracy:
            best_accuracy = epoch_acc
            torch.save(model.state_dict(), MODEL_DIR / f"best_model_acc{epoch_acc:.2f}.pth")

print(f"\n--- Complete. Best Accuracy: {best_accuracy:.2f}% ---")