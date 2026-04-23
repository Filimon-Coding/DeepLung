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
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
    classification_report,
    roc_curve, auc,
    precision_recall_curve, average_precision_score,
)
from sklearn.calibration import calibration_curve
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
BATCH_SIZE = 1                 # must be 1 — volumes have variable Z depth
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


class SampleListDataset(Dataset):
    """Flat dataset built from a list of (path, label) tuples — used for k-fold."""
    def __init__(self, samples, transform=None):
        self.samples   = samples
        self.transform = transform

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        image_np = sitk.GetArrayFromImage(sitk.ReadImage(str(img_path)))
        volume   = torch.from_numpy(image_np).float().unsqueeze(0)
        volume   = volume.permute(0, 3, 2, 1).contiguous()
        volume   = torch.nan_to_num(volume, nan=0.0, posinf=0.0, neginf=0.0)
        subject  = tio.Subject(mri=tio.ScalarImage(tensor=volume))
        if self.transform:
            subject = self.transform(subject)
        return subject.mri.data, label, str(img_path)


train_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.RandomFlip(axes=(0, 1, 2)),
    tio.RandomAffine(scales=(0.95, 1.05), degrees=5),
    tio.RandomNoise(std=(0, 0.02)),
    tio.RandomBlur(std=(0, 0.5)),
])

test_transform = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
])

train_dataset = NiiDataset(DATA_DIR / "Train", transform=train_transform)
test_dataset  = NiiDataset(DATA_DIR / "Test",  transform=test_transform)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                          num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)
test_loader  = DataLoader(test_dataset,  batch_size=BATCH_SIZE, shuffle=False,
                          num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

print(f"--- Loaded {len(train_dataset)} training and {len(test_dataset)} test samples ---")
print(f"--- No cropping — full volumes | Batch size: {BATCH_SIZE} ---")

############################################
# DATASET DISTRIBUTION CHART
############################################
def _class_counts(dataset):
    labels = [s[1] for s in dataset.samples]
    return labels.count(0), labels.count(1)   # (benign, malignancy)

tr_b, tr_m = _class_counts(train_dataset)
te_b, te_m = _class_counts(test_dataset)

fig, axes = plt.subplots(1, 3, figsize=(15, 5))
class_names = ["Benign", "Malignancy"]
colors      = ["steelblue", "tomato"]

# Train bar
axes[0].bar(class_names, [tr_b, tr_m], color=colors, edgecolor="white")
for i, v in enumerate([tr_b, tr_m]):
    axes[0].text(i, v + 0.3, str(v), ha="center", fontsize=12, fontweight="bold")
axes[0].set_title(f"Train Set  (n={tr_b + tr_m})")
axes[0].set_ylabel("Number of samples")
axes[0].grid(axis="y", alpha=0.3)

# Test bar
axes[1].bar(class_names, [te_b, te_m], color=colors, edgecolor="white")
for i, v in enumerate([te_b, te_m]):
    axes[1].text(i, v + 0.3, str(v), ha="center", fontsize=12, fontweight="bold")
axes[1].set_title(f"Test Set  (n={te_b + te_m})")
axes[1].set_ylabel("Number of samples")
axes[1].grid(axis="y", alpha=0.3)

# Total pie chart
total_b = tr_b + te_b
total_m = tr_m + te_m
wedges, texts, autotexts = axes[2].pie(
    [total_b, total_m],
    labels=class_names,
    colors=colors,
    autopct="%1.1f%%",
    startangle=90,
    wedgeprops=dict(edgecolor="white", linewidth=2),
)
for at in autotexts:
    at.set_fontsize(12)
axes[2].set_title(f"Total Dataset  (n={total_b + total_m})")

plt.suptitle("Dataset Class Distribution", fontsize=14, fontweight="bold")
plt.tight_layout()
dist_path = MODEL_DIR / "dataset_distribution.png"
plt.savefig(dist_path, dpi=120)
plt.close(fig)
print(f"Dataset distribution saved → {dist_path}")

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
    """Grad-CAM on layer3 — returns a 3-D numpy heatmap matching input volume size."""
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

    # GradCAM++ weights — sharper localization than plain mean(grads)
    grads    = gradients[0]
    acts     = activations[0]
    grads_sq = grads.pow(2)
    grads_cb = grads.pow(3)
    act_sum  = acts.sum(dim=(2, 3, 4), keepdim=True)
    alpha    = grads_sq / (2.0 * grads_sq + act_sum * grads_cb + 1e-7)
    weights  = (alpha * F.relu(grads)).sum(dim=(2, 3, 4), keepdim=True)
    cam = F.relu((weights * acts).sum(dim=1).squeeze())

    # Upsample back to the original volume spatial size
    target_size = tuple(img_tensor.shape[2:])
    cam_resized = F.interpolate(
        cam.detach().cpu().unsqueeze(0).unsqueeze(0),
        size=target_size,
        mode="trilinear",
        align_corners=False,
    ).squeeze().numpy()

    # Keep only top 30% of activations — suppresses background lung noise
    if cam_resized.max() > 0:
        nonzero = cam_resized[cam_resized > 0]
        thr = float(np.percentile(nonzero, 70)) if len(nonzero) > 0 else 0.0
        cam_resized[cam_resized < thr] = 0.0
        c_max = cam_resized.max()
        if c_max > 0:
            cam_resized = cam_resized / c_max

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
           "test_loss":  [], "test_acc":  [],
           "lr":         []}

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
    history["lr"].append(optimizer.param_groups[0]["lr"])

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
# TRAINING CURVES  (annotated)
############################################
epochs_axis = range(1, len(history["train_loss"]) + 1)

fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# --- Loss ---
axes[0].plot(epochs_axis, history["train_loss"], marker="o", markersize=3, label="Train")
axes[0].plot(epochs_axis, history["test_loss"],  marker="o", markersize=3, label="Val")
best_val_loss_ep = int(np.argmin(history["test_loss"])) + 1
best_val_loss    = min(history["test_loss"])
axes[0].axvline(best_val_loss_ep, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
axes[0].annotate(f"best {best_val_loss:.4f}\n(ep {best_val_loss_ep})",
                 xy=(best_val_loss_ep, best_val_loss),
                 xytext=(best_val_loss_ep + 1, best_val_loss + 0.02),
                 fontsize=7, color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=0.8))
axes[0].set_title("Loss per Epoch")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Cross-Entropy Loss")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# --- Accuracy ---
axes[1].plot(epochs_axis, history["train_acc"], marker="o", markersize=3, label="Train")
axes[1].plot(epochs_axis, history["test_acc"],  marker="o", markersize=3, label="Val")
best_val_acc_ep = int(np.argmax(history["test_acc"])) + 1
best_val_acc_v  = max(history["test_acc"])
axes[1].axvline(best_val_acc_ep, color="red", linestyle="--", linewidth=0.8, alpha=0.6)
axes[1].annotate(f"best {best_val_acc_v:.1f}%\n(ep {best_val_acc_ep})",
                 xy=(best_val_acc_ep, best_val_acc_v),
                 xytext=(best_val_acc_ep + 1, best_val_acc_v - 5),
                 fontsize=7, color="red",
                 arrowprops=dict(arrowstyle="->", color="red", lw=0.8))
axes[1].set_title("Accuracy per Epoch (%)")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy (%)")
axes[1].set_ylim(0, 105)
axes[1].legend()
axes[1].grid(True, alpha=0.3)

# --- Learning Rate ---
axes[2].plot(epochs_axis, history["lr"], marker="o", markersize=3, color="purple", label="LR")
lr_drops = [i + 1 for i in range(1, len(history["lr"]))
            if history["lr"][i] < history["lr"][i - 1]]
