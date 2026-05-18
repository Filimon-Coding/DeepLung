"""
DataProvider.py  (underdev4)
-----------------------------
CLI test script: runs inference on 30 malignant + 30 benign LIDC-IDRI cases,
calls the local FastAPI /analyze endpoint on port 8002, and writes results to
PredictOutPut/DataProviderOutPut<timestamp>.md.

Usage (underdev4 service must be running on port 8002):
    python DataProvider.py [--url http://127.0.0.1:8002] [--output DataProviderOutPut.md]
"""

import argparse
import os
import sys
import time
import datetime
import requests

# ---------------------------------------------------------------------------
# Case lists — unseen cases (not in training or test split)
# Labels derived from underdev3/list3.2.csv:
#   in CSV  → Malignancy (confirmed malignant nodule)
#   not in CSV → Benign (no malignant nodule)
# ---------------------------------------------------------------------------

MALIGNANT_CASES = [
    "LIDC-IDRI-0106",
    "LIDC-IDRI-0132",
    "LIDC-IDRI-0158",
    "LIDC-IDRI-0184",
    "LIDC-IDRI-0212",
    "LIDC-IDRI-0244",
    "LIDC-IDRI-0271",
    "LIDC-IDRI-0299",
    "LIDC-IDRI-0329",
    "LIDC-IDRI-0360",
    "LIDC-IDRI-0390",
    "LIDC-IDRI-0420",
    "LIDC-IDRI-0450",
    "LIDC-IDRI-0478",
    "LIDC-IDRI-0504",
    "LIDC-IDRI-0538",
    "LIDC-IDRI-0568",
    "LIDC-IDRI-0598",
    "LIDC-IDRI-0631",
    "LIDC-IDRI-0660",
    "LIDC-IDRI-0695",
    "LIDC-IDRI-0724",
    "LIDC-IDRI-0754",
    "LIDC-IDRI-0783",
    "LIDC-IDRI-0811",
    "LIDC-IDRI-0836",
    "LIDC-IDRI-0864",
    "LIDC-IDRI-0898",
    "LIDC-IDRI-0929",
    "LIDC-IDRI-0962",
]

BENIGN_CASES = [
    "LIDC-IDRI-0746",
    "LIDC-IDRI-0755",
    "LIDC-IDRI-0760",
    "LIDC-IDRI-0764",
    "LIDC-IDRI-0774",
    "LIDC-IDRI-0784",
    "LIDC-IDRI-0804",
    "LIDC-IDRI-0808",
    "LIDC-IDRI-0839",
    "LIDC-IDRI-0853",
    "LIDC-IDRI-0862",
    "LIDC-IDRI-0876",
    "LIDC-IDRI-0877",
    "LIDC-IDRI-0878",
    "LIDC-IDRI-0881",
    "LIDC-IDRI-0885",
    "LIDC-IDRI-0887",
    "LIDC-IDRI-0889",
    "LIDC-IDRI-0891",
    "LIDC-IDRI-0897",
    "LIDC-IDRI-0900",
    "LIDC-IDRI-0901",
    "LIDC-IDRI-0903",
    "LIDC-IDRI-0906",
    "LIDC-IDRI-0918",
    "LIDC-IDRI-0927",
    "LIDC-IDRI-0930",
    "LIDC-IDRI-0931",
    "LIDC-IDRI-0934",
    "LIDC-IDRI-0937",
]

NIFTI_DIR = "/media/neov/NewDisk/NewDownload/ALLNewDicomNifit"
_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), f"DataProviderOutPut{_ts}.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def nifti_path(case_id: str) -> str:
    return os.path.join(NIFTI_DIR, f"{case_id}_CT.nii.gz")


def analyze(url: str, filepath: str, retries: int = 3, retry_delay: int = 15) -> dict:
    for attempt in range(1, retries + 1):
        try:
            with open(filepath, "rb") as f:
                resp = requests.post(
                    f"{url}/analyze",
                    files={"file": (os.path.basename(filepath), f, "application/gzip")},
                    timeout=300,
                )
            resp.raise_for_status()
            return resp.json()
        except (requests.HTTPError, requests.ConnectionError, requests.Timeout) as e:
            if attempt < retries:
                print(f"\n  [retry {attempt}/{retries}] {e} — waiting {retry_delay}s for service recovery …", end="", flush=True)
                time.sleep(retry_delay)
            else:
                raise


def check_health(url: str) -> bool:
    try:
        r = requests.get(f"{url}/health", timeout=10)
        data = r.json()
        return data.get("model_loaded", False)
    except Exception as e:
        print(f"[health] {e}")
        return False


