"""
finetune_medicalnet.py — underdev4
------------------------------------
Fine-tunes a MedicalNet ResNet-18 backbone on the LIDC-IDRI lung CT dataset.

Two-phase strategy:
  Phase 1 (head-only):  freeze backbone, train only classifier  — fast convergence
  Phase 2 (full):       unfreeze everything, low LR fine-tune   — full adaptation

Data:   ../underdev3/Data/{Train,Test}/{Benign,Malignancy}/*.nii.gz
CSV:    ../underdev3/list3.2.csv
Backbone: checkpoints/resnet_18.pth  (MedicalNet pretrained)
Output:   checkpoints/medicalnet_finetuned_*.pth

Usage:
    cd underdev4
    python finetune_medicalnet.py
"""

import os
import re
import csv
import json
import sys
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
from sklearn.metrics import (
    confusion_matrix, ConfusionMatrixDisplay,
    classification_report,
    roc_curve, auc,
    average_precision_score,
)
from tqdm import tqdm

sys.path.insert(0, os.path.dirname(__file__))
from underDevFileCollection.underdev4.model import ResNet3D

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

HERE       = Path(__file__).parent
DATA_DIR   = HERE / "Data"
NODULE_CSV = HERE / ".." / "underdev3" / "list3.2.csv"
CKPT_DIR   = HERE / "checkpoints"
CKPT_DIR.mkdir(exist_ok=True)

BACKBONE_PATH  = CKPT_DIR / "resnet_18.pth"
LATEST_PATH    = CKPT_DIR / "medicalnet_finetuned_latest.pth"

CROP_SIZE   = (96, 96, 96)
BATCH_SIZE  = 4
NUM_WORKERS = 0
HU_MIN, HU_MAX = -1000, 400

# Phase 1 — classifier head only
P1_EPOCHS = 5
P1_LR     = 1e-3

# Phase 2 — full fine-tune
P2_EPOCHS = 15
P2_LR     = 1e-4

EARLY_STOP_PAT = 5

# ---------------------------------------------------------------------------
# Nodule map
# ---------------------------------------------------------------------------
def load_all_nodules(csv_path):
    if not Path(csv_path).exists():
        print(f"WARNING: {csv_path} not found")
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
        print(f"CSV column not found: {e}")
        return {}
    all_nodules = {}
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
    print(f"Loaded {sum(len(v) for v in all_nodules.values())} nodules "
          f"across {len(all_nodules)} cases")
    return all_nodules


def case_from_path(img_path):
    m = re.search(r"LIDC-IDRI-(\d+)", str(img_path))
    return int(m.group(1)) if m else None


def crop_volume(volume, cx, cy, cz, crop_size):
    hx, hy, hz = crop_size[0]//2, crop_size[1]//2, crop_size[2]//2
    _, X, Y, Z = volume.shape
    x0 = max(0, min(cx - hx, X - crop_size[0]))
    y0 = max(0, min(cy - hy, Y - crop_size[1]))
    z0 = max(0, min(cz - hz, Z - crop_size[2]))
    cropped = volume[:, x0:x0+crop_size[0], y0:y0+crop_size[1], z0:z0+crop_size[2]]
    px = crop_size[0] - cropped.shape[1]
    py = crop_size[1] - cropped.shape[2]
    pz = crop_size[2] - cropped.shape[3]
    if px > 0 or py > 0 or pz > 0:
        cropped = F.pad(cropped, (0, pz, 0, py, 0, px))
    return cropped


# ---------------------------------------------------------------------------
# Dataset — identical pipeline to underdev3
# ---------------------------------------------------------------------------
base_tf = tio.RescaleIntensity(out_min_max=(0, 1))
aug_tf  = tio.Compose([
    tio.RandomFlip(axes=(0, 1, 2)),
    tio.RandomAffine(scales=(0.9, 1.1), degrees=10),
    tio.RandomNoise(std=(0, 0.025)),
    tio.RandomBlur(std=(0, 0.5)),
    tio.RandomGamma(log_gamma=(-0.3, 0.3)),
])