for ep in lr_drops:
    axes[2].axvline(ep, color="orange", linestyle="--", linewidth=0.8, alpha=0.7)
    axes[2].annotate(f"↓ ep {ep}", xy=(ep, history["lr"][ep - 1]),
                     xytext=(ep + 0.5, history["lr"][ep - 1]),
                     fontsize=7, color="orange")
axes[2].set_title("Learning Rate Schedule")
axes[2].set_xlabel("Epoch")
axes[2].set_ylabel("Learning Rate")
axes[2].set_yscale("log")
axes[2].legend()
axes[2].grid(True, alpha=0.3)

plt.tight_layout()
curves_path = MODEL_DIR / "training_curves.png"
plt.savefig(curves_path, dpi=120)
plt.close(fig)
print(f"Training curves saved → {curves_path}")

############################################
# CONFUSION MATRIX (on full test set)
############################################
print("\n--- Generating confusion matrix ---")
model.eval()
cm_preds, cm_labels, cm_probs = [], [], []

with torch.no_grad():
    for images, labels, _ in test_loader:
        images = images.to(device, non_blocking=PIN_MEMORY)
        with torch.amp.autocast("cuda", enabled=use_cuda):
            outputs = model(images)
        probs = torch.softmax(outputs.float(), dim=1)[:, 1]   # P(malignancy)
        cm_preds.extend(outputs.argmax(1).cpu().numpy())
        cm_labels.extend(labels.numpy())
        cm_probs.extend(probs.cpu().numpy())

cm = confusion_matrix(cm_labels, cm_preds)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Benign", "Malignancy"])

fig, ax = plt.subplots(figsize=(6, 5))
disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("Confusion Matrix — Test Set")
plt.tight_layout()
cm_path = MODEL_DIR / "confusion_matrix.png"
plt.savefig(cm_path, dpi=120)
plt.close(fig)
print(f"Confusion matrix saved → {cm_path}")
print(classification_report(cm_labels, cm_preds, target_names=["Benign", "Malignancy"]))

############################################
# ROC CURVE + PRECISION-RECALL CURVE
############################################
print("--- Generating ROC and Precision-Recall curves ---")

fpr, tpr, _   = roc_curve(cm_labels, cm_probs)
roc_auc       = auc(fpr, tpr)

precision, recall, _ = precision_recall_curve(cm_labels, cm_probs)
avg_precision         = average_precision_score(cm_labels, cm_probs)

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# ROC
axes[0].plot(fpr, tpr, color="steelblue", lw=2,
             label=f"ROC curve (AUC = {roc_auc:.3f})")
axes[0].plot([0, 1], [0, 1], color="gray", linestyle="--", lw=1, label="Random (AUC = 0.5)")
axes[0].set_xlim(0, 1); axes[0].set_ylim(0, 1.02)
axes[0].set_xlabel("False Positive Rate")
axes[0].set_ylabel("True Positive Rate")
axes[0].set_title("ROC Curve — Test Set")
axes[0].legend(loc="lower right")
axes[0].grid(True, alpha=0.3)

# Precision-Recall
axes[1].plot(recall, precision, color="darkorange", lw=2,
             label=f"PR curve (AP = {avg_precision:.3f})")
axes[1].axhline(sum(cm_labels) / len(cm_labels), color="gray", linestyle="--", lw=1,
                label="Baseline (class ratio)")
axes[1].set_xlim(0, 1); axes[1].set_ylim(0, 1.02)
axes[1].set_xlabel("Recall")
axes[1].set_ylabel("Precision")
axes[1].set_title("Precision-Recall Curve — Test Set")
axes[1].legend(loc="upper right")
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
roc_pr_path = MODEL_DIR / "roc_pr_curves.png"
plt.savefig(roc_pr_path, dpi=120)
plt.close(fig)
print(f"ROC + PR curves saved → {roc_pr_path}")
print(f"  AUC-ROC: {roc_auc:.4f}  |  Average Precision: {avg_precision:.4f}")