def wait_for_recovery(url: str, max_wait: int = 120) -> bool:
    """Poll /health until the service is back up, or give up after max_wait seconds."""
    print(f"\n  [recovery] Waiting for service to recover (max {max_wait}s) …", end="", flush=True)
    deadline = time.time() + max_wait
    while time.time() < deadline:
        time.sleep(5)
        if check_health(url):
            print(" back online.")
            return True
        print(".", end="", flush=True)
    print(" gave up.")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DataProvider (underdev4) — batch inference CLI test")
    parser.add_argument("--url", default="http://127.0.0.1:8002", help="Inference service base URL")
    parser.add_argument("--output", default=OUTPUT_PATH, help="Output markdown file path")
    args = parser.parse_args()

    print(f"[DataProvider] Service URL : {args.url}")
    print(f"[DataProvider] Output file : {args.output}")
    print(f"[DataProvider] NIfTI dir   : {NIFTI_DIR}")
    print()

    print("[DataProvider] Checking service health …")
    if not check_health(args.url):
        print("[ERROR] Inference service is not reachable or model is not loaded.")
        print("        Start it with:  cd underdev4 && uvicorn app:app --reload --port 8002")
        sys.exit(1)
    print("[DataProvider] Service is up and model is loaded.\n")

    jobs = (
        [(cid, "Malignancy") for cid in MALIGNANT_CASES] +
        [(cid, "Benign")     for cid in BENIGN_CASES]
    )

    results = []
    skipped = []

    total = len(jobs)
    for idx, (case_id, gt_label) in enumerate(jobs, 1):
        path = nifti_path(case_id)
        prefix = f"[{idx:02d}/{total}] {case_id} (GT={gt_label})"

        if not os.path.isfile(path):
            print(f"{prefix}  →  FILE NOT FOUND, skipping")
            skipped.append((case_id, gt_label, "file not found"))
            continue

        print(f"{prefix}  →  sending …", end="", flush=True)
        try:
            out = analyze(args.url, path)
        except requests.HTTPError as e:
            print(f"  HTTP error: {e}")
            skipped.append((case_id, gt_label, f"HTTP {e.response.status_code}"))
            wait_for_recovery(args.url)
            continue
        except Exception as e:
            print(f"  error: {e}")
            skipped.append((case_id, gt_label, str(e)))
            wait_for_recovery(args.url)
            continue

        time.sleep(1)

        prediction  = out.get("prediction", "?")
        confidence  = out.get("confidence", 0.0)
        prob_benign = out.get("prob_benign", 0.0)
        prob_mal    = out.get("prob_malignancy", 0.0)
        correct     = prediction == gt_label

        results.append({
            "case_id":      case_id,
            "ground_truth": gt_label,
            "prediction":   prediction,
            "confidence":   confidence,
            "prob_benign":  prob_benign,
            "prob_mal":     prob_mal,
            "correct":      correct,
        })

        mark = "✓" if correct else "✗"
        print(f"  {mark}  pred={prediction}  conf={confidence:.1%}  "
              f"p_mal={prob_mal:.3f}  p_ben={prob_benign:.3f}")

    write_markdown(args.output, results, skipped)
    print(f"\n[DataProvider] Results written to {args.output}")


def write_markdown(output_path: str, results: list, skipped: list):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    total_run = len(results)
    correct   = sum(1 for r in results if r["correct"])
    wrong     = total_run - correct
    accuracy  = correct / total_run if total_run > 0 else 0.0

    mal_results = [r for r in results if r["ground_truth"] == "Malignancy"]
    ben_results = [r for r in results if r["ground_truth"] == "Benign"]

    tp = sum(1 for r in mal_results if r["prediction"] == "Malignancy")
    fn = sum(1 for r in mal_results if r["prediction"] != "Malignancy")
    tn = sum(1 for r in ben_results if r["prediction"] == "Benign")
    fp = sum(1 for r in ben_results if r["prediction"] != "Benign")

    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision   = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    f1          = (2 * precision * sensitivity / (precision + sensitivity)
                   if (precision + sensitivity) > 0 else 0.0)

    lines = [
        f"# Batch Inference Results — underdev4 (MedicalNet ResNet-18)",
        f"",
        f"_Generated: {now}_",
        f"",
        f"**Dataset:** LIDC-IDRI  |  **Cases run:** {total_run}  |  **Skipped:** {len(skipped)}",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Value |",
        f"|--------|-------|",
        f"| Total cases run | {total_run} |",
        f"| Correct predictions | {correct} |",
        f"| Wrong predictions | {wrong} |",
        f"| **Overall Accuracy** | **{accuracy:.1%}** |",
        f"| True Positives (TP) | {tp} |",
        f"| True Negatives (TN) | {tn} |",
        f"| False Positives (FP) | {fp} |",
        f"| False Negatives (FN) | {fn} |",
        f"| **Sensitivity (Recall)** | **{sensitivity:.1%}** |",
        f"| **Specificity** | **{specificity:.1%}** |",
        f"| **Precision** | **{precision:.1%}** |",
        f"| **F1 Score** | **{f1:.3f}** |",
        f"",
        f"## Confusion Matrix",
        f"",
        f"|  | Predicted Malignant | Predicted Benign |",
        f"|--|:-------------------:|:----------------:|",
        f"| **Actual Malignant** | {tp} (TP) | {fn} (FN) |",
        f"| **Actual Benign**    | {fp} (FP) | {tn} (TN) |",
        f"",
        f"## Malignant Cases ({len(mal_results)} / 30)",
        f"",
        f"| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |",
        f"|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|",
    ]
    for i, r in enumerate(mal_results, 1):
        mark = "✓" if r["correct"] else "✗"
        lines.append(
            f"| {i} | {r['case_id']} | {r['ground_truth']} | {r['prediction']} | {mark} "
            f"| {r['confidence']:.1%} | {r['prob_mal']:.3f} | {r['prob_benign']:.3f} |"
        )

    lines += [
        f"",
        f"## Benign Cases ({len(ben_results)} / 30)",
        f"",
        f"| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |",
        f"|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|",
    ]
    for i, r in enumerate(ben_results, 1):
        mark = "✓" if r["correct"] else "✗"
        lines.append(
            f"| {i} | {r['case_id']} | {r['ground_truth']} | {r['prediction']} | {mark} "
            f"| {r['confidence']:.1%} | {r['prob_mal']:.3f} | {r['prob_benign']:.3f} |"
        )
    lines.append(f"")

    if skipped:
        lines += [
            f"## Skipped Cases ({len(skipped)})",
            f"",
            f"| Case ID | Ground Truth | Reason |",
            f"|---------|:------------:|--------|",
        ]
        for (cid, gt, reason) in skipped:
            lines.append(f"| {cid} | {gt} | {reason} |")
        lines.append(f"")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
