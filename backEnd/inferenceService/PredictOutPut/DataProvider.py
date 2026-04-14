"""
DataProvider.py
---------------
CLI test script: runs inference on 30 malignant + 30 benign LIDC-IDRI cases,
calls the local FastAPI /analyze endpoint, and writes results to
PredictOutPut/PredicationOutPut.md.

Usage (inference service must be running on port 8001):
    python DataProvider.py [--url http://127.0.0.1:8001] [--output PredicationOutPut.md]
"""

import argparse
import os
import sys
import datetime
import requests

# ---------------------------------------------------------------------------
# Case lists — first 30 from each source file
# ---------------------------------------------------------------------------

MALIGNANT_CASES = [
    "LIDC-IDRI-0001",
    "LIDC-IDRI-0002",
    "LIDC-IDRI-0003",
    "LIDC-IDRI-0004",
    "LIDC-IDRI-0005",
    "LIDC-IDRI-0006",
    "LIDC-IDRI-0007",
    "LIDC-IDRI-0009",
    "LIDC-IDRI-0010",
    "LIDC-IDRI-0011",
    "LIDC-IDRI-0012",
    "LIDC-IDRI-0013",
    "LIDC-IDRI-0015",
    "LIDC-IDRI-0017",
    "LIDC-IDRI-0019",
    "LIDC-IDRI-0020",
    "LIDC-IDRI-0021",
    "LIDC-IDRI-0022",
    "LIDC-IDRI-0023",
    "LIDC-IDRI-0024",
    "LIDC-IDRI-0025",
    "LIDC-IDRI-0026",
    "LIDC-IDRI-0027",
    "LIDC-IDRI-0031",
    "LIDC-IDRI-0033",
    "LIDC-IDRI-0034",
    "LIDC-IDRI-0035",
    "LIDC-IDRI-0037",
    "LIDC-IDRI-0038",
    "LIDC-IDRI-0039",
]

BENIGN_CASES = [
    # Section 1 — has nodules ≥3mm but all rated benign
    "LIDC-IDRI-0265",
    # Section 2 — no nodules ≥3mm (first 29 to reach total of 30)
    "LIDC-IDRI-0028",
    "LIDC-IDRI-0032",
    "LIDC-IDRI-0062",
    "LIDC-IDRI-0071",
    "LIDC-IDRI-0100",
    "LIDC-IDRI-0143",
    "LIDC-IDRI-0174",
    "LIDC-IDRI-0189",
    "LIDC-IDRI-0197",
    "LIDC-IDRI-0205",
    "LIDC-IDRI-0214",
    "LIDC-IDRI-0218",
    "LIDC-IDRI-0224",
    "LIDC-IDRI-0225",
    "LIDC-IDRI-0226",
    "LIDC-IDRI-0239",
    "LIDC-IDRI-0253",
    "LIDC-IDRI-0261",
    "LIDC-IDRI-0279",
    "LIDC-IDRI-0293",
    "LIDC-IDRI-0295",
    "LIDC-IDRI-0300",
    "LIDC-IDRI-0301",
    "LIDC-IDRI-0302",
    "LIDC-IDRI-0303",
    "LIDC-IDRI-0304",
    "LIDC-IDRI-0305",
    "LIDC-IDRI-0306",
    "LIDC-IDRI-0307",
]

NIFTI_DIR = "/media/neov/NewDisk/NewDownload/ALLNewDicomNifit"
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "DataProviderOutPut.md")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def nifti_path(case_id: str) -> str:
    return os.path.join(NIFTI_DIR, f"{case_id}_CT.nii.gz")


def analyze(url: str, filepath: str) -> dict:
    """POST file to /analyze and return the JSON response dict."""
    with open(filepath, "rb") as f:
        filename = os.path.basename(filepath)
        resp = requests.post(
            f"{url}/analyze",
            files={"file": (filename, f, "application/gzip")},
            timeout=300,
        )
    resp.raise_for_status()
    return resp.json()


