import os
import pandas as pd
import shutil
import time
from pathlib import Path
from sklearn.model_selection import train_test_split

import torch
import torch.nn as nn
import torch.optim as optim
import torchio as tio
import SimpleITK as sitk
from torch.utils.data import Dataset, DataLoader

############################################
# SPLIT DATA INTO TRAIN / TEST (SHORT VERSION)
############################################

CSV_PATH = "list3.2.csv"
INPUT_DIR = Path("test_images")
DATA_DIR = Path("Data") # Using the short version folder

labels_df = pd.read_csv(CSV_PATH)
cancer_cases = set(labels_df['case'].values)
all_files = [f for f in os.listdir(INPUT_DIR) if f.endswith(".nii.gz")]


# sorts files into 70/30 split wher 30 are test and 70 are for training
'''

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
'''
############################################
# DATASET & LOADERS
############################################

class NiiDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.samples = []
        self.transform = transform
        for label, folder in enumerate(["Benign", "Malignancy"]):
            folder_path = Path(root_dir) / folder
            for img_path in folder_path.glob("*.nii.gz"):
                self.samples.append((img_path, label))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image = sitk.ReadImage(str(img_path))
        image = sitk.GetArrayFromImage(image)
        image = torch.from_numpy(image).float().unsqueeze(0)
        subject = tio.Subject(mri=tio.ScalarImage(tensor=image))
        if self.transform:
            subject = self.transform(subject)
        return subject.mri.data, label

transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad((128, 128, 128))
])

train_dataset = NiiDataset(DATA_DIR/"Train", transform=transform)
test_dataset  = NiiDataset(DATA_DIR/"Test", transform=transform)

# Set num_workers > 0 on server to speed up NIfTI loading
train_loader = DataLoader(train_dataset, batch_size=2, shuffle=True)
test_loader  = DataLoader(test_dataset, batch_size=2, shuffle=False)

print(f"--- Loaded {len(train_dataset)} training samples and {len(test_dataset)} testing samples ---")

############################################
# MODEL & TRAINING
############################################

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

if device.type == "cuda":
    gpu_name = torch.cuda.get_device_name(0)
    print(f"--- Training will run on GPU: {gpu_name} ---")
else:
    print("--- Training will run on: CPU (Warning: This will be very slow!) ---")

class ResidualBlock(nn.Module):
    def __init__(self, in_channels, out_channels, stride=1):
        super().__init__()
        self.conv = nn.Sequential(
            nn.Conv3d(in_channels, out_channels, kernel_size=3, stride=stride, padding=1),
            nn.BatchNorm3d(out_channels),
            nn.ReLU(),
            nn.Conv3d(out_channels, out_channels, kernel_size=3, padding=1),
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
        self.prep = nn.Sequential(nn.Conv3d(1, 16, 3, padding=1), nn.BatchNorm3d(16), nn.ReLU())
        self.layer1 = ResidualBlock(16, 32, stride=2)
        self.layer2 = ResidualBlock(32, 64, stride=2)
        self.layer3 = ResidualBlock(64, 128, stride=2)
        self.avgpool = nn.AdaptiveAvgPool3d(1)
        self.classifier = nn.Linear(128, 2)

    def forward(self, x):
        x = self.layer3(self.layer2(self.layer1(self.prep(x))))
        x = self.avgpool(x).flatten(1)
        return self.classifier(x)

model = ResNetShort().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-4)

num_epochs = 10

for epoch in range(num_epochs):
    model.train()
    total_loss = 0
    start_time = time.time()
    
    print(f"\n--- Starting Epoch {epoch+1}/{num_epochs} ---")
    
    for i, (images, labels) in enumerate(train_loader):
        batch_start = time.time()
        
        images, labels = images.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
        batch_duration = time.time() - batch_start
        
        # Log every 10 batches to keep the terminal clean
        if (i + 1) % 10 == 0 or (i + 1) == len(train_loader):
            print(f"Epoch [{epoch+1}/{num_epochs}] | Batch [{i+1}/{len(train_loader)}] | Loss: {loss.item():.4f} | Time/Batch: {batch_duration:.2f}s")

    avg_loss = total_loss / len(train_loader)
    epoch_duration = time.time() - start_time
    print(f"--- Epoch {epoch+1} Completed | Avg Loss: {avg_loss:.4f} | Total Time: {epoch_duration:.2f}s ---")

############################################
# EVALUATION
############################################

print("\n--- Starting Evaluation on Test Set ---")
model.eval()
correct = 0
total = 0

with torch.no_grad():
    for images, labels in test_loader:
        images, labels = images.to(device), labels.to(device)
        outputs = model(images)
        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()
        total += labels.size(0)

accuracy = 100 * correct / total
print(f"--- Final Test Accuracy: {accuracy:.2f}% ---")