############################################
# CONFIDENCE HISTOGRAM
############################################
print("--- Generating confidence histogram ---")
cm_probs_arr  = np.array(cm_probs)
cm_labels_arr = np.array(cm_labels)
cm_preds_arr  = np.array(cm_preds)

correct_mask = (cm_labels_arr == cm_preds_arr)
wrong_mask   = ~correct_mask

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Left: correct vs wrong predictions
axes[0].hist(cm_probs_arr[correct_mask], bins=20, range=(0, 1),
             alpha=0.7, color="steelblue",  label=f"Correct  (n={correct_mask.sum()})")
axes[0].hist(cm_probs_arr[wrong_mask],   bins=20, range=(0, 1),
             alpha=0.7, color="tomato",     label=f"Wrong  (n={wrong_mask.sum()})")
axes[0].axvline(0.5, color="gray", linestyle="--", linewidth=1, label="Decision threshold")
axes[0].set_xlabel("Predicted P(Malignancy)")
axes[0].set_ylabel("Count")
axes[0].set_title("Confidence Distribution — Correct vs Wrong")
axes[0].legend()
axes[0].grid(True, alpha=0.3)

# Right: per true class
benign_probs     = cm_probs_arr[cm_labels_arr == 0]
malignant_probs  = cm_probs_arr[cm_labels_arr == 1]
axes[1].hist(benign_probs,    bins=20, range=(0, 1),
             alpha=0.7, color="steelblue", label=f"True Benign  (n={len(benign_probs)})")
axes[1].hist(malignant_probs, bins=20, range=(0, 1),
             alpha=0.7, color="tomato",    label=f"True Malignancy  (n={len(malignant_probs)})")
axes[1].axvline(0.5, color="gray", linestyle="--", linewidth=1, label="Decision threshold")
axes[1].set_xlabel("Predicted P(Malignancy)")
axes[1].set_ylabel("Count")
axes[1].set_title("Confidence Distribution — Per True Class")
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.suptitle("Model Confidence Histogram", fontsize=13, fontweight="bold")
plt.tight_layout()
conf_hist_path = MODEL_DIR / "confidence_histogram.png"
plt.savefig(conf_hist_path, dpi=120)
plt.close(fig)
print(f"Confidence histogram saved → {conf_hist_path}")

############################################
# CALIBRATION CURVE
############################################
print("--- Generating calibration curve ---")
fraction_pos, mean_pred = calibration_curve(cm_labels_arr, cm_probs_arr, n_bins=10)

fig, ax = plt.subplots(figsize=(7, 6))
ax.plot(mean_pred, fraction_pos, marker="o", color="steelblue", lw=2,
        label="Model calibration")
ax.plot([0, 1], [0, 1], linestyle="--", color="gray", lw=1.5,
        label="Perfect calibration")
ax.fill_between(mean_pred, fraction_pos, mean_pred,
                alpha=0.15, color="steelblue", label="Calibration gap")
ax.set_xlabel("Mean Predicted Probability")
ax.set_ylabel("Fraction of Positives (Malignancy)")
ax.set_title("Calibration Curve — Test Set\n"
             "(closer to dashed line = better calibrated)")
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_xlim(0, 1); ax.set_ylim(0, 1)
plt.tight_layout()
calib_path = MODEL_DIR / "calibration_curve.png"
plt.savefig(calib_path, dpi=120)
plt.close(fig)
print(f"Calibration curve saved → {calib_path}")

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

############################################
# K-FOLD CROSS VALIDATION (5-fold, 15 epochs each)
############################################
print("\n" + "="*50)
print("  K-FOLD CROSS VALIDATION (5 folds)")
print("="*50)

K_FOLDS      = 5
KFOLD_EPOCHS = 15   # fewer epochs per fold keeps CI runtime reasonable

# Collect every sample from both Train and Test folders into a flat list
all_samples = []
for label_idx, folder in enumerate(["Benign", "Malignancy"]):
    for split in ["Train", "Test"]:
        folder_path = DATA_DIR / split / folder
        if folder_path.exists():
            for img_path in folder_path.glob("*.nii.gz"):
                all_samples.append((img_path, label_idx))

