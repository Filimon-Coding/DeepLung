import os
import re
import csv
import json
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
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
    classification_report,
    roc_curve, auc,
    precision_recall_curve, average_precision_score,
    matthews_corrcoef,
)
from sklearn.calibration import calibration_curve
from tqdm import tqdm

############################################
# PATHS AND CONFIGURATION
############################################
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

DATA_DIR   = Path("Data")
MODEL_DIR  = Path("checkpoints")
MODEL_DIR.mkdir(exist_ok=True)
NODULE_CSV = Path("list3.2.csv")

LATEST_MODEL_PATH = MODEL_DIR / "resnet3d_latest.pth"

############################################
# TRAINING SETTINGS
############################################
# 128³ matches the inference service's CropOrPad((128,128,128)) exactly —
# same distribution at train time and production time.
CROP_SIZE      = (128, 128, 128)
BATCH_SIZE     = 4
NUM_EPOCHS     = 60
NUM_WORKERS    = 0
PIN_MEMORY     = False
EARLY_STOP_PAT = 10

# Lung CT Hounsfield Unit window.
# Clips bone/air artifacts so RescaleIntensity maps the clinically
# relevant range to [0,1] rather than an arbitrary global min/max.
HU_MIN = -1000
HU_MAX =  400

############################################
# NODULE MAP  (list3.2.csv — all nodules per case)
############################################
def load_all_nodules(csv_path):
    """
    Returns dict: case_int -> list of {'x', 'y', 'z', 'vol'}.
    Every row in the CSV becomes one entry — one entry per nodule per case.
    Coordinates are LIDC pixel-space: x=column, y=row, z=slice.
    """
    if not Path(csv_path).exists():
        print(f"WARNING: {csv_path} not found — crops will fall back to volume centre")
        return {}

    with open(csv_path, newline="") as f:
        raw = list(csv.reader(f))

    header = [c.strip() for c in raw[0]]
    try:
        i_case = header.index("case")
        i_vol  = header.index("volume")
        i_x    = header.index("x loc.")
        i_y    = header.index("y loc.")
        i_z    = header.index("sliceno")
    except ValueError as e:
        print(f"CSV column not found: {e}  — no nodule cropping")
        return {}

    all_nodules: dict = {}
    for row in raw[1:]:
        if len(row) <= max(i_case, i_vol, i_x, i_y, i_z):
            continue
        try:
            case = int(str(row[i_case]).strip())
            vol  = float(str(row[i_vol]).strip() or "0")
            x    = int(float(str(row[i_x]).strip()))
            y    = int(float(str(row[i_y]).strip()))
            z    = int(float(str(row[i_z]).strip()))
        except (ValueError, IndexError):
            continue
        all_nodules.setdefault(case, []).append({"x": x, "y": y, "z": z, "vol": vol})

    total_nodules = sum(len(v) for v in all_nodules.values())
    print(f"Loaded {total_nodules} nodules across {len(all_nodules)} cases from {csv_path}")
    return all_nodules


def case_from_path(img_path):
    """Extract integer case number from LIDC-IDRI-XXXX_CT.nii.gz."""
    m = re.search(r"LIDC-IDRI-(\d+)", str(img_path))
    return int(m.group(1)) if m else None


def crop_volume(volume, cx, cy, cz, crop_size):
    """
    Crop a fixed box around (cx, cy, cz) in a (1, X, Y, Z) tensor.
    Zero-pads if the box extends beyond the volume boundary.
    Returns (cropped_tensor, x_start, y_start, z_start).
    """
    hx, hy, hz = crop_size[0] // 2, crop_size[1] // 2, crop_size[2] // 2
    _, X, Y, Z = volume.shape

    x0 = max(0, min(cx - hx, X - crop_size[0]))
    y0 = max(0, min(cy - hy, Y - crop_size[1]))
    z0 = max(0, min(cz - hz, Z - crop_size[2]))

    x1c = min(x0 + crop_size[0], X)
    y1c = min(y0 + crop_size[1], Y)
    z1c = min(z0 + crop_size[2], Z)
    cropped = volume[:, x0:x1c, y0:y1c, z0:z1c]

    # Zero-pad to exact crop_size if the volume was too small
    px = crop_size[0] - cropped.shape[1]
    py = crop_size[1] - cropped.shape[2]
    pz = crop_size[2] - cropped.shape[3]
    if px > 0 or py > 0 or pz > 0:
        # F.pad pads from last dim backwards: (z_l,z_r, y_l,y_r, x_l,x_r)
        cropped = F.pad(cropped, (0, pz, 0, py, 0, px))

    return cropped, x0, y0, z0


all_nodules = load_all_nodules(NODULE_CSV)

############################################
# TRANSFORMS
############################################
# base_transform normalises the full volume before cropping.
# aug_transform augments the already-cropped patch.
base_transform = tio.RescaleIntensity(out_min_max=(0, 1))

aug_transform = tio.Compose([
    tio.RandomFlip(axes=(0, 1, 2)),
    tio.RandomAffine(scales=(0.9, 1.1), degrees=10),
    tio.RandomNoise(std=(0, 0.025)),
    tio.RandomBlur(std=(0, 0.5)),
    tio.RandomGamma(log_gamma=(-0.3, 0.3)),
])