class NiiDataset(Dataset):
    def __init__(self, root_dir, all_nodules, augment=False):
        self.samples = []
        self.augment = augment
        for label, folder in enumerate(["Benign", "Malignancy"]):
            folder_path = Path(root_dir) / folder
            if not folder_path.exists():
                continue
            for img_path in folder_path.glob("*.nii.gz"):
                case = case_from_path(img_path)
                if case and case in all_nodules:
                    for nd in all_nodules[case]:
                        self.samples.append((img_path, label, nd["x"], nd["y"], nd["z"]))
                else:
                    self.samples.append((img_path, label, None, None, None))

    def __len__(self):
        return len(self.samples)

    def _load(self, img_path, cx, cy, cz):
        arr = sitk.GetArrayFromImage(sitk.ReadImage(str(Path(img_path).resolve())))
        while arr.ndim > 3:
            arr = arr[0]
        vol = torch.from_numpy(arr).float().unsqueeze(0)
        vol = vol.permute(0, 3, 2, 1).contiguous()
        vol = torch.nan_to_num(vol, nan=0.0, posinf=0.0, neginf=0.0)
        vol = torch.clamp(vol, HU_MIN, HU_MAX)
        vol = base_tf(tio.Subject(mri=tio.ScalarImage(tensor=vol))).mri.data
        if cx is None:
            cx, cy, cz = vol.shape[1]//2, vol.shape[2]//2, vol.shape[3]//2
        return crop_volume(vol, cx, cy, cz, CROP_SIZE)

    def __getitem__(self, idx):
        img_path, label, cx, cy, cz = self.samples[idx]
        crop = self._load(img_path, cx, cy, cz)
        if self.augment:
            crop = aug_tf(tio.Subject(mri=tio.ScalarImage(tensor=crop))).mri.data
        return crop, label


def make_sampler(dataset):
    labels       = [s[1] for s in dataset.samples]
    class_counts = [labels.count(0), labels.count(1)]
    print(f"  Benign: {class_counts[0]}  Malignancy: {class_counts[1]}")
    weights = [1.0 / class_counts[l] for l in labels]
    return WeightedRandomSampler(weights, num_samples=len(weights), replacement=True)


# ---------------------------------------------------------------------------
# Backbone loader — strips DataParallel 'module.' prefix, strict=False
# ---------------------------------------------------------------------------
def load_medicalnet_backbone(model, backbone_path, device):
    ckpt  = torch.load(backbone_path, map_location=device, weights_only=False)
    raw   = ckpt.get("state_dict", ckpt)
    state = {k.replace("module.", ""): v for k, v in raw.items()}
    missing, unexpected = model.load_state_dict(state, strict=False)
    print(f"  Backbone loaded — missing: {missing}  unexpected: {unexpected}")
    return model


# ---------------------------------------------------------------------------
# Training helpers
# ---------------------------------------------------------------------------
def set_backbone_frozen(model, frozen: bool):
    """Freeze/unfreeze everything except the classifier head."""
    for name, param in model.named_parameters():
        if "classifier" not in name:
            param.requires_grad = not frozen
    status = "FROZEN" if frozen else "UNFROZEN"
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"  Backbone {status} — trainable params: {trainable:,}")


def run_epoch(model, loader, criterion, optimizer, device, scaler, train=True):
    model.train() if train else model.eval()
    total_loss, correct, total = 0.0, 0, 0
    ctx = torch.enable_grad() if train else torch.no_grad()
    use_cuda = device.type == "cuda"
    with ctx:
        for images, labels in tqdm(loader, leave=False):
            images = images.to(device)
            labels = labels.to(device)
            if train:
                optimizer.zero_grad(set_to_none=True)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = model(images)
                loss    = criterion(outputs, labels)
            if train:
                scaler.scale(loss).backward()
                scaler.unscale_(optimizer)
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                scaler.step(optimizer)
                scaler.update()
            total_loss += loss.item()
            correct    += (outputs.argmax(1) == labels).sum().item()
            total      += labels.size(0)
    acc = 100.0 * correct / total if total > 0 else 0.0
    return total_loss / len(loader), acc


