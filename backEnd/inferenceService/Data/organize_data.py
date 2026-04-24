"""
organize_data.py
----------------
Reads benignCases.md and malignantCases.md to get the case IDs,
then finds the matching .nii.gz files in your flat source folder
and moves them into:

    Data/
    ├── Train/
    │   ├── Benign/        (587 files)
    │   └── Malignancy/    (206 files)
    └── Test/
        ├── Benign/        (147 files)
        └── Malignancy/    (51 files)
"""

import re
import random
import shutil
from pathlib import Path

random.seed(42)

# ── CONFIGURE THESE TWO LINES ─────────────────────────────────────
SRC_FOLDER    = Path("/media/neov/NewDisk/NewDownload/nifti_output_usingDcm2niixx")
BENIGN_MD     = Path("/home/neov/Documents/MinCodingLinuxV/Prosjekter/6thSemester/DATA3900Bacheloroppgave/Bachelor-CRAI/backEnd/inferenceService/PredictOutPut/benignCases.md")
MALIGNANT_MD  = Path("/home/neov/Documents/MinCodingLinuxV/Prosjekter/6thSemester/DATA3900Bacheloroppgave/Bachelor-CRAI/backEnd/inferenceService/PredictOutPut/malignantCases.md")
OUT_BASE      = Path("/media/neov/NewDisk/NewDownload/allData")
TEST_RATIO    = 0.20
# ──────────────────────────────────────────────────────────────────


def extract_ids(md_path):
    """Pull every LIDC-IDRI-XXXX pattern from a markdown file."""
    text = md_path.read_text()
    ids  = set(re.findall(r"LIDC-IDRI-\d{4}", text))
    return ids


def move_split(files, train_dst, test_dst):
    files = list(files)
    random.shuffle(files)
    n_test      = round(len(files) * TEST_RATIO)
    test_files  = files[:n_test]
    train_files = files[n_test:]
    train_dst.mkdir(parents=True, exist_ok=True)
    test_dst.mkdir(parents=True,  exist_ok=True)
    for f in train_files:
        shutil.copy2(str(f), train_dst / f.name)
    for f in test_files:
        shutil.copy2(str(f), test_dst  / f.name)
    return len(train_files), len(test_files)


# ── STEP 1: load case ID lists ────────────────────────────────────
print("=== Reading case ID lists ===")
benign_ids    = extract_ids(BENIGN_MD)
malignant_ids = extract_ids(MALIGNANT_MD)
print(f"  Benign IDs found in md:    {len(benign_ids)}")
print(f"  Malignant IDs found in md: {len(malignant_ids)}")

overlap = benign_ids & malignant_ids
if overlap:
    print(f"  WARNING: {len(overlap)} IDs appear in both files: {overlap}")

# ── STEP 2: scan source folder and classify each file ─────────────
print(f"\n=== Scanning {SRC_FOLDER} ===")
all_files = list(SRC_FOLDER.glob("*.nii.gz"))
print(f"  Total .nii.gz files found: {len(all_files)}")

benign_files    = []
malignant_files = []
unmatched_files = []

for f in all_files:
    match = re.search(r"LIDC-IDRI-\d{4}", f.name)
    if not match:
        unmatched_files.append(f)
        continue
    case_id = match.group()
    if case_id in malignant_ids:
        malignant_files.append(f)
    elif case_id in benign_ids:
        benign_files.append(f)
    else:
        unmatched_files.append(f)

print(f"  Matched as Benign:     {len(benign_files)}")
print(f"  Matched as Malignancy: {len(malignant_files)}")
if unmatched_files:
    print(f"  Unmatched (skipped):   {len(unmatched_files)}")
    for f in unmatched_files:
        print(f"    - {f.name}")

# ── STEP 3: move into Data/ structure ─────────────────────────────
print("\n=== Moving files ===")
tr_b, te_b = move_split(benign_files,    OUT_BASE / "Train/Benign",    OUT_BASE / "Test/Benign")
tr_m, te_m = move_split(malignant_files, OUT_BASE / "Train/Malignancy", OUT_BASE / "Test/Malignancy")
print(f"  Benign    → Train: {tr_b}  |  Test: {te_b}")
print(f"  Malignancy→ Train: {tr_m}  |  Test: {te_m}")

# ── STEP 4: verify ────────────────────────────────────────────────
print("\n=== Verification ===")
for folder in ["Train/Benign", "Train/Malignancy", "Test/Benign", "Test/Malignancy"]:
    actual = len(list((OUT_BASE / folder).glob("*.nii.gz")))
    print(f"  {OUT_BASE / folder}: {actual} files")

print("\nDone. Data is organized and ready.")