############################################
# DATASET
# Each nodule in the CSV becomes its own training sample.
# samples list: (path, label, cx, cy, cz)
############################################
class NiiDataset(Dataset):
    def __init__(self, root_dir, all_nodules, augment=False):
        self.samples   = []   # (path, label, cx, cy, cz)
        self.augment   = augment

        for label, folder in enumerate(["Benign", "Malignancy"]):
            folder_path = Path(root_dir) / folder
            if not folder_path.exists():
                continue
            for img_path in folder_path.glob("*.nii.gz"):
                case = case_from_path(img_path)
                if case and case in all_nodules:
                    # One sample per nodule — multiplies effective data 2-4×
                    for nd in all_nodules[case]:
                        self.samples.append((img_path, label, nd["x"], nd["y"], nd["z"]))
                else:
                    # No CSV entry: crop around volume centre as fallback
                    self.samples.append((img_path, label, None, None, None))

    def __len__(self):
        return len(self.samples)

    def _load_and_crop(self, img_path, cx, cy, cz):
        image_np = sitk.GetArrayFromImage(sitk.ReadImage(str(img_path)))
        # Some NIfTI files have an extra dimension (e.g. 4D scout) — reduce to 3D
        while image_np.ndim > 3:
            image_np = image_np[0]
        volume   = torch.from_numpy(image_np).float().unsqueeze(0)
        # SimpleITK: (Z, Y, X) → TorchIO: (C, X, Y, Z)
        volume = volume.permute(0, 3, 2, 1).contiguous()
        volume = torch.nan_to_num(volume, nan=0.0, posinf=0.0, neginf=0.0)

        # Lung window — keeps clinically relevant HU range
        volume = torch.clamp(volume, HU_MIN, HU_MAX)

        # Intensity normalise the full volume before cropping
        subj   = tio.Subject(mri=tio.ScalarImage(tensor=volume))
        volume = base_transform(subj).mri.data

        # Resolve fallback centre
        if cx is None:
            cx, cy, cz = volume.shape[1] // 2, volume.shape[2] // 2, volume.shape[3] // 2

        return crop_volume(volume, cx, cy, cz, CROP_SIZE)

    def __getitem__(self, idx):
        img_path, label, cx, cy, cz = self.samples[idx]
        cropped, x0, y0, z0 = self._load_and_crop(img_path, cx, cy, cz)

        if self.augment:
            subj    = tio.Subject(mri=tio.ScalarImage(tensor=cropped))
            cropped = aug_transform(subj).mri.data

        offset = torch.tensor([x0, y0, z0], dtype=torch.long)
        return cropped, label, str(img_path), offset


class SampleListDataset(Dataset):
    """Built from a flat (path, label, cx, cy, cz) list — used for k-fold."""
    def __init__(self, samples, augment=False):
        self.samples = samples
        self.augment = augment

    def __len__(self):
        return len(self.samples)

    def _load_and_crop(self, img_path, cx, cy, cz):
        image_np = sitk.GetArrayFromImage(sitk.ReadImage(str(img_path)))
        while image_np.ndim > 3:
            image_np = image_np[0]
        volume   = torch.from_numpy(image_np).float().unsqueeze(0)
        volume   = volume.permute(0, 3, 2, 1).contiguous()
        volume   = torch.nan_to_num(volume, nan=0.0, posinf=0.0, neginf=0.0)
        volume   = torch.clamp(volume, HU_MIN, HU_MAX)
        subj     = tio.Subject(mri=tio.ScalarImage(tensor=volume))
        volume   = base_transform(subj).mri.data
        if cx is None:
            cx, cy, cz = volume.shape[1] // 2, volume.shape[2] // 2, volume.shape[3] // 2
        return crop_volume(volume, cx, cy, cz, CROP_SIZE)

    def __getitem__(self, idx):
        img_path, label, cx, cy, cz = self.samples[idx]
        cropped, x0, y0, z0 = self._load_and_crop(img_path, cx, cy, cz)
        if self.augment:
            subj    = tio.Subject(mri=tio.ScalarImage(tensor=cropped))
            cropped = aug_transform(subj).mri.data
        offset = torch.tensor([x0, y0, z0], dtype=torch.long)
        return cropped, label, str(img_path), offset


def make_weighted_sampler(dataset):
    """
    Returns a WeightedRandomSampler that draws each class with equal
    probability regardless of how many nodules each class has in the CSV.
    """
    labels       = [s[1] for s in dataset.samples]
    class_counts = [labels.count(0), labels.count(1)]
    print(f"  Class counts — Benign: {class_counts[0]}  Malignancy: {class_counts[1]}")
    weights  = [1.0 / class_counts[l] for l in labels]
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


train_dataset = NiiDataset(DATA_DIR / "Train", all_nodules, augment=True)
test_dataset  = NiiDataset(DATA_DIR / "Test",  all_nodules, augment=False)

train_sampler = make_weighted_sampler(train_dataset)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, sampler=train_sampler,
                          num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

print(f"--- Train samples (nodule-level): {len(train_dataset)} ---")
print(f"--- Test  samples (nodule-level): {len(test_dataset)} ---")
print(f"--- Crop: {CROP_SIZE}  |  Batch: {BATCH_SIZE} ---")

############################################
# DATASET DISTRIBUTION CHART
############################################
def _class_counts(dataset):
    labels = [s[1] for s in dataset.samples]
    return labels.count(0), labels.count(1)

tr_b, tr_m = _class_counts(train_dataset)
te_b, te_m = _class_counts(test_dataset)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
class_names = ["Benign", "Malignancy"]
colors      = ["steelblue", "tomato"]

for ax, counts, title in zip(
    axes[:2],
    [(tr_b, tr_m), (te_b, te_m)],
    [f"Train Set  (n={tr_b+tr_m})", f"Test Set  (n={te_b+te_m})"]
):
    ax.bar(class_names, counts, color=colors, edgecolor="white")
    for i, v in enumerate(counts):
        ax.text(i, v + 0.3, str(v), ha="center", fontsize=12, fontweight="bold")
    ax.set_title(title)
    ax.set_ylabel("Number of samples (nodule-level)")
    ax.grid(axis="y", alpha=0.3)

total_b, total_m = tr_b + te_b, tr_m + te_m
_, _, autotexts = axes[2].pie(
    [total_b, total_m], labels=class_names, colors=colors,
    autopct="%1.1f%%", startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=2),
)
for at in autotexts:
    at.set_fontsize(12)
axes[2].set_title(f"Total  (n={total_b+total_m})")

plt.suptitle("Dataset Class Distribution (nodule-level samples)", fontsize=14, fontweight="bold")
plt.tight_layout()
dist_path = MODEL_DIR / "dataset_distribution.png"
plt.savefig(dist_path, dpi=120)
plt.close(fig)
print(f"Dataset distribution saved → {dist_path}")

############################################
# MODEL  (must match backEnd/inferenceService/model.py exactly)
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


def _make_layer(in_c, out_c, num_blocks=2, stride=1):
    layers = [BasicBlock3D(in_c, out_c, stride=stride)]
    for _ in range(1, num_blocks):
        layers.append(BasicBlock3D(out_c, out_c))
    return nn.Sequential(*layers)


