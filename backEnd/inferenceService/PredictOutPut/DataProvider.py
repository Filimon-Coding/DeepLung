"""
DataProvider.py
---------------
CLI test script: runs inference on 80 malignant + 80 benign LIDC-IDRI cases,
calls the local FastAPI /analyze endpoint, and writes results to a timestamped
PredictOutPut/DataProviderOutPut_<YYYYMMDD_HHMM>.md file.

Case pools are loaded from:
  - malignantCases.md  (257 confirmed-malignant cases, radiologist score >= 4)
  - benignCases.md     (734 confirmed-benign cases, all scores <= 2 / no nodule >= 3 mm)

80 cases are randomly sampled from each pool per run.
Cases not found on disk are reported in the Skipped section.

Usage (inference service must be running on port 8001):
    python DataProvider.py [--url http://127.0.0.1:8001] [--output <path>] [--seed <int>]
"""

import argparse
import os
import re
import sys
import random
import datetime
import requests

SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
NIFTI_DIR   = "/media/neov/NewDisk/NewDownload/ALLNewDicomNifit"
SAMPLE_SIZE = 10

_ts = datetime.datetime.now().strftime("%Y%m%d_%H%M")
OUTPUT_PATH = os.path.join(SCRIPT_DIR, f"DataProviderOutPut{_ts}.md")


# ---------------------------------------------------------------------------
# Pool loaders — parse LIDC-IDRI-XXXX IDs from the companion markdown files
# ---------------------------------------------------------------------------

def load_cases_from_md(md_path: str) -> list:
    """Return deduplicated list of LIDC-IDRI-XXXX case IDs found in *md_path*."""
    pattern = re.compile(r"LIDC-IDRI-\d{4}")
    seen = set()
    cases = []
    with open(md_path, encoding="utf-8") as f:
        for line in f:
            if not line.startswith("|"):
                continue
            for cid in pattern.findall(line):
                if cid not in seen:
                    seen.add(cid)
                    cases.append(cid)
    return cases


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
    parser.add_argument("--url",    default="http://127.0.0.1:8001", help="Inference service base URL")
    parser.add_argument("--output", default=OUTPUT_PATH,             help="Output markdown file path")
    parser.add_argument("--seed",   type=int, default=None,          help="Random seed for reproducibility")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print(f"[DataProvider] Service URL : {args.url}")
    print(f"[DataProvider] Output file : {args.output}")
    print(f"[DataProvider] NIfTI dir   : {NIFTI_DIR}")
    print(f"[DataProvider] Sample size : {SAMPLE_SIZE} per class")
    print()

    # Load pools from companion MD files
    mal_md  = os.path.join(SCRIPT_DIR, "newMalignant.md")
    ben_md  = os.path.join(SCRIPT_DIR, "newBenign.md")

    for path, _ in [(mal_md, "malignantCases.md"), (ben_md, "benignCases.md")]:
        if not os.path.isfile(path):
            print(f"[ERROR] Pool file not found: {path}")
            sys.exit(1)

    mal_pool = load_cases_from_md(mal_md)
    ben_pool = load_cases_from_md(ben_md)

    print(f"[DataProvider] Malignant pool : {len(mal_pool)} cases")
    print(f"[DataProvider] Benign pool    : {len(ben_pool)} cases")

    random.shuffle(mal_pool)
    random.shuffle(ben_pool)

    mal_sample = mal_pool[:SAMPLE_SIZE]
    ben_sample = ben_pool[:SAMPLE_SIZE]

    print(f"[DataProvider] Selected       : {len(mal_sample)} malignant + {len(ben_sample)} benign\n")

    # Health check
    print("[DataProvider] Checking service health ...")
    if not check_health(args.url):
        print("[ERROR] Inference service is not reachable or model is not loaded.")
        print("        Start it with:  uvicorn app:app --reload --port 8001")
        sys.exit(1)
    print("[DataProvider] Service is up and model is loaded.\n")

    # Build unified job list
    jobs = [(cid, "Malignancy") for cid in mal_sample] + \
           [(cid, "Benign")     for cid in ben_sample]

    results = []
    skipped = []

    total = len(jobs)
    for idx, (case_id, gt_label) in enumerate(jobs, 1):
        path = nifti_path(case_id)
        prefix = f"[{idx:03d}/{total}] {case_id} (GT={gt_label})"

        if not os.path.isfile(path):
            print(f"{prefix}  →  FILE NOT FOUND, skipping")
            skipped.append((case_id, gt_label, "file not found"))
            continue

        print(f"{prefix}  →  sending ...", end="", flush=True)
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

    lines = []
    lines.append(f"# Batch Inference Results — DataProvider")
    lines.append(f"")
    lines.append(f"_Generated: {now}_")
    lines.append(f"")
    lines.append(f"**Dataset:** LIDC-IDRI  |  **Target:** {SAMPLE_SIZE} malignant + {SAMPLE_SIZE} benign  "
                 f"|  **Cases run:** {total_run}  |  **Skipped:** {len(skipped)}")
    lines.append(f"")

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

    lines.append(f"## Confusion Matrix")
    lines.append(f"")
    lines.append(f"|  | Predicted Malignant | Predicted Benign |")
    lines.append(f"|--|:-------------------:|:----------------:|")
    lines.append(f"| **Actual Malignant** | {tp} (TP) | {fn} (FN) |")
    lines.append(f"| **Actual Benign**    | {fp} (FP) | {tn} (TN) |")
    lines.append(f"")

    lines.append(f"## Malignant Cases ({len(mal_results)} / {SAMPLE_SIZE})")
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

    lines.append(f"## Benign Cases ({len(ben_results)} / {SAMPLE_SIZE})")
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
