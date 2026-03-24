import os
import time
import random
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import torchio as tio
import SimpleITK as sitk
import matplotlib
matplotlib.use("Agg")   # headless — no display needed on CI
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader
from tqdm import tqdm

############################################
# PATHS AND CONFIGURATION
############################################
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

DATA_DIR  = Path("Data")
MODEL_DIR = Path("checkpoints")
MODEL_DIR.mkdir(exist_ok=True)

LATEST_MODEL_PATH = MODEL_DIR / "resnet3d_latest.pth"

############################################
# TRAINING SETTINGS
############################################
CROP_SIZE  = (192, 192, 192)   # scaled up from 128 — more context around nodules
BATCH_SIZE = 2                 # reduced to fit larger volumes in VRAM
NUM_EPOCHS = 50
NUM_WORKERS = 0
PIN_MEMORY  = False

############################################
# DATASET
############################################
class NiiDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.samples  = []
        self.transform = transform
        for label, folder in enumerate(["Benign", "Malignancy"]):
            folder_path = Path(root_dir) / folder
            if not folder_path.exists():
                continue
            for img_path in folder_path.glob("*.nii.gz"):
                self.samples.append((img_path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]

        image_np = sitk.GetArrayFromImage(sitk.ReadImage(str(img_path)))
        volume   = torch.from_numpy(image_np).float().unsqueeze(0)

        # SimpleITK gives (Z, Y, X) — TorchIO wants (C, X, Y, Z)
        volume = volume.permute(0, 3, 2, 1).contiguous()
        volume = torch.nan_to_num(volume, nan=0.0, posinf=0.0, neginf=0.0)

        subject = tio.Subject(mri=tio.ScalarImage(tensor=volume))
        if self.transform:
            subject = self.transform(subject)

        return subject.mri.data, label, str(img_path)


train_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad(CROP_SIZE),
    tio.RandomFlip(axes=(0, 1, 2)),
    tio.RandomAffine(scales=(0.95, 1.05), degrees=5),
    tio.RandomNoise(std=(0, 0.02)),
    tio.RandomBlur(std=(0, 0.5)),
])

test_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad(CROP_SIZE),
])

train_dataset = NiiDataset(DATA_DIR / "Train", transform=train_transform)
test_dataset  = NiiDataset(DATA_DIR / "Test",  transform=test_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

print(f"--- Loaded {len(train_dataset)} training and {len(test_dataset)} test samples ---")
print(f"--- Crop size: {CROP_SIZE} | Batch size: {BATCH_SIZE} ---")

############################################
# MODEL  (ResNet3D — matches inference service)
############################################
class BasicBlock3D(nn.Module):
    def __init__(self, in_c, out_c, stride=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(in_c, out_c, 3, stride=stride, padding=1, bias=False),
            nn.BatchNorm3d(out_c), nn.ReLU(inplace=True),
            nn.Conv3d(out_c, out_c, 3, stride=1, padding=1, bias=False),
            nn.BatchNorm3d(out_c),
        )
        self.shortcut = nn.Sequential()
        if stride != 1 or in_c != out_c:
            self.shortcut = nn.Sequential(
                nn.Conv3d(in_c, out_c, 1, stride=stride, bias=False),
                nn.BatchNorm3d(out_c),
            )

    def forward(self, x):
        return F.relu(self.conv(x) + self.shortcut(x))


class ResNet3D(nn.Module):
    def __init__(self):
        super().__init__()
        self.prep = nn.Sequential(
            nn.Conv3d(1, 32, 7, stride=2, padding=3, bias=False),
            nn.BatchNorm3d(32), nn.ReLU(inplace=True),
            nn.MaxPool3d(3, stride=2, padding=1),
        )
        self.layer1 = BasicBlock3D(32,  64)
        self.layer2 = BasicBlock3D(64,  128, stride=2)
        self.layer3 = BasicBlock3D(128, 256, stride=2)

        self.avgpool    = nn.AdaptiveAvgPool3d(1)
        self.classifier = nn.Linear(256, 2)

    def forward(self, x):
        x = self.prep(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = x.flatten(1)
        return self.classifier(x)

############################################
# GRAD-CAM HEATMAP
############################################
def get_heatmap(model, img_tensor, target_label, device):
    """Grad-CAM on layer3 — returns a 3-D numpy heatmap (CROP_SIZE)."""
    model.eval()
    activations, gradients = [], []

    h1 = model.layer3.register_forward_hook(
        lambda m, i, o: activations.append(o))
    h2 = model.layer3.register_full_backward_hook(
        lambda m, gi, go: gradients.append(go[0]))

    img_tensor = img_tensor.to(device)
    output = model(img_tensor)
    model.zero_grad()
    output[0, target_label].backward()

    weights = torch.mean(gradients[0], dim=(2, 3, 4), keepdim=True)
    cam = F.relu((weights * activations[0]).sum(dim=1).squeeze())

    cam_resized = F.interpolate(
        cam.detach().cpu().unsqueeze(0).unsqueeze(0),
        size=CROP_SIZE,
        mode="trilinear",
        align_corners=False,
    ).squeeze().numpy()

    h1.remove()
    h2.remove()
    return cam_resized


def save_heatmap_figure(img_tensor, heatmap, label, pred, save_path):
    """Overlay Grad-CAM on the middle axial slice and save to PNG."""
    # img_tensor: (1, X, Y, Z) — take middle Z slice
    vol = img_tensor.squeeze().cpu().numpy()       # (X, Y, Z)
    mid_z = vol.shape[2] // 2
    slice_img = vol[:, :, mid_z]
    slice_hm  = heatmap[:, :, mid_z]

    class_names = ["Benign", "Malignancy"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))

    axes[0].imshow(slice_img, cmap="bone")
    axes[0].set_title(f"CT slice (z={mid_z})")
    axes[0].axis("off")

    axes[1].imshow(slice_img, cmap="bone")
    axes[1].imshow(slice_hm,  cmap="jet", alpha=0.45)
    axes[1].set_title(f"Grad-CAM | Label: {class_names[label]} | Pred: {class_names[pred]}")
    axes[1].axis("off")

    plt.tight_layout()
    plt.savefig(save_path, dpi=120)
    plt.close(fig)

############################################
# TRAINING SETUP
############################################
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = ResNet3D().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode="max", patience=3, factor=0.5
)