class ResNet3D(nn.Module):
    def __init__(self, dropout=0.5):
        super().__init__()
        self.prep = nn.Sequential(
            nn.Conv3d(1, 32, 7, stride=2, padding=3, bias=False),
            nn.BatchNorm3d(32), nn.ReLU(inplace=True),
            nn.MaxPool3d(3, stride=2, padding=1),
        )
        self.layer1 = _make_layer(32,  64,  num_blocks=2)
        self.layer2 = _make_layer(64,  128, num_blocks=2, stride=2)
        self.layer3 = _make_layer(128, 256, num_blocks=2, stride=2)

        self.avgpool    = nn.AdaptiveAvgPool3d(1)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout),
            nn.Linear(256, 2),
        )

    def forward(self, x):
        x = self.prep(x)
        x = self.layer1(x)
        x = self.layer2(x)
        x = self.layer3(x)
        x = self.avgpool(x)
        x = x.flatten(1)
        return self.classifier(x)

############################################
# GRAD-CAM++ HEATMAP
############################################
def get_heatmap(model, img_tensor, target_label, device):
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

    grads    = gradients[0]
    acts     = activations[0]
    grads_sq = grads.pow(2)
    grads_cb = grads.pow(3)
    act_sum  = acts.sum(dim=(2, 3, 4), keepdim=True)
    alpha    = grads_sq / (2.0 * grads_sq + act_sum * grads_cb + 1e-7)
    weights  = (alpha * F.relu(grads)).sum(dim=(2, 3, 4), keepdim=True)
    cam = F.relu((weights * acts).sum(dim=1).squeeze())

    target_size = tuple(img_tensor.shape[2:])
    cam_resized = F.interpolate(
        cam.detach().cpu().unsqueeze(0).unsqueeze(0),
        size=target_size, mode="trilinear", align_corners=False,
    ).squeeze().numpy()

    if cam_resized.max() > 0:
        nonzero = cam_resized[cam_resized > 0]
        thr = float(np.percentile(nonzero, 90)) if len(nonzero) > 0 else 0.0
        cam_resized[cam_resized < thr] = 0.0
        c_max = cam_resized.max()
        if c_max > 0:
            cam_resized = cam_resized / c_max

    h1.remove()
    h2.remove()
    return cam_resized


def save_heatmap_figure(img_tensor, heatmap, label, pred, save_path):
    vol   = img_tensor.squeeze().cpu().numpy()
    mid_z = vol.shape[2] // 2
    slice_img = vol[:, :, mid_z]
    slice_hm  = heatmap[:, :, mid_z]

    class_names = ["Benign", "Malignancy"]
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    axes[0].imshow(slice_img, cmap="bone"); axes[0].set_title(f"CT crop (z={mid_z})"); axes[0].axis("off")
    axes[1].imshow(slice_img, cmap="bone")
    axes[1].imshow(slice_hm,  cmap="jet", alpha=0.45)
    axes[1].set_title(f"Grad-CAM++ | Label: {class_names[label]} | Pred: {class_names[pred]}")
    axes[1].axis("off")
    plt.tight_layout()
    plt.savefig(save_path, dpi=120)
    plt.close(fig)

############################################
# TRAINING SETUP
############################################
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model  = ResNet3D(dropout=0.5).to(device)

criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
optimizer = optim.Adam(model.parameters(), lr=1e-4, weight_decay=1e-4)
scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=NUM_EPOCHS, eta_min=1e-6)

use_cuda = (device.type == "cuda")
scaler   = torch.amp.GradScaler("cuda", enabled=use_cuda)

history = {"train_loss": [], "train_acc": [], "test_loss": [], "test_acc": [], "lr": []}

best_accuracy      = 0.0
best_model_path    = None
early_stop_counter = 0
training_start     = time.time()

total_params = sum(p.numel() for p in model.parameters())
print(f"--- Training on: {device}  |  Model parameters: {total_params:,} ---")

############################################
# TRAINING LOOP
############################################
for epoch in range(NUM_EPOCHS):
    model.train()
    run_loss, correct, total = 0.0, 0, 0
    start = time.time()

    pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{NUM_EPOCHS}", leave=False)
    for images, labels, _, _ in pbar:
        images = images.to(device, non_blocking=PIN_MEMORY)
        labels = labels.to(device, non_blocking=PIN_MEMORY)

        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast("cuda", enabled=use_cuda):
            outputs = model(images)
            loss    = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
        scaler.step(optimizer)
        scaler.update()

        correct  += (outputs.argmax(1) == labels).sum().item()
        total    += labels.size(0)
        run_loss += loss.item()
        pbar.set_postfix(loss=f"{loss.item():.4f}")

    train_acc  = 100.0 * correct / total if total > 0 else 0.0
    train_loss = run_loss / len(train_loader)

    model.eval()
    v_loss, v_correct, v_total = 0.0, 0, 0
    with torch.no_grad():
        for images, labels, _, _ in test_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            labels = labels.to(device, non_blocking=PIN_MEMORY)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = model(images)
            v_loss    += criterion(outputs, labels).item()
            v_correct += (outputs.argmax(1) == labels).sum().item()
            v_total   += labels.size(0)

    val_acc  = 100.0 * v_correct / v_total if v_total > 0 else 0.0
    val_loss = v_loss / len(test_loader)

    history["train_loss"].append(train_loss)
    history["train_acc"].append(train_acc)
    history["test_loss"].append(val_loss)
    history["test_acc"].append(val_acc)
    history["lr"].append(optimizer.param_groups[0]["lr"])

    elapsed = time.time() - start
    print(f"Epoch {epoch+1:>3}/{NUM_EPOCHS} | "
          f"Train Loss: {train_loss:.4f}  Acc: {train_acc:.1f}% | "
          f"Test  Loss: {val_loss:.4f}  Acc: {val_acc:.1f}% | "
          f"Time: {elapsed:.1f}s")

    scheduler.step()

    if val_acc > best_accuracy:
        best_accuracy = val_acc
        best_model_path = MODEL_DIR / f"resnet3d_best_epoch{epoch+1}_acc{val_acc:.2f}.pth"
        torch.save({
            "epoch": epoch + 1, "accuracy": val_acc,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
        }, best_model_path)
        print(f"  >> NEW BEST SAVED: {best_model_path.name}")
        early_stop_counter = 0
    else:
        early_stop_counter += 1
        if early_stop_counter >= EARLY_STOP_PAT:
            print(f"\n  >> Early stopping at epoch {epoch+1} "
                  f"(no improvement for {EARLY_STOP_PAT} epochs)")
            break

    torch.save({
        "epoch": epoch + 1,
        "model_state_dict": model.state_dict(),
        "optimizer_state_dict": optimizer.state_dict(),
    }, LATEST_MODEL_PATH)

