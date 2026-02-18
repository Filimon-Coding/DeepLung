import os
import pandas as pd
import shutil
import time
import random
from pathlib import Path

import torch
import torch.nn as nn
import torch.optim as optim
import torchio as tio
import SimpleITK as sitk
from torch.utils.data import Dataset, DataLoader

############################################
# PATHS AND CONFIGURATION
############################################
random.seed(42)
torch.manual_seed(42)

CSV_PATH = "list3.2.csv"
INPUT_DIR = Path("test_images")
DATA_DIR = Path("Data")
MODEL_DIR = Path("checkpoints")
MODEL_DIR.mkdir(exist_ok=True)

LATEST_MODEL_PATH = MODEL_DIR / "resnet3d_latest.pth"

############################################
# TRAINING SETTINGS (edit here)
############################################
CROP_SIZE = (128, 128, 128)   # <<<<<< changed to 128
BATCH_SIZE = 3
NUM_EPOCHS = 50
PRINT_EVERY = 5              # prints every N batches
NUM_WORKERS = 0              # CI-safe; change to 2/4 if running locally
PIN_MEMORY = False           # set True if you want, helps with non_blocking=True

############################################
# (Optional) DATA CREATION FUNCTION
# NOTE: If Data/ already exists, this never runs.
# Requires: all_files and cancer_cases (defined somewhere else).
############################################
def create_short_dataset(file_list, target_count=100):
    counts = {"Malignancy": 0, "Benign": 0}
    print(f"--- Starting Data Sorting: Target is {target_count} of each class ---")

    for fname in file_list:
        if counts["Malignancy"] >= target_count and counts["Benign"] >= target_count:
            print(f"--- Goal reached: {counts['Malignancy']} Malignant and {counts['Benign']} Benign images collected ---")
            break

        try:
            case_id = int(fname.split('-')[-1].split('_')[0])
        except:
            continue

        label_folder = "Malignancy" if case_id in cancer_cases else "Benign"

        if counts[label_folder] < target_count:
            subset = "Train" if (counts["Malignancy"] + counts["Benign"]) % 5 != 0 else "Test"
            dest_path = DATA_DIR / subset / label_folder
            dest_path.mkdir(parents=True, exist_ok=True)

            if not (dest_path / fname).exists():
                shutil.copy(INPUT_DIR / fname, dest_path / fname)

            counts[label_folder] += 1

            if (counts["Malignancy"] + counts["Benign"]) % 20 == 0:
                print(f"[DATA SETUP] Current Count -> Malignant: {counts['Malignancy']} | Benign: {counts['Benign']}")

# Check if data already exists, if not, create it
if not DATA_DIR.exists():
    create_short_dataset(all_files, target_count=100)
else:
    print(f"--- Folder '{DATA_DIR}' already exists. Skipping sorting. ---")

############################################
# DATASET & LOADERS
############################################
class NiiDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.samples = []
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

        # SimpleITK -> numpy (typically Z, Y, X)
        image_np = sitk.GetArrayFromImage(sitk.ReadImage(str(img_path)))

        # numpy -> torch + channel dim: (1, Z, Y, X)
        volume = torch.from_numpy(image_np).float().unsqueeze(0)

        # TorchIO wants (C, X, Y, Z): (1, X, Y, Z)
        volume = volume.permute(0, 3, 2, 1).contiguous()

        volume = torch.nan_to_num(volume, nan=0.0, posinf=0.0, neginf=0.0)

        subject = tio.Subject(mri=tio.ScalarImage(tensor=volume))
        if self.transform:
            subject = self.transform(subject)

        return subject.mri.data, label, str(img_path)


# TRAINING: augmentation
train_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad(CROP_SIZE),
    tio.RandomFlip(axes=(0, 1, 2)),
    tio.RandomAffine(scales=(0.95, 1.05), degrees=5),
    tio.RandomNoise(std=(0, 0.02)),
    tio.RandomBlur(std=(0, 0.5)),
])

# TEST: preprocessing only
test_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad(CROP_SIZE),
])

train_dataset = NiiDataset(DATA_DIR / "Train", transform=train_transform)
test_dataset  = NiiDataset(DATA_DIR / "Test",  transform=test_transform)

train_loader = DataLoader(
    train_dataset,
    batch_size=BATCH_SIZE,
    shuffle=True,
    num_workers=NUM_WORKERS,
    pin_memory=PIN_MEMORY,
)
test_loader = DataLoader(
    test_dataset,
    batch_size=BATCH_SIZE,
    shuffle=False,
    num_workers=NUM_WORKERS,
    pin_memory=PIN_MEMORY,
)

print(f"--- Loaded {len(train_dataset)} training and {len(test_dataset)} testing samples ---")