def eval_with_probs(model, loader, device):
    model.eval()
    use_cuda = device.type == "cuda"
    all_labels, all_preds, all_probs = [], [], []
    with torch.no_grad():
        for images, labels in loader:
            images = images.to(device)
            with torch.amp.autocast("cuda", enabled=use_cuda):
                outputs = model(images)
            probs = torch.softmax(outputs.float(), dim=1)[:, 1]
            all_preds.extend(outputs.argmax(1).cpu().numpy())
            all_labels.extend(labels.numpy())
            all_probs.extend(probs.cpu().numpy())
    return np.array(all_labels), np.array(all_preds), np.array(all_probs)


# ---------------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------------
def save_curves(history, path):
    epochs = range(1, len(history["train_loss"]) + 1)
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    axes[0].plot(epochs, history["train_loss"], marker="o", markersize=3, label="Train")
    axes[0].plot(epochs, history["val_loss"],   marker="o", markersize=3, label="Val")
    axes[0].set_title("Loss"); axes[0].set_xlabel("Epoch"); axes[0].legend(); axes[0].grid(True, alpha=0.3)
    axes[1].plot(epochs, history["train_acc"], marker="o", markersize=3, label="Train")
    axes[1].plot(epochs, history["val_acc"],   marker="o", markersize=3, label="Val")
    axes[1].set_title("Accuracy (%)"); axes[1].set_xlabel("Epoch"); axes[1].set_ylim(0, 105)
    axes[1].legend(); axes[1].grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path, dpi=120)
    plt.close(fig)