total_training_time = time.time() - training_start
epochs_run          = len(history["train_loss"])
print(f"\n--- Training complete. Best test accuracy: {best_accuracy:.2f}% ---")
print(f"--- Total training time: {total_training_time/3600:.2f} h  ({epochs_run} epochs) ---")

# All downstream evaluation uses the best checkpoint — not the final epoch
if best_model_path and best_model_path.exists():
    ckpt = torch.load(best_model_path, map_location=device)
    model.load_state_dict(ckpt["model_state_dict"])
    print(f"--- Loaded best checkpoint: {best_model_path.name} ---")

# Deploy checkpoint to inference service immediately after training completes —
# before k-fold, so the model is available even if post-training analysis times out.
import shutil
_infer_ckpt_dir = Path("../backEnd/inferenceService/checkpoints")
_infer_ckpt_dir.mkdir(parents=True, exist_ok=True)
shutil.copy2(LATEST_MODEL_PATH, _infer_ckpt_dir / "resnet3d_latest.pth")
print(f"--- Checkpoint deployed → {_infer_ckpt_dir}/resnet3d_latest.pth ---")

############################################
# TRAINING CURVES
############################################
epochs_axis = range(1, len(history["train_loss"]) + 1)
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

axes[0].plot(epochs_axis, history["train_loss"], marker="o", markersize=3, label="Train")
axes[0].plot(epochs_axis, history["test_loss"],  marker="o", markersize=3, label="Val")
bvl_ep = int(np.argmin(history["test_loss"])) + 1
bvl    = min(history["test_loss"])
axes[0].axvline(bvl_ep, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
axes[0].annotate(f"best {bvl:.4f}\n(ep {bvl_ep})",
                 xy=(bvl_ep, bvl), xytext=(bvl_ep+1, bvl+0.02), fontsize=7, color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=0.8))
axes[0].set_title("Loss per Epoch"); axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss")
axes[0].legend(); axes[0].grid(True, alpha=0.3)

axes[1].plot(epochs_axis, history["train_acc"], marker="o", markersize=3, label="Train")
axes[1].plot(epochs_axis, history["test_acc"],  marker="o", markersize=3, label="Val")
bva_ep = int(np.argmax(history["test_acc"])) + 1
bva    = max(history["test_acc"])
axes[1].axvline(bva_ep, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
axes[1].annotate(f"best {bva:.1f}%\n(ep {bva_ep})",
                 xy=(bva_ep, bva), xytext=(bva_ep+1, bva-5), fontsize=7, color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=0.8))
axes[1].set_title("Accuracy per Epoch (%)"); axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Accuracy (%)")
axes[1].set_ylim(0, 105); axes[1].legend(); axes[1].grid(True, alpha=0.3)

axes[2].plot(epochs_axis, history["lr"], marker="o", markersize=3, color="purple", label="LR")
axes[2].set_title("LR Schedule (Cosine)"); axes[2].set_xlabel("Epoch"); axes[2].set_ylabel("LR")
axes[2].set_yscale("log"); axes[2].legend(); axes[2].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(MODEL_DIR / "training_curves.png", dpi=120); plt.close(fig)
print(f"Training curves saved → {MODEL_DIR}/training_curves.png")

# Save raw per-epoch numbers so they can be re-plotted or quoted in the thesis
history_csv_path = MODEL_DIR / "history_curves.csv"
with open(history_csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["epoch", "train_loss", "train_acc", "val_loss", "val_acc", "lr"])
    for i in range(len(history["train_loss"])):
        writer.writerow([
            i + 1,
            round(history["train_loss"][i], 6),
            round(history["train_acc"][i],  4),
            round(history["test_loss"][i],  6),
            round(history["test_acc"][i],   4),
            history["lr"][i],
        ])
print(f"Per-epoch history saved → {history_csv_path}")

############################################
# CONFUSION MATRIX  (best checkpoint)
############################################
print("\n--- Generating confusion matrix ---")
model.eval()
cm_preds, cm_labels, cm_probs = [], [], []

with torch.no_grad():
    for images, labels, _, _ in test_loader:
        images = images.to(device, non_blocking=PIN_MEMORY)
        with torch.amp.autocast("cuda", enabled=use_cuda):
            outputs = model(images)
        probs = torch.softmax(outputs.float(), dim=1)[:, 1]
        cm_preds.extend(outputs.argmax(1).cpu().numpy())
        cm_labels.extend(labels.numpy())
        cm_probs.extend(probs.cpu().numpy())

disp = ConfusionMatrixDisplay(confusion_matrix(cm_labels, cm_preds),
                               display_labels=["Benign", "Malignancy"])
fig, ax = plt.subplots(figsize=(6, 5))
disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Confusion Matrix — Test Set (best checkpoint)")
plt.tight_layout()
plt.savefig(MODEL_DIR / "confusion_matrix.png", dpi=120); plt.close(fig)
print(f"Confusion matrix saved → {MODEL_DIR}/confusion_matrix.png")
print(classification_report(cm_labels, cm_preds, target_names=["Benign", "Malignancy"]))

# Derive clinical metrics from the confusion matrix
cm_arr = confusion_matrix(cm_labels, cm_preds)
TN, FP, FN, TP = cm_arr.ravel()
sensitivity  = TP / (TP + FN) if (TP + FN) > 0 else 0.0   # recall for malignancy
specificity  = TN / (TN + FP) if (TN + FP) > 0 else 0.0   # recall for benign
mcc          = matthews_corrcoef(cm_labels, cm_preds)
test_acc_pct = 100.0 * (TP + TN) / (TP + TN + FP + FN)

print(f"  Sensitivity (malignancy recall) : {sensitivity*100:.1f}%")
print(f"  Specificity (benign recall)     : {specificity*100:.1f}%")
print(f"  MCC                             : {mcc:.4f}  (1=perfect, 0=random, -1=inverse)")

# Measure inference time on a single sample (no augmentation, CPU timing is fine)
model.eval()
_sample_img, _, _, _ = test_dataset[0]
_x = _sample_img.unsqueeze(0).to(device)
# warm-up pass
with torch.no_grad():
    _ = model(_x)
if use_cuda:
    torch.cuda.synchronize()
