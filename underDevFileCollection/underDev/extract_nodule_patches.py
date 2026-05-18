import os
import numpy as np
from pathlib import Path
from tqdm import tqdm

import pylidc as pl

# --- OUTPUT ---
OUT_ROOT = Path("DataNodules")  # ikke push denne til git
PATCH_SIZE = 64  # 64x64x64 voxels (kan endres)
DROP_SCORE = 3   # dropp malignancy==3

def crop_center(vol, center_zyx, size):
    zc, yc, xc = center_zyx
    r = size // 2

    z1, z2 = zc - r, zc + r
    y1, y2 = yc - r, yc + r
    x1, x2 = xc - r, xc + r

    # pad hvis utenfor
    pad_z1 = max(0, -z1); pad_y1 = max(0, -y1); pad_x1 = max(0, -x1)
    pad_z2 = max(0, z2 - vol.shape[0]); pad_y2 = max(0, y2 - vol.shape[1]); pad_x2 = max(0, x2 - vol.shape[2])

    z1 = max(0, z1); y1 = max(0, y1); x1 = max(0, x1)
    z2 = min(vol.shape[0], z2); y2 = min(vol.shape[1], y2); x2 = min(vol.shape[2], x2)

    patch = vol[z1:z2, y1:y2, x1:x2]
    if any([pad_z1, pad_y1, pad_x1, pad_z2, pad_y2, pad_x2]):
        patch = np.pad(
            patch,
            ((pad_z1, pad_z2), (pad_y1, pad_y2), (pad_x1, pad_x2)),
            mode="constant",
            constant_values=0
        )
    return patch

def malignancy_label(mean_score: float):
    # standard mapping:
    # 1-2 benign, 4-5 malignant, 3 drop
    if mean_score < 2.5:
        return "Benign"
    if mean_score > 3.5:
        return "Malignant"
    return None  # drop

def main():
    OUT_ROOT.mkdir(parents=True, exist_ok=True)
    for split in ["Train", "Test"]:
        for cls in ["Benign", "Malignant"]:
            (OUT_ROOT / split / cls).mkdir(parents=True, exist_ok=True)

    scans = pl.query(pl.Scan).all()
    print("Antall scans i pylidc db:", len(scans))

    # Pasient-basert split (80/20)
    # NB: bruker scan.patient_id
    patient_ids = sorted({s.patient_id for s in scans})
    rng = np.random.default_rng(42)
    rng.shuffle(patient_ids)
    cut = int(0.8 * len(patient_ids))
    train_patients = set(patient_ids[:cut])

    saved = {"Benign": 0, "Malignant": 0, "Dropped": 0}

    for scan in tqdm(scans, desc="Extracting nodules"):
        pid = scan.patient_id
        split = "Train" if pid in train_patients else "Test"

        # last volum (zyx)
        vol = scan.to_volume()  # numpy array

        # cluster annotations -> nodules
        nodules = scan.cluster_annotations()

        for n_idx, nodule_anns in enumerate(nodules):
            # malignancy per radiolog
            scores = [a.malignancy for a in nodule_anns if a.malignancy is not None]
            if len(scores) == 0:
                saved["Dropped"] += 1
                continue

            mean_score = float(np.mean(scores))
            lbl = malignancy_label(mean_score)
            if lbl is None:
                saved["Dropped"] += 1
                continue

            # finn et "center" for nodulen
            # vi bruker bbox fra hver annotation og tar midtpunkt + gjennomsnitt
            centers = []
            for a in nodule_anns:
                bb = a.bbox()  # ((zmin,zmax),(ymin,ymax),(xmin,xmax))
                (zmin, zmax), (ymin, ymax), (xmin, xmax) = bb
                centers.append(((zmin + zmax)//2, (ymin + ymax)//2, (xmin + xmax)//2))
            cz, cy, cx = np.mean(np.array(centers), axis=0).astype(int)

            patch = crop_center(vol, (cz, cy, cx), PATCH_SIZE)

            # normaliser litt (enkel)
            patch = patch.astype(np.float32)
            patch = (patch - np.mean(patch)) / (np.std(patch) + 1e-6)

            # lagre som .npy
            out_name = f"{pid}_n{n_idx}_m{mean_score:.2f}.npy"
            out_path = OUT_ROOT / split / lbl / out_name
            np.save(out_path, patch)
            saved[lbl] += 1

    print("Ferdig. Lagret:", saved)
    print("Output:", OUT_ROOT.resolve())

if __name__ == "__main__":
    main()