all_labels_arr = np.array([s[1] for s in all_samples])
print(f"Total samples for k-fold: {len(all_samples)}  "
      f"(Benign: {(all_labels_arr==0).sum()}, Malignancy: {(all_labels_arr==1).sum()})")

skf = StratifiedKFold(n_splits=K_FOLDS, shuffle=True, random_state=42)

kfold_history = []   # list of per-fold dicts
all_fold_preds, all_fold_labels = [], []

for fold, (train_idx, val_idx) in enumerate(skf.split(all_samples, all_labels_arr)):
    print(f"\n--- Fold {fold+1}/{K_FOLDS}  |  train={len(train_idx)}  val={len(val_idx)} ---")

    fold_train_samples = [all_samples[i] for i in train_idx]
    fold_val_samples   = [all_samples[i] for i in val_idx]

    fold_train_ds = SampleListDataset(fold_train_samples, transform=train_transform)
    fold_val_ds   = SampleListDataset(fold_val_samples,   transform=test_transform)

    fold_train_loader = DataLoader(fold_train_ds, batch_size=BATCH_SIZE, shuffle=True,
                                   num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)
    fold_val_loader   = DataLoader(fold_val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                                   num_workers=NUM_WORKERS, pin_memory=PIN_MEMORY)

    fold_model = ResNet3D().to(device)
    fold_opt   = optim.Adam(fold_model.parameters(), lr=1e-4)

    fold_train_losses, fold_val_losses   = [], []
    fold_train_accs,   fold_val_accs     = [], []

    for epoch in range(KFOLD_EPOCHS):
        fold_model.train()
        r_loss, correct, total = 0.0, 0, 0

        for images, labels, _ in fold_train_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            labels = labels.to(device, non_blocking=PIN_MEMORY)
            fold_opt.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = fold_model(images)
                loss    = criterion(outputs, labels)
            scaler.scale(loss).backward()
            scaler.step(fold_opt)
            scaler.update()
            r_loss  += loss.item()
            correct += (outputs.argmax(1) == labels).sum().item()
            total   += labels.size(0)

        train_loss = r_loss / len(fold_train_loader)
        train_acc  = 100.0 * correct / total if total > 0 else 0.0

        fold_model.eval()
        v_loss, v_correct, v_total = 0.0, 0, 0
        with torch.no_grad():
            for images, labels, _ in fold_val_loader:
                images = images.to(device, non_blocking=PIN_MEMORY)
                labels = labels.to(device, non_blocking=PIN_MEMORY)
                with torch.amp.autocast("cuda", enabled=use_cuda):
                    outputs = fold_model(images)
                loss = criterion(outputs, labels)
                v_loss    += loss.item()
                v_correct += (outputs.argmax(1) == labels).sum().item()
                v_total   += labels.size(0)

        val_loss = v_loss / len(fold_val_loader)
        val_acc  = 100.0 * v_correct / v_total if v_total > 0 else 0.0

        fold_train_losses.append(train_loss)
        fold_val_losses.append(val_loss)
        fold_train_accs.append(train_acc)
        fold_val_accs.append(val_acc)

        print(f"  Epoch {epoch+1:>2}/{KFOLD_EPOCHS}  "
              f"Train Loss {train_loss:.4f} Acc {train_acc:.1f}%  |  "
              f"Val Loss {val_loss:.4f} Acc {val_acc:.1f}%")

    # Collect predictions for the fold-level confusion matrix
    fold_model.eval()
    with torch.no_grad():
        for images, labels, _ in fold_val_loader:
            images = images.to(device, non_blocking=PIN_MEMORY)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = fold_model(images)
            all_fold_preds.extend(outputs.argmax(1).cpu().numpy())
            all_fold_labels.extend(labels.numpy())

    kfold_history.append({
        "train_losses": fold_train_losses,
        "val_losses":   fold_val_losses,
        "train_accs":   fold_train_accs,
        "val_accs":     fold_val_accs,
        "best_val_acc": max(fold_val_accs),
    })
    print(f"  Fold {fold+1} best val accuracy: {kfold_history[-1]['best_val_acc']:.1f}%")

    # Free GPU memory between folds
    del fold_model, fold_opt, fold_train_ds, fold_val_ds
    del fold_train_loader, fold_val_loader
    torch.cuda.empty_cache() if use_cuda else None