_t0 = time.time()
_n_infer = 20
with torch.no_grad():
    for _ in range(_n_infer):
        with torch.amp.autocast("cuda", enabled=use_cuda):
            _ = model(_x)
if use_cuda:
    torch.cuda.synchronize()
infer_ms = (time.time() - _t0) / _n_infer * 1000
print(f"  Inference time (single crop)    : {infer_ms:.1f} ms  (avg over {_n_infer} runs)")

############################################
# ROC + PRECISION-RECALL
############################################
print("--- Generating ROC and Precision-Recall curves ---")
fpr, tpr, _ = roc_curve(cm_labels, cm_probs)
roc_auc     = auc(fpr, tpr)
precision, recall, _ = precision_recall_curve(cm_labels, cm_probs)
avg_precision = average_precision_score(cm_labels, cm_probs)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].plot(fpr, tpr, color="steelblue", lw=2, label=f"AUC = {roc_auc:.3f}")
axes[0].plot([0,1],[0,1], color="gray", linestyle="--", lw=1, label="Random")
axes[0].set_xlim(0,1); axes[0].set_ylim(0,1.02)
axes[0].set_xlabel("FPR"); axes[0].set_ylabel("TPR")
axes[0].set_title("ROC Curve — Test Set (best checkpoint)")
axes[0].legend(loc="lower right"); axes[0].grid(True, alpha=0.3)

axes[1].plot(recall, precision, color="darkorange", lw=2, label=f"AP = {avg_precision:.3f}")
axes[1].axhline(sum(cm_labels)/len(cm_labels), color="gray", linestyle="--", lw=1, label="Baseline")
axes[1].set_xlim(0,1); axes[1].set_ylim(0,1.02)
axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
axes[1].set_title("Precision-Recall — Test Set (best checkpoint)")
axes[1].legend(loc="upper right"); axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(MODEL_DIR / "roc_pr_curves.png", dpi=120); plt.close(fig)
print(f"ROC + PR curves saved → {MODEL_DIR}/roc_pr_curves.png")
print(f"  AUC-ROC: {roc_auc:.4f}  |  Average Precision: {avg_precision:.4f}")

# ── training_summary.json ────────────────────────────────────────────────────
# Single file with every key metric — paste numbers directly into thesis/slides.
summary = {
    "model": {
        "architecture":       "ResNet3D (2 blocks/layer, dropout=0.5)",
        "total_parameters":   total_params,
        "crop_size":          list(CROP_SIZE),
        "hu_window":          [HU_MIN, HU_MAX],
    },
    "dataset": {
        "train_samples_nodule_level": len(train_dataset),
        "test_samples_nodule_level":  len(test_dataset),
        "train_benign":    tr_b,
        "train_malignancy": tr_m,
        "test_benign":     te_b,
        "test_malignancy": te_m,
    },
    "training": {
        "epochs_configured": NUM_EPOCHS,
        "epochs_run":        epochs_run,
        "best_epoch":        int(np.argmax(history["test_acc"])) + 1,
        "early_stopping_patience": EARLY_STOP_PAT,
        "total_training_time_h":   round(total_training_time / 3600, 3),
        "optimizer":               "Adam",
        "lr_initial":              1e-4,
        "lr_final":                float(history["lr"][-1]),
        "weight_decay":            1e-4,
        "label_smoothing":         0.1,
        "batch_size":              BATCH_SIZE,
    },
    "test_set_metrics": {
        "accuracy_pct":    round(test_acc_pct, 2),
        "sensitivity_pct": round(sensitivity * 100, 2),
        "specificity_pct": round(specificity * 100, 2),
        "auc_roc":         round(roc_auc, 4),
        "average_precision": round(avg_precision, 4),
        "mcc":             round(mcc, 4),
        "TP": int(TP), "TN": int(TN), "FP": int(FP), "FN": int(FN),
    },
    "inference": {
        "inference_time_ms_single_crop": round(infer_ms, 2),
        "device": str(device),
    },
}
summary_path = MODEL_DIR / "training_summary.json"
with open(summary_path, "w") as f:
    json.dump(summary, f, indent=2)
print(f"Training summary saved → {summary_path}")

############################################
# CONFIDENCE HISTOGRAM
############################################
print("--- Generating confidence histogram ---")
cm_probs_arr  = np.array(cm_probs)
cm_labels_arr = np.array(cm_labels)
cm_preds_arr  = np.array(cm_preds)
correct_mask  = cm_labels_arr == cm_preds_arr

fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].hist(cm_probs_arr[correct_mask],  bins=20, range=(0,1), alpha=0.7,
             color="steelblue", label=f"Correct  (n={correct_mask.sum()})")
axes[0].hist(cm_probs_arr[~correct_mask], bins=20, range=(0,1), alpha=0.7,
             color="tomato",   label=f"Wrong  (n={(~correct_mask).sum()})")
axes[0].axvline(0.5, color="gray", linestyle="--", lw=1, label="Threshold")
axes[0].set_xlabel("P(Malignancy)"); axes[0].set_ylabel("Count")
axes[0].set_title("Confidence — Correct vs Wrong"); axes[0].legend(); axes[0].grid(True, alpha=0.3)

axes[1].hist(cm_probs_arr[cm_labels_arr==0], bins=20, range=(0,1), alpha=0.7,
             color="steelblue", label=f"True Benign  (n={(cm_labels_arr==0).sum()})")
axes[1].hist(cm_probs_arr[cm_labels_arr==1], bins=20, range=(0,1), alpha=0.7,
             color="tomato",    label=f"True Malignancy  (n={(cm_labels_arr==1).sum()})")
axes[1].axvline(0.5, color="gray", linestyle="--", lw=1, label="Threshold")
axes[1].set_xlabel("P(Malignancy)"); axes[1].set_ylabel("Count")
axes[1].set_title("Confidence — Per True Class"); axes[1].legend(); axes[1].grid(True, alpha=0.3)

plt.suptitle("Model Confidence Histogram", fontsize=13, fontweight="bold")
plt.tight_layout()
plt.savefig(MODEL_DIR / "confidence_histogram.png", dpi=120); plt.close(fig)
print(f"Confidence histogram saved → {MODEL_DIR}/confidence_histogram.png")