def save_eval_plots(labels, preds, probs, prefix):
    # Confusion matrix
    disp = ConfusionMatrixDisplay(
        confusion_matrix(labels, preds), display_labels=["Benign", "Malignancy"]
    )
    fig, ax = plt.subplots(figsize=(6, 5))
    disp.plot(ax=ax, cmap="Blues", colorbar=False)
    ax.set_title(f"Confusion Matrix — {prefix}")
    plt.tight_layout()
    plt.savefig(CKPT_DIR / f"confusion_matrix_{prefix}.png", dpi=120)
    plt.close(fig)

    # ROC + PR
    try:
        fpr, tpr, _ = roc_curve(labels, probs)
        roc_auc     = auc(fpr, tpr)
        ap          = average_precision_score(labels, probs)
        fig, axes   = plt.subplots(1, 2, figsize=(12, 5))
        axes[0].plot(fpr, tpr, lw=2, label=f"AUC={roc_auc:.3f}")
        axes[0].plot([0,1],[0,1], "k--", lw=1)
        axes[0].set_xlabel("FPR"); axes[0].set_ylabel("TPR")
        axes[0].set_title(f"ROC — {prefix}"); axes[0].legend(); axes[0].grid(True, alpha=0.3)
        from sklearn.metrics import precision_recall_curve
        prec, rec, _ = precision_recall_curve(labels, probs)
        axes[1].plot(rec, prec, lw=2, label=f"AP={ap:.3f}")
        axes[1].axhline(labels.mean(), color="gray", linestyle="--", lw=1, label="Baseline")
        axes[1].set_xlabel("Recall"); axes[1].set_ylabel("Precision")
        axes[1].set_title(f"Precision-Recall — {prefix}"); axes[1].legend(); axes[1].grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(CKPT_DIR / f"roc_pr_{prefix}.png", dpi=120)
        plt.close(fig)
        return roc_auc, ap
    except Exception as e:
        print(f"  WARNING: ROC/PR plot skipped: {e}")
        return 0.0, 0.0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    device   = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_cuda = device.type == "cuda"
    print(f"Device: {device}")

    if not BACKBONE_PATH.exists():
        print(f"ERROR: backbone not found at {BACKBONE_PATH}")
        print("Copy resnet_18.pth from MedicalNet downloads into underdev4/checkpoints/")
        sys.exit(1)

    # ── Data ─────────────────────────────────────────────────────────────────
    all_nodules  = load_all_nodules(NODULE_CSV)
    train_ds     = NiiDataset(DATA_DIR / "Train", all_nodules, augment=True)
    val_ds       = NiiDataset(DATA_DIR / "Test",  all_nodules, augment=False)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, sampler=make_sampler(train_ds),
                              num_workers=NUM_WORKERS)
    val_loader   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                              num_workers=NUM_WORKERS)
    print(f"Train samples: {len(train_ds)}  |  Val samples: {len(val_ds)}")

    # ── Model ─────────────────────────────────────────────────────────────────
    model = ResNet3D(dropout=0.5).to(device)
    print(f"Loading MedicalNet backbone from {BACKBONE_PATH.name} …")
    load_medicalnet_backbone(model, BACKBONE_PATH, device)
    print(f"Total params: {sum(p.numel() for p in model.parameters()):,}")

    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    scaler    = torch.amp.GradScaler("cuda", enabled=use_cuda)

    best_acc   = 0.0
    full_history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 1 — train classifier head only
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print(f"\n{'='*55}")
    print(f"  PHASE 1 — head-only  ({P1_EPOCHS} epochs, LR={P1_LR})")
    print(f"{'='*55}")
    set_backbone_frozen(model, frozen=True)

    optimizer = optim.Adam(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=P1_LR, weight_decay=1e-4,
    )
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=P1_EPOCHS, eta_min=1e-6)

    p1_history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    for epoch in range(P1_EPOCHS):
        t0 = time.time()
        tr_loss, tr_acc = run_epoch(model, train_loader, criterion, optimizer, device, scaler, train=True)
        vl_loss, vl_acc = run_epoch(model, val_loader,   criterion, optimizer, device, scaler, train=False)
        scheduler.step()

        p1_history["train_loss"].append(tr_loss); p1_history["val_loss"].append(vl_loss)
        p1_history["train_acc"].append(tr_acc);   p1_history["val_acc"].append(vl_acc)
        full_history["train_loss"].append(tr_loss); full_history["val_loss"].append(vl_loss)
        full_history["train_acc"].append(tr_acc);   full_history["val_acc"].append(vl_acc)

        print(f"  P1 Epoch {epoch+1:>2}/{P1_EPOCHS} | "
              f"Train {tr_loss:.4f} / {tr_acc:.1f}%  "
              f"Val {vl_loss:.4f} / {vl_acc:.1f}%  "
              f"({time.time()-t0:.1f}s)")

        if vl_acc > best_acc:
            best_acc = vl_acc
            torch.save({"epoch": epoch+1, "phase": 1,
                        "model_state_dict": model.state_dict()}, LATEST_PATH)
            print(f"    >> Best so far ({best_acc:.1f}%) — saved")

    save_curves(p1_history, CKPT_DIR / "phase1_curves.png")
    print(f"Phase 1 done. Best val acc: {best_acc:.1f}%")

    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # PHASE 2 — full fine-tune
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    print(f"\n{'='*55}")
    print(f"  PHASE 2 — full fine-tune  ({P2_EPOCHS} epochs, LR={P2_LR})")
    print(f"{'='*55}")
    set_backbone_frozen(model, frozen=False)

    optimizer = optim.Adam(model.parameters(), lr=P2_LR, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=P2_EPOCHS, eta_min=1e-6)

    p2_history    = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    early_counter = 0

    for epoch in range(P2_EPOCHS):
        t0 = time.time()
        tr_loss, tr_acc = run_epoch(model, train_loader, criterion, optimizer, device, scaler, train=True)
        vl_loss, vl_acc = run_epoch(model, val_loader,   criterion, optimizer, device, scaler, train=False)
        scheduler.step()

        p2_history["train_loss"].append(tr_loss); p2_history["val_loss"].append(vl_loss)
        p2_history["train_acc"].append(tr_acc);   p2_history["val_acc"].append(vl_acc)
        full_history["train_loss"].append(tr_loss); full_history["val_loss"].append(vl_loss)
        full_history["train_acc"].append(tr_acc);   full_history["val_acc"].append(vl_acc)

        print(f"  P2 Epoch {epoch+1:>2}/{P2_EPOCHS} | "
              f"Train {tr_loss:.4f} / {tr_acc:.1f}%  "
              f"Val {vl_loss:.4f} / {vl_acc:.1f}%  "
              f"({time.time()-t0:.1f}s)")

        if vl_acc > best_acc:
            best_acc      = vl_acc
            early_counter = 0
            best_path     = CKPT_DIR / f"medicalnet_finetuned_best_ep{epoch+1}_acc{vl_acc:.1f}.pth"
            torch.save({"epoch": epoch+1, "phase": 2, "accuracy": vl_acc,
                        "model_state_dict": model.state_dict()}, best_path)
            torch.save({"epoch": epoch+1, "phase": 2,
                        "model_state_dict": model.state_dict()}, LATEST_PATH)
            print(f"    >> NEW BEST ({best_acc:.1f}%) — saved {best_path.name}")
        else:
            early_counter += 1
            if early_counter >= EARLY_STOP_PAT:
                print(f"\n  >> Early stop at epoch {epoch+1} "
                      f"(no improvement for {EARLY_STOP_PAT} epochs)")
                break

    save_curves(p2_history,    CKPT_DIR / "phase2_curves.png")
    save_curves(full_history,  CKPT_DIR / "full_training_curves.png")

    # ── Final evaluation ──────────────────────────────────────────────────────
    print("\n--- Final evaluation on val set ---")
    ckpt = torch.load(LATEST_PATH, map_location=device, weights_only=False)
    model.load_state_dict(ckpt["model_state_dict"])

    labels, preds, probs = eval_with_probs(model, val_loader, device)
    cm  = confusion_matrix(labels, preds)
    TN, FP, FN, TP = cm.ravel()
    acc         = 100.0 * (TP + TN) / len(labels)
    sensitivity = TP / (TP + FN) if (TP + FN) > 0 else 0.0
    specificity = TN / (TN + FP) if (TN + FP) > 0 else 0.0

    roc_auc, ap = save_eval_plots(labels, preds, probs, "final")

    print(classification_report(labels, preds, target_names=["Benign", "Malignancy"]))
    print(f"  Accuracy    : {acc:.1f}%")
    print(f"  Sensitivity : {sensitivity*100:.1f}%")
    print(f"  Specificity : {specificity*100:.1f}%")
    print(f"  AUC-ROC     : {roc_auc:.4f}")
    print(f"  Avg Prec    : {ap:.4f}")
    print(f"  TP={TP}  TN={TN}  FP={FP}  FN={FN}")

    summary = {
        "backbone": str(BACKBONE_PATH.name),
        "phase1_epochs": P1_EPOCHS,
        "phase2_epochs": P2_EPOCHS,
        "best_val_accuracy_pct": round(best_acc, 2),
        "final_accuracy_pct":    round(acc, 2),
        "sensitivity_pct":       round(sensitivity * 100, 2),
        "specificity_pct":       round(specificity * 100, 2),
        "auc_roc":               round(roc_auc, 4),
        "avg_precision":         round(ap, 4),
        "TP": int(TP), "TN": int(TN), "FP": int(FP), "FN": int(FN),
    }
    summary_path = CKPT_DIR / "finetune_summary.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nSummary saved → {summary_path}")
    print(f"Best checkpoint → {LATEST_PATH}")
    print("\n--- Done ---")


if __name__ == "__main__":
    main()
