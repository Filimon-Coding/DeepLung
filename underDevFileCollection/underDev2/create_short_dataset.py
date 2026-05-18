import shutil
from pathlib import Path
import pandas as pd

# --------- CONFIG ----------
INPUT_DIR = Path("/media/neov/NewDisk/NewDownload/ALLNewDicomNifit/")     # <-- change to where your nii.gz files are
DATA_DIR  = Path("Data")            # output structure Data/Train/... Data/Test/...
DIAG_XLS  = Path("tcia-diagnosis-data-2012-04-20.xls")
TARGET_PER_CLASS = 100

# --------- LOAD DIAGNOSIS MAP ----------
df = pd.read_excel(DIAG_XLS, sheet_name="Diagnosis Truth")

diag_col_candidates = [c for c in df.columns if "Diagnosis at the Patient Level" in str(c)]
if not diag_col_candidates:
    raise ValueError("Fant ikke kolonnen 'Diagnosis at the Patient Level' i XLS-fila.")
diag_col = diag_col_candidates[0]

diagnosis_map = {}
for _, row in df.iterrows():
    pid = str(row.get("TCIA Patient ID", ""))
    try:
        case_id = int(pid.split("-")[-1])  # "LIDC-IDRI-0068" -> 68
    except:
        continue

    code = row.get(diag_col, None)
    try:
        code = int(code)
    except:
        continue

    diagnosis_map[case_id] = code

print(f"[DIAG] Loaded diagnosis for {len(diagnosis_map)} patients from XLS.")


# --------- DATASET BUILDER ----------
def extract_case_id(fname: str):
    """
    Matches your earlier logic:
    takes the last '-' chunk, then the first '_' chunk.
    Example expected patterns:
      something-0086_xxx.nii.gz  -> 86
    """
    try:
        return int(fname.split('-')[-1].split('_')[0])
    except:
        return None


def label_from_diagnosis(case_id: int):
    """
    Returns 'Malignancy', 'Benign', or None (skip).
    Diagnosis codes (per TCIA sheet):
      0 = Unknown
      1 = Benign
      2 = Malignant primary
      3 = Malignant metastatic
    """
    code = diagnosis_map.get(case_id, None)
    if code is None or code == 0:
        return None
    if code in (2, 3):
        return "Malignancy"
    if code == 1:
        return "Benign"
    return None


def create_short_dataset(file_list, target_count=100, test_ratio=0.2):
    counts_train = {"Malignancy": 0, "Benign": 0}
    counts_test  = {"Malignancy": 0, "Benign": 0}

    target_test  = int(round(target_count * test_ratio))
    target_train = target_count - target_test

    print(f"--- Target per class: {target_count} (Train={target_train}, Test={target_test}) ---")

    for fname in file_list:
        # stop if done for both classes
        done = all(counts_train[c] >= target_train and counts_test[c] >= target_test for c in ["Malignancy", "Benign"])
        if done:
            print("--- Goal reached ---")
            print("Train:", counts_train, "Test:", counts_test)
            break

        case_id = extract_case_id(fname)
        if case_id is None:
            continue

        label = label_from_diagnosis(case_id)
        if label is None:
            # skip unknown or missing diagnosis in XLS
            continue

        # decide subset per class (fill Test first up to target_test, then Train)
        if counts_test[label] < target_test:
            subset = "Test"
        elif counts_train[label] < target_train:
            subset = "Train"
        else:
            continue  # this class already full

        dest_path = DATA_DIR / subset / label
        dest_path.mkdir(parents=True, exist_ok=True)

        src = INPUT_DIR / fname
        dst = dest_path / fname

        if not dst.exists():
            shutil.copy(src, dst)

        if subset == "Test":
            counts_test[label] += 1
        else:
            counts_train[label] += 1

        total = sum(counts_train.values()) + sum(counts_test.values())
        if total % 20 == 0:
            print(f"[DATA] Train {counts_train} | Test {counts_test}")

    print("--- Finished ---")
    print("Train:", counts_train, "Test:", counts_test)


if __name__ == "__main__":
    # collect files
    all_files = sorted([p.name for p in INPUT_DIR.glob("*.nii*")])

    if not DATA_DIR.exists():
        create_short_dataset(all_files, target_count=TARGET_PER_CLASS)
    else:
        print(f"--- Folder '{DATA_DIR}' already exists. Skipping sorting. ---")