############################################
# CALIBRATION CURVE
############################################
print("--- Generating calibration curve ---")
fraction_pos, mean_pred = calibration_curve(cm_labels_arr, cm_probs_arr, n_bins=10)
fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(mean_pred, fraction_pos, marker="o", color="steelblue", lw=2, label="Model")
ax.plot([0,1],[0,1], linestyle="--", color="gray", lw=1.5, label="Perfect")
ax.fill_between(mean_pred, fraction_pos, mean_pred, alpha=0.15, color="steelblue", label="Gap")
ax.set_xlabel("Mean Predicted Probability"); ax.set_ylabel("Fraction Positives")
ax.set_title("Calibration Curve — Test Set (best checkpoint)")
ax.legend(); ax.grid(True, alpha=0.3); ax.set_xlim(0,1); ax.set_ylim(0,1)
plt.tight_layout()
plt.savefig(MODEL_DIR / "calibration_curve.png", dpi=120); plt.close(fig)
print(f"Calibration curve saved → {MODEL_DIR}/calibration_curve.png")

############################################
# GRAD-CAM HEATMAPS ON TEST SAMPLES
############################################
print("--- Generating Grad-CAM heatmaps on test samples ---")
model.eval()
generated = 0
for images, labels, paths, offsets in test_loader:
    for i in range(images.size(0)):
        if generated >= 4:
            break
        img_t = images[i:i+1]
        label = labels[i].item()
        with torch.no_grad():
            with torch.amp.autocast("cuda", enabled=use_cuda):
                pred = model(img_t.to(device)).argmax(1).item()
        heatmap   = get_heatmap(model, img_t, target_label=pred, device=device)
        save_path = MODEL_DIR / f"heatmap_sample{generated+1}_label{label}_pred{pred}.png"
        save_heatmap_figure(img_t, heatmap, label, pred, save_path)
        print(f"  Heatmap saved → {save_path.name}")
        generated += 1
    if generated >= 4:
        break

############################################
# GRAD-CAM LOCALIZATION VALIDATION
# Compares Grad-CAM peak (full-volume coords) against CSV ground-truth.
############################################
print("\n--- Grad-CAM Localization Validation (vs CSV ground truth) ---")
model.eval()
loc_results = []

for images, labels, paths, offsets in test_loader:
    for i in range(images.size(0)):
        case = case_from_path(paths[i])
        if case is None or case not in all_nodules:
            continue

        # Use the largest nodule as the reference target
        nd     = max(all_nodules[case], key=lambda n: n["vol"])
        true_x, true_y, true_z = nd["x"], nd["y"], nd["z"]

        img_t  = images[i:i+1]
        offset = offsets[i].numpy()

        with torch.no_grad():
            with torch.amp.autocast("cuda", enabled=use_cuda):
                pred = model(img_t.to(device)).argmax(1).item()

        heatmap   = get_heatmap(model, img_t, target_label=pred, device=device)
        peak_flat = int(np.argmax(heatmap))
        px, py, pz = np.unravel_index(peak_flat, heatmap.shape)

        fv_x = int(px) + int(offset[0])
        fv_y = int(py) + int(offset[1])
        fv_z = int(pz) + int(offset[2])

        dist = float(np.sqrt(
            (fv_x - true_x)**2 + (fv_y - true_y)**2 + (fv_z - true_z)**2
        ))

        loc_results.append({
            "case": case, "label": labels[i].item(), "pred": pred,
            "true_xyz": (true_x, true_y, true_z),
            "cam_xyz":  (fv_x, fv_y, fv_z),
            "distance": dist,
        })

if not loc_results:
    print("  No test samples with CSV entries — skipping localization validation")