def check_health(url: str) -> bool:
    try:
        r = requests.get(f"{url}/health", timeout=10)
        data = r.json()
        return data.get("model_loaded", False)
    except Exception as e:
        print(f"[health] {e}")
        return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="DataProvider — batch inference CLI test")
    parser.add_argument("--url", default="http://127.0.0.1:8001", help="Inference service base URL")
    parser.add_argument("--output", default=OUTPUT_PATH, help="Output markdown file path")
    args = parser.parse_args()

    print(f"[DataProvider] Service URL : {args.url}")
    print(f"[DataProvider] Output file : {args.output}")
    print(f"[DataProvider] NIfTI dir   : {NIFTI_DIR}")
    print()

    # Health check
    print("[DataProvider] Checking service health …")
    if not check_health(args.url):
        print("[ERROR] Inference service is not reachable or model is not loaded.")
        print("        Start it with:  uvicorn app:app --reload --port 8001")
        sys.exit(1)
    print("[DataProvider] Service is up and model is loaded.\n")

    # Build unified job list: (case_id, ground_truth_label)
    jobs = [(cid, "Malignancy") for cid in MALIGNANT_CASES] + \
           [(cid, "Benign")     for cid in BENIGN_CASES]

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
            continue
        except Exception as e:
            print(f"  error: {e}")
            skipped.append((case_id, gt_label, str(e)))
            continue

        prediction   = out.get("prediction", "?")
        confidence   = out.get("confidence", 0.0)
        prob_benign  = out.get("prob_benign", 0.0)
        prob_mal     = out.get("prob_malignancy", 0.0)
        correct      = prediction == gt_label

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

    # ------------------------------------------------------------------
    # Write markdown output
    # ------------------------------------------------------------------
    write_markdown(args.output, results, skipped)
    print(f"\n[DataProvider] Results written to {args.output}")


def write_markdown(output_path: str, results: list, skipped: list):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    # Summary stats
    total_run   = len(results)
    correct     = sum(1 for r in results if r["correct"])
    wrong       = total_run - correct
    accuracy    = correct / total_run if total_run > 0 else 0.0

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

    lines = []
    lines.append(f"# Batch Inference Results — DataProvider")
    lines.append(f"")
    lines.append(f"_Generated: {now}_")
    lines.append(f"")
    lines.append(f"**Dataset:** LIDC-IDRI  |  **Cases run:** {total_run}  |  **Skipped:** {len(skipped)}")
    lines.append(f"")

    # Summary table
    lines.append(f"## Summary")
    lines.append(f"")
    lines.append(f"| Metric | Value |")
    lines.append(f"|--------|-------|")
    lines.append(f"| Total cases run | {total_run} |")
    lines.append(f"| Correct predictions | {correct} |")
    lines.append(f"| Wrong predictions | {wrong} |")
    lines.append(f"| **Overall Accuracy** | **{accuracy:.1%}** |")
    lines.append(f"| True Positives (TP) | {tp} |")
    lines.append(f"| True Negatives (TN) | {tn} |")
    lines.append(f"| False Positives (FP) | {fp} |")
    lines.append(f"| False Negatives (FN) | {fn} |")
    lines.append(f"| **Sensitivity (Recall)** | **{sensitivity:.1%}** |")
    lines.append(f"| **Specificity** | **{specificity:.1%}** |")
    lines.append(f"| **Precision** | **{precision:.1%}** |")
    lines.append(f"| **F1 Score** | **{f1:.3f}** |")
    lines.append(f"")

    # Confusion matrix (2×2)
    lines.append(f"## Confusion Matrix")
    lines.append(f"")
    lines.append(f"|  | Predicted Malignant | Predicted Benign |")
    lines.append(f"|--|:-------------------:|:----------------:|")
    lines.append(f"| **Actual Malignant** | {tp} (TP) | {fn} (FN) |")
    lines.append(f"| **Actual Benign**    | {fp} (FP) | {tn} (TN) |")
    lines.append(f"")

    # Full results table — malignant
    lines.append(f"## Malignant Cases ({len(mal_results)} / 30)")
    lines.append(f"")
    lines.append(f"| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |")
    lines.append(f"|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|")
    for i, r in enumerate(mal_results, 1):
        mark = "✓" if r["correct"] else "✗"
        lines.append(
            f"| {i} | {r['case_id']} | {r['ground_truth']} | {r['prediction']} | {mark} "
            f"| {r['confidence']:.1%} | {r['prob_mal']:.3f} | {r['prob_benign']:.3f} |"
        )
    lines.append(f"")

    # Full results table — benign
    lines.append(f"## Benign Cases ({len(ben_results)} / 30)")
    lines.append(f"")
    lines.append(f"| # | Case ID | Ground Truth | Prediction | Correct | Confidence | P(Malignant) | P(Benign) |")
    lines.append(f"|---|---------|:------------:|:----------:|:-------:|:----------:|:------------:|:---------:|")
    for i, r in enumerate(ben_results, 1):
        mark = "✓" if r["correct"] else "✗"
        lines.append(
            f"| {i} | {r['case_id']} | {r['ground_truth']} | {r['prediction']} | {mark} "
            f"| {r['confidence']:.1%} | {r['prob_mal']:.3f} | {r['prob_benign']:.3f} |"
        )
    lines.append(f"")

    # Skipped cases
    if skipped:
        lines.append(f"## Skipped Cases ({len(skipped)})")
        lines.append(f"")
        lines.append(f"| Case ID | Ground Truth | Reason |")
        lines.append(f"|---------|:------------:|--------|")
        for (cid, gt, reason) in skipped:
            lines.append(f"| {cid} | {gt} | {reason} |")
        lines.append(f"")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