use_cuda = (device.type == "cuda")
scaler   = torch.amp.GradScaler("cuda", enabled=use_cuda)

history = {"train_loss": [], "train_acc": [],
           "test_loss":  [], "test_acc":  []}

best_accuracy = 0.0
print(f"--- Training on: {device} ---")

############################################
# TRAINING LOOP
############################################
for epoch in range(NUM_EPOCHS):
    model.train()
    run_loss, correct, total = 0.0, 0, 0
    start = time.time()

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS}", leave=False)
    for images, labels, _ in pbar:
        images = images.to(device, non_blocking=PIN_MEMORY)
        labels = labels.to(device, non_blocking=PIN_MEMORY)

        optimizer.zero_grad(set_to_none=True)

        with torch.amp.autocast("cuda", enabled=use_cuda):
            outputs = model(images)
            loss    = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        preds    = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total   += labels.size(0)
        run_loss += loss.item()
        pbar.set_postfix(loss=f"{loss.item():.4f}")

    train_acc  = 100.0 * correct / total if total > 0 else 0.0
    train_loss = run_loss / len(train_loader)

    # --- EVALUATION ---
    model.eval()
    v_loss, v_correct, v_total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels, _ in test_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            labels = labels.to(device, non_blocking=PIN_MEMORY)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = model(images)
            loss = criterion(outputs, labels)
            v_loss    += loss.item()
            v_correct += (outputs.argmax(1) == labels).sum().item()
            v_total   += labels.size(0)

    val_acc  = 100.0 * v_correct / v_total if v_total > 0 else 0.0
    val_loss = v_loss / len(test_loader)

    history["train_loss"].append(train_loss)
    history["train_acc"].append(train_acc)
    history["test_loss"].append(val_loss)
    history["test_acc"].append(val_acc)

    elapsed = time.time() - start
    print(f"Epoch {epoch+1:>3}/{NUM_EPOCHS} | "
          f"Train Loss: {train_loss:.4f}  Acc: {train_acc:.1f}% | "
          f"Test  Loss: {val_loss:.4f}  Acc: {val_acc:.1f}% | "
          f"Time: {elapsed:.1f}s")

    scheduler.step(val_acc)

    # --- SAVE BEST ---
    if val_acc > best_accuracy:
        best_accuracy = val_acc
        best_path = MODEL_DIR / f"resnet3d_best_epoch{epoch+1}_acc{val_acc:.2f}.pth"
        torch.save({
            "epoch":                epoch + 1,
            "accuracy":             val_acc,
            "model_state_dict":     model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        }, best_path)
        print(f"  >> NEW BEST SAVED: {best_path.name}")

    # --- SAVE LATEST ---
    torch.save({
        "epoch":                epoch + 1,
        "model_state_dict":     model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
    }, LATEST_MODEL_PATH)

print(f"\n--- Training complete. Best test accuracy: {best_accuracy:.2f}% ---")

############################################
# TRAINING CURVES
############################################
fig, axes = plt.subplots(1, 2, figsize=(12, 4))

axes[0].plot(history["train_loss"], label="Train")
axes[0].plot(history["test_loss"],  label="Test")
axes[0].set_title("Loss"); axes[0].set_xlabel("Epoch"); axes[0].legend()

axes[1].plot(history["train_acc"], label="Train")
axes[1].plot(history["test_acc"],  label="Test")
axes[1].set_title("Accuracy (%)"); axes[1].set_xlabel("Epoch"); axes[1].legend()

plt.tight_layout()
curves_path = MODEL_DIR / "training_curves.png"
plt.savefig(curves_path, dpi=120)
plt.close(fig)
print(f"Training curves saved → {curves_path}")

############################################
# GRAD-CAM ON TEST SAMPLES
############################################
print("--- Generating Grad-CAM heatmaps on test samples ---")
model.eval()

num_heatmaps = 4   # save heatmaps for the first N test samples
generated    = 0

for images, labels, paths in test_loader:
    for i in range(images.size(0)):
        if generated >= num_heatmaps:
            break

        img_t  = images[i:i+1]
        label  = labels[i].item()

        with torch.no_grad():
            with torch.amp.autocast("cuda", enabled=use_cuda):
                pred = model(img_t.to(device)).argmax(1).item()

        heatmap   = get_heatmap(model, img_t, target_label=pred, device=device)
        save_path = MODEL_DIR / f"heatmap_sample{generated+1}_label{label}_pred{pred}.png"
        save_heatmap_figure(img_t, heatmap, label, pred, save_path)
        print(f"  Heatmap saved → {save_path.name}")
        generated += 1

    if generated >= num_heatmaps:
        break

print("--- Done ---")