# Summary
best_accs = [f["best_val_acc"] for f in kfold_history]
print(f"\n--- K-Fold Summary ---")
for i, acc in enumerate(best_accs):
    print(f"  Fold {i+1}: {acc:.1f}%")
print(f"  Mean: {np.mean(best_accs):.1f}%  ±  {np.std(best_accs):.1f}%")

############################################
# K-FOLD LEARNING CURVES (all folds on one chart)
############################################
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
epoch_axis = range(1, KFOLD_EPOCHS + 1)

for fold_idx, fd in enumerate(kfold_history):
    label = f"Fold {fold_idx+1}"
    axes[0].plot(epoch_axis, fd["val_losses"],  label=label)
    axes[1].plot(epoch_axis, fd["val_accs"],    label=label)

axes[0].set_title("K-Fold Validation Loss per Epoch")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss")
axes[0].legend(fontsize=8)

axes[1].set_title("K-Fold Validation Accuracy per Epoch")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy (%)")
axes[1].legend(fontsize=8)

plt.tight_layout()
kfold_curves_path = MODEL_DIR / "kfold_curves.png"
plt.savefig(kfold_curves_path, dpi=120)
plt.close(fig)
print(f"K-fold curves saved → {kfold_curves_path}")

############################################
# K-FOLD CONFUSION MATRIX (aggregated over all folds)
############################################
kfold_cm = confusion_matrix(all_fold_labels, all_fold_preds)
kfold_disp = ConfusionMatrixDisplay(confusion_matrix=kfold_cm,
                                    display_labels=["Benign", "Malignancy"])
fig, ax = plt.subplots(figsize=(6, 5))
kfold_disp.plot(ax=ax, cmap="Blues", colorbar=False)
ax.set_title("K-Fold Confusion Matrix (aggregated across all folds)")
plt.tight_layout()
kfold_cm_path = MODEL_DIR / "kfold_confusion_matrix.png"
plt.savefig(kfold_cm_path, dpi=120)
plt.close(fig)
print(f"K-fold confusion matrix saved → {kfold_cm_path}")
print(classification_report(all_fold_labels, all_fold_preds,
                             target_names=["Benign", "Malignancy"]))

############################################
# K-FOLD BAR CHART — best accuracy per fold
############################################
fig, ax = plt.subplots(figsize=(8, 5))
fold_labels = [f"Fold {i+1}" for i in range(len(best_accs))]
bars = ax.bar(fold_labels, best_accs, color="steelblue", edgecolor="white", width=0.5)

mean_acc = np.mean(best_accs)
ax.axhline(mean_acc, color="red", linestyle="--", linewidth=1.5,
           label=f"Mean = {mean_acc:.1f}%")

for bar, acc in zip(bars, best_accs):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
            f"{acc:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold")

ax.set_ylim(0, 110)
ax.set_ylabel("Best Validation Accuracy (%)")
ax.set_title(f"K-Fold Cross Validation — Best Accuracy per Fold\n"
             f"Mean: {mean_acc:.1f}%  ±  {np.std(best_accs):.1f}%")
ax.legend()
ax.grid(axis="y", alpha=0.3)
plt.tight_layout()
kfold_bar_path = MODEL_DIR / "kfold_bar_chart.png"
plt.savefig(kfold_bar_path, dpi=120)
plt.close(fig)
print(f"K-fold bar chart saved → {kfold_bar_path}")

print("\n--- All done ---")