############################################
# MODEL ARCHITECTURE
############################################
class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, mid_channels=None, stride=1):
        super().__init__()
        if mid_channels is None:
            mid_channels = out_channels // 2

        self.conv = nn.Sequential(
            nn.Conv3d(in_channels, mid_channels, kernel_size=1, stride=1),
            nn.BatchNorm3d(mid_channels),
            nn.ReLU(),
            nn.Conv3d(mid_channels, mid_channels, kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm3d(mid_channels),
            nn.ReLU(),
            nn.Conv3d(mid_channels, out_channels, kernel_size=1, stride=1),
            nn.BatchNorm3d(out_channels)
        )

        self.shortcut = nn.Sequential()
        if stride != 1 or in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv3d(in_channels, out_channels, kernel_size=1, stride=stride),
                nn.BatchNorm3d(out_channels)
            )

    def forward(self, x):
        return torch.relu(self.conv(x) + self.shortcut(x))


class ResNetShort(nn.Module):
    def __init__(self):
        super().__init__()
        self.prep = nn.Sequential(
            nn.Conv3d(1, 32, 3, padding=1),
            nn.BatchNorm3d(32),
            nn.ReLU()
        )

        self.layer1 = ResidualBlock(32, 64, stride=2)
        self.layer2 = ResidualBlock(64, 128, stride=2)
        self.layer3 = ResidualBlock(128, 256, stride=2)

        self.avgpool = nn.AdaptiveAvgPool3d(1)
        self.dropout = nn.Dropout3d(p=0.3)
        self.classifier = nn.Linear(256, 2)

    def forward(self, x):
        x = self.prep(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = self.dropout(x)
        x = x.flatten(1)
        return self.classifier(x)

############################################
# TRAINING SETUP
############################################
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ResNetShort().to(device)

criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer, mode='max', patience=3, factor=0.5
)

# AMP (new API)
use_cuda = (device.type == "cuda")
scaler = torch.amp.GradScaler('cuda', enabled=use_cuda)

best_accuracy = 0.0
print(f"--- Training running on: {device} ---")
print("DEBUG: About to start training loop...")

for epoch in range(NUM_EPOCHS):
    model.train()
    total_loss, correct, total = 0.0, 0, 0
    start_time = time.time()

    print(f"\n--- Starting Epoch {epoch+1}/{NUM_EPOCHS} ---")
    print("DEBUG: Entering train_loader loop...")

    for i, (images, labels, paths) in enumerate(train_loader):
        if i == 0:
            print("DEBUG: Got first batch from DataLoader")

        batch_start = time.time()

        images = images.to(device, non_blocking=PIN_MEMORY)
        labels = labels.to(device, non_blocking=PIN_MEMORY)

        optimizer.zero_grad(set_to_none=True)

        with torch.amp.autocast('cuda', enabled=use_cuda):
            outputs = model(images)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)
        total_loss += loss.item()

        batch_duration = time.time() - batch_start

        if i == 0 or (i + 1) % PRINT_EVERY == 0 or (i + 1) == len(train_loader):
            print(f"Batch [{i+1}/{len(train_loader)}] | Loss: {loss.item():.4f} | Time/Batch: {batch_duration:.2f}s")

    train_accuracy = 100.0 * correct / total if total > 0 else 0.0
    epoch_duration = time.time() - start_time

    # --- EVALUATION ---
    model.eval()
    val_correct, val_total = 0, 0
    with torch.no_grad():
        for images, labels, paths in test_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            labels = labels.to(device, non_blocking=PIN_MEMORY)

            with torch.amp.autocast('cuda', enabled=use_cuda):
                outputs = model(images)

            preds = outputs.argmax(dim=1)
            val_correct += (preds == labels).sum().item()
            val_total += labels.size(0)

    val_accuracy = 100.0 * val_correct / val_total if val_total > 0 else 0.0
    print(f"--- Epoch {epoch+1} Summary | Train Acc: {train_accuracy:.2f}% | Test Acc: {val_accuracy:.2f}% | Time: {epoch_duration:.2f}s ---")

    scheduler.step(val_accuracy)

    # --- SAVE BEST ---
    if val_accuracy > best_accuracy:
        best_accuracy = val_accuracy
        current_best_filename = f"resnet3d_best_epoch{epoch+1}_acc{val_accuracy:.2f}.pth"
        current_best_path = MODEL_DIR / current_best_filename

        torch.save({
            'epoch': epoch + 1,
            'accuracy': val_accuracy,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, current_best_path)
        print(f"NEW BEST MODEL SAVED: {current_best_filename}")

    # --- SAVE LATEST ---
    torch.save({
        'epoch': epoch + 1,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
    }, LATEST_MODEL_PATH)

print(f"\n--- Training Complete. Best Test Accuracy: {best_accuracy:.2f}% ---")