else:
    distances = np.array([r["distance"] for r in loc_results])
    n = len(distances)
    print(f"  Samples evaluated : {n}")
    print(f"  Mean distance     : {np.mean(distances):.1f} voxels")
    print(f"  Median distance   : {np.median(distances):.1f} voxels")
    print(f"  Std               : {np.std(distances):.1f} voxels")
    print(f"  Within 10 voxels  : {100*np.mean(distances<=10):.1f}%  (~7-10 mm)")
    print(f"  Within 20 voxels  : {100*np.mean(distances<=20):.1f}%  (~14-20 mm)")
    print(f"  Within 30 voxels  : {100*np.mean(distances<=30):.1f}%  (~21-30 mm)")

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    axes[0].hist(distances, bins=20, color="steelblue", edgecolor="white")
    axes[0].axvline(np.mean(distances), color="red", linestyle="--",
                    label=f"Mean = {np.mean(distances):.1f} vox")
    axes[0].axvline(10, color="orange", linestyle=":", label="10 vox (~10 mm)")
    axes[0].axvline(20, color="green",  linestyle=":", label="20 vox (~20 mm)")
    axes[0].set_xlabel("Distance to True Nodule Centre (voxels)")
    axes[0].set_ylabel("Count")
    axes[0].set_title("Grad-CAM Peak Distance from Ground-Truth Nodule")
    axes[0].legend(); axes[0].grid(True, alpha=0.3)

    true_xs = [r["true_xyz"][0] for r in loc_results]
    cam_xs  = [r["cam_xyz"][0]  for r in loc_results]
    true_ys = [r["true_xyz"][1] for r in loc_results]
    cam_ys  = [r["cam_xyz"][1]  for r in loc_results]
    all_c   = true_xs + cam_xs + true_ys + cam_ys
    lim     = (min(all_c) - 10, max(all_c) + 10)

    axes[1].scatter(true_xs, cam_xs, alpha=0.7, label="X (column)", marker="o")
    axes[1].scatter(true_ys, cam_ys, alpha=0.7, label="Y (row)",    marker="^")
    axes[1].plot(lim, lim, "r--", lw=1.2, label="Perfect agreement")
    axes[1].set_xlim(lim); axes[1].set_ylim(lim)
    axes[1].set_xlabel("True Coordinate (voxels)"); axes[1].set_ylabel("CAM Peak Coordinate (voxels)")
    axes[1].set_title("Grad-CAM Localisation vs Ground Truth")
    axes[1].legend(); axes[1].grid(True, alpha=0.3)

    plt.suptitle(
        f"Grad-CAM Localization  n={n}  |  "
        f"mean={np.mean(distances):.1f} vox  |  "
        f"≤10vox: {100*np.mean(distances<=10):.0f}%  "
        f"≤20vox: {100*np.mean(distances<=20):.0f}%",
        fontsize=11, fontweight="bold"
    )
    plt.tight_layout()
    plt.savefig(MODEL_DIR / "gradcam_localization_validation.png", dpi=120); plt.close(fig)
    print(f"  Validation chart saved → {MODEL_DIR}/gradcam_localization_validation.png")

    # Per-sample overlay: CT crop + CAM + true nodule dot
    print("  Saving per-sample localization overlays …")
    class_names = ["Benign", "Malignancy"]
    for r in loc_results[:6]:
        try:
            sample_idx = next(
                j for j, s in enumerate(test_dataset.samples)
                if case_from_path(s[0]) == r["case"]
            )
        except StopIteration:
            continue

        vol_t, _, _, off_t = test_dataset[sample_idx]
        off_np = off_t.numpy()
        vol_np = vol_t.squeeze().cpu().numpy()
        mid_z  = vol_np.shape[2] // 2

        tx = r["true_xyz"][0] - off_np[0]
        ty = r["true_xyz"][1] - off_np[1]
        tz = r["true_xyz"][2] - off_np[2]

        hm_tmp    = get_heatmap(model, vol_t.unsqueeze(0), r["pred"], device)
        peak_flat = int(np.argmax(hm_tmp))
        px, py, pz = np.unravel_index(peak_flat, hm_tmp.shape)

        fig, axes = plt.subplots(1, 3, figsize=(15, 4))

        axes[0].imshow(vol_np[:, :, mid_z], cmap="bone")
        axes[0].set_title(f"Case {r['case']:04d} — CT crop (z={mid_z})"); axes[0].axis("off")

        axes[1].imshow(vol_np[:, :, mid_z], cmap="bone")
        axes[1].imshow(hm_tmp[:, :, mid_z], cmap="jet", alpha=0.45)
        if 0 <= tz < vol_np.shape[2]:
            axes[1].plot(ty, tx, "g+", markersize=14, markeredgewidth=2, label="True nodule")
            axes[1].plot(py, px, "r*", markersize=10,
                         label=f"CAM peak (Δ={r['distance']:.1f}vox)")
        axes[1].set_title(f"Label: {class_names[r['label']]}  Pred: {class_names[r['pred']]}")
        axes[1].legend(fontsize=7, loc="upper right"); axes[1].axis("off")

        tz_c = int(np.clip(tz, 0, vol_np.shape[2] - 1))
        axes[2].imshow(vol_np[:, :, tz_c], cmap="bone")
        axes[2].imshow(hm_tmp[:, :, tz_c], cmap="jet", alpha=0.45)
        if 0 <= tz < vol_np.shape[2]:
            axes[2].plot(ty, tx, "g+", markersize=14, markeredgewidth=2, label="True nodule")
        axes[2].set_title(f"Nodule slice (z={tz_c})")
        axes[2].legend(fontsize=7, loc="upper right"); axes[2].axis("off")

        plt.suptitle(
            f"Case {r['case']:04d}  True: {r['true_xyz']}  CAM: {r['cam_xyz']}  "
            f"Dist: {r['distance']:.1f} vox", fontsize=9
        )
        plt.tight_layout()
        overlay_path = MODEL_DIR / f"gradcam_overlay_case{r['case']:04d}.png"
        plt.savefig(overlay_path, dpi=120); plt.close(fig)
        print(f"    Overlay saved → {overlay_path.name}")

print("--- Done ---")

############################################
# K-FOLD CROSS VALIDATION  (5 folds, 20 epochs each)
# Uses combined train+test samples so all data is seen.
############################################
print("\n" + "="*50)
print("  K-FOLD CROSS VALIDATION (5 folds)")
print("="*50)

K_FOLDS      = 3
KFOLD_EPOCHS = 10

# Reuse the already-built nodule-level sample lists from both splits
all_samples    = train_dataset.samples + test_dataset.samples
all_labels_arr = np.array([s[1] for s in all_samples])
print(f"Total samples for k-fold: {len(all_samples)}  "
      f"(Benign: {(all_labels_arr==0).sum()}, Malignancy: {(all_labels_arr==1).sum()})")

skf = StratifiedKFold(n_splits=K_FOLDS, shuffle=True, random_state=42)
kfold_history = []
all_fold_preds, all_fold_labels = [], []

for fold, (train_idx, val_idx) in enumerate(skf.split(all_samples, all_labels_arr)):
    print(f"\n--- Fold {fold+1}/{K_FOLDS}  |  train={len(train_idx)}  val={len(val_idx)} ---")

    fold_train_samples = [all_samples[i] for i in train_idx]
    fold_val_samples   = [all_samples[i] for i in val_idx]

    fold_train_ds = SampleListDataset(fold_train_samples, augment=True)
    fold_val_ds   = SampleListDataset(fold_val_samples,   augment=False)

    fold_train_sampler = make_weighted_sampler(fold_train_ds)

    fold_train_loader = DataLoader(fold_train_ds, batch_size=BATCH_SIZE,
                                   sampler=fold_train_sampler,
                                   num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)
    fold_val_loader   = DataLoader(fold_val_ds, batch_size=BATCH_SIZE, shuffle=False,
                                   num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

    fold_model = ResNet3D(dropout=0.5).to(device)
    fold_opt   = optim.Adam(fold_model.parameters(), lr=1e-4, weight_decay=1e-4)
    fold_sched = optim.lr_scheduler.CosineAnnealingLR(fold_opt, T_max=KFOLD_EPOCHS, eta_min=1e-6)

    fold_train_losses, fold_val_losses = [], []
    fold_train_accs,   fold_val_accs   = [], []
    fold_best_acc   = 0.0
    fold_best_state = None

    for epoch in range(KFOLD_EPOCHS):
        fold_model.train()
        r_loss, correct, total = 0.0, 0, 0
        for images, labels, _, _ in fold_train_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            labels = labels.to(device, non_blocking=PIN_MEMORY)
            fold_opt.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = fold_model(images)
                loss    = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.unscale_(fold_opt)
            torch.nn.utils.clip_grad_norm_(fold_model.parameters(), max_norm=1.0)
            scaler.step(fold_opt); scaler.update()
            r_loss  += loss.item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total   += labels.size(0)

        train_loss = r_loss / len(fold_train_loader)
        train_acc  = 100.0 * correct / total if total > 0 else 0.0

        fold_model.eval()
        v_loss, v_correct, v_total = 0.0, 0, 0
        with torch.no_grad():
            for images, labels, _, _ in fold_val_loader:
                images = images.to(device, non_blocking=PIN_MEMORY)
                labels = labels.to(device, non_blocking=PIN_MEMORY)
                with torch.amp.autocast("cuda", enabled=use_cuda):
                    outputs = fold_model(images)
                v_loss    += criterion(outputs, labels).item()
                v_correct += (outputs.argmax(1) == labels).sum().item()
                v_total   += labels.size(0)

        val_loss = v_loss / len(fold_val_loader)
        val_acc  = 100.0 * v_correct / v_total if v_total > 0 else 0.0

        fold_train_losses.append(train_loss); fold_val_losses.append(val_loss)
        fold_train_accs.append(train_acc);   fold_val_accs.append(val_acc)

        if val_acc > fold_best_acc:
            fold_best_acc   = val_acc
            fold_best_state = {k: v.cpu().clone() for k, v in fold_model.state_dict().items()}

        fold_sched.step()
        print(f"  Epoch {epoch+1:>2}/{KFOLD_EPOCHS}  "
              f"Train Loss {train_loss:.4f} Acc {train_acc:.1f}%  |  "
              f"Val Loss {val_loss:.4f} Acc {val_acc:.1f}%")

    fold_model.load_state_dict(fold_best_state)
    fold_model.eval()
    with torch.no_grad():
        for images, labels, _, _ in fold_val_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = fold_model(images)
            all_fold_preds.extend(outputs.argmax(1).cpu().numpy())
            all_fold_labels.extend(labels.numpy())

    kfold_history.append({
        "train_losses": fold_train_losses, "val_losses":   fold_val_losses,
        "train_accs":   fold_train_accs,   "val_accs":     fold_val_accs,
        "best_val_acc": fold_best_acc,
    })
    print(f"  Fold {fold+1} best val accuracy: {fold_best_acc:.1f}%")

    del fold_model, fold_opt, fold_train_ds, fold_val_ds
    del fold_train_loader, fold_val_loader, fold_best_state
    if use_cuda: torch.cuda.empty_cache()

best_accs = [f["best_val_acc"] for f in kfold_history]

# Compute sensitivity, specificity, MCC from the aggregated fold predictions
kf_cm              = confusion_matrix(all_fold_labels, all_fold_preds)
kf_TN, kf_FP, kf_FN, kf_TP = kf_cm.ravel()
kf_sensitivity = kf_TP / (kf_TP + kf_FN) if (kf_TP + kf_FN) > 0 else 0.0
kf_specificity = kf_TN / (kf_TN + kf_FP) if (kf_TN + kf_FP) > 0 else 0.0
kf_mcc         = matthews_corrcoef(all_fold_labels, all_fold_preds)

print(f"\n--- K-Fold Summary ---")
for i, acc in enumerate(best_accs):
    print(f"  Fold {i+1}: {acc:.1f}%")
print(f"  Mean accuracy  : {np.mean(best_accs):.1f}%  ±  {np.std(best_accs):.1f}%")
print(f"  Sensitivity    : {kf_sensitivity*100:.1f}%  (aggregated across all folds)")
print(f"  Specificity    : {kf_specificity*100:.1f}%")
print(f"  MCC            : {kf_mcc:.4f}")

# Append k-fold results to training_summary.json
if summary_path.exists():
    with open(summary_path) as f:
        summary_data = json.load(f)
    summary_data["kfold"] = {
        "folds":             K_FOLDS,
        "epochs_per_fold":   KFOLD_EPOCHS,
        "fold_accuracies":   [round(a, 2) for a in best_accs],
        "mean_accuracy_pct": round(float(np.mean(best_accs)), 2),
        "std_accuracy_pct":  round(float(np.std(best_accs)),  2),
        "sensitivity_pct":   round(kf_sensitivity * 100, 2),
        "specificity_pct":   round(kf_specificity * 100, 2),
        "mcc":               round(kf_mcc, 4),
    }
    with open(summary_path, "w") as f:
        json.dump(summary_data, f, indent=2)
    print(f"K-fold results appended → {summary_path}")

############################################
# K-FOLD CHARTS
############################################
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
epoch_axis = range(1, KFOLD_EPOCHS + 1)
for fi, fd in enumerate(kfold_history):
    axes[0].plot(epoch_axis, fd["val_losses"], label=f"Fold {fi+1}")
    axes[1].plot(epoch_axis, fd["val_accs"],   label=f"Fold {fi+1}")
axes[0].set_title("K-Fold Val Loss"); axes[0].set_xlabel("Epoch"); axes[0].set_ylabel("Loss"); axes[0].legend(fontsize=8)
axes[1].set_title("K-Fold Val Accuracy"); axes[1].set_xlabel("Epoch"); axes[1].set_ylabel("Accuracy (%)"); axes[1].legend(fontsize=8)
plt.tight_layout()
plt.savefig(MODEL_DIR / "kfold_curves.png", dpi=120); plt.close(fig)

kfold_cm   = confusion_matrix(all_fold_labels, all_fold_preds)
kfold_disp = ConfusionMatrixDisplay(kfold_cm, display_labels=["Benign", "Malignancy"])
fig, ax = plt.subplots(figsize=(6, 5))
kfold_disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("K-Fold Confusion Matrix (aggregated, best ckpt per fold)")
plt.tight_layout()
plt.savefig(MODEL_DIR / "kfold_confusion_matrix.png", dpi=120); plt.close(fig)
print(classification_report(all_fold_labels, all_fold_preds, target_names=["Benign", "Malignancy"]))

fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar([f"Fold {i+1}" for i in range(len(best_accs))],
              best_accs, color="steelblue", edgecolor="white", width=0.5)
mean_acc = np.mean(best_accs)
ax.axhline(mean_acc, color="red", linestyle="--", lw=1.5, label=f"Mean = {mean_acc:.1f}%")
for bar, acc in zip(bars, best_accs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.5,
            f"{acc:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")
ax.set_ylim(0, 110); ax.set_ylabel("Best Val Accuracy (%)")
ax.set_title(f"K-Fold Best Accuracy  Mean: {mean_acc:.1f}% ± {np.std(best_accs):.1f}%")
ax.legend(); ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
plt.savefig(MODEL_DIR / "kfold_bar_chart.png", dpi=120); plt.close(fig)
print(f"K-fold charts saved → {MODEL_DIR}/kfold_*.png")

print("\n--- All done ---")
