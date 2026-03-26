"""
run_lidc_batch.py
-----------------
CLI batch runner that converts all LIDC-IDRI patients using dicom_converter.

Usage
-----
    python run_lidc_batch.py \
        --dataset /media/neov/NewDisk/NewDownload/manifest-1600709154662/LIDC-IDRI \
        --output  ./nifti_output \
        --workers 4 \
        --limit   10          # omit to process all 1012 patients

Each patient can have multiple CT series (different reconstructions). This
script converts ALL series per patient and names the output files:
    <output>/<patient_id>_<series_uid_short>.nii.gz

A summary CSV is written to <output>/conversion_summary.csv.
"""

import argparse
import csv
import logging
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from dicom_converter import ConversionResult, SeriesInfo, convert_series, discover_series

# ---------------------------------------------------------------------------
# Logging — structured so a web app can attach its own handler
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Worker function (runs in a subprocess when workers > 1)
# ---------------------------------------------------------------------------

def _convert_one(args: tuple) -> dict:
    """
    Top-level function (must be picklable for multiprocessing).
    Returns a plain dict so it crosses the process boundary cleanly.
    """
    patient_id, series_info, output_dir = args

    uid_short = series_info.series_uid[-8:]
    out_name  = f"{patient_id}_{uid_short}.nii.gz"
    out_path  = os.path.join(output_dir, out_name)

    # Skip if already converted (resume-friendly)
    if os.path.exists(out_path):
        logger.info("SKIP  %s — already exists", out_name)
        return {
            "patient_id": patient_id,
            "series_uid": series_info.series_uid,
            "output_file": out_name,
            "status": "skipped",
            "shape": "",
            "voxel_size_mm": "",
            "warnings": "",
            "error": "",
        }

    result: ConversionResult = convert_series(
        dicom_dir=series_info.folder,
        output_path=out_path,
    )

    return {
        "patient_id": patient_id,
        "series_uid": series_info.series_uid,
        "output_file": out_name if result.success else "",
        "status": "ok" if result.success else "failed",
        "shape": str(result.shape),
        "voxel_size_mm": str(result.voxel_size_mm),
        "warnings": " | ".join(result.warnings),
        "error": result.error,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Batch DICOM→NIfTI for LIDC-IDRI")
    parser.add_argument("--dataset", required=True, help="Path to LIDC-IDRI root folder")
    parser.add_argument("--output",  required=True, help="Output directory for .nii.gz files")
    parser.add_argument("--workers", type=int, default=1,
                        help="Parallel worker processes (default 1 — safe for low RAM)")
    parser.add_argument("--limit",   type=int, default=None,
                        help="Stop after N patients (useful for testing)")
    parser.add_argument("--min-slices", type=int, default=10,
                        help="Minimum slices to treat a series as a CT volume")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    summary_path = os.path.join(args.output, "conversion_summary.csv")

    # ---- Discover all patients ----
    base = Path(args.dataset)
    patient_dirs = sorted(base.glob("LIDC-IDRI-*"))

    if args.limit:
        patient_dirs = patient_dirs[: args.limit]

    logger.info("Found %d patient folders (limit=%s)", len(patient_dirs), args.limit)

    # ---- Build job list ----
    jobs: list[tuple] = []
    for patient_dir in patient_dirs:
        patient_id = patient_dir.name
        series_list = discover_series(str(patient_dir), min_slices=args.min_slices)
        if not series_list:
            logger.warning("No convertible series found for %s", patient_id)
            continue
        logger.info(
            "%s — %d series: %s",
            patient_id,
            len(series_list),
            [f"{s.modality}({s.file_count})" for s in series_list],
        )
        for series in series_list:
            jobs.append((patient_id, series, args.output))

    logger.info("Total conversion jobs: %d", len(jobs))

    # ---- Run jobs ----
    rows: list[dict] = []

    if args.workers > 1:
        with ProcessPoolExecutor(max_workers=args.workers) as pool:
            futures = {pool.submit(_convert_one, job): job for job in jobs}
            for fut in as_completed(futures):
                row = fut.result()
                rows.append(row)
                status = row["status"].upper()
                logger.info("[%s] %s / %s", status, row["patient_id"], row["output_file"] or row["error"])
    else:
        for job in jobs:
            row = _convert_one(job)
            rows.append(row)
            status = row["status"].upper()
            logger.info("[%s] %s / %s", status, row["patient_id"], row["output_file"] or row["error"])

    # ---- Write summary CSV ----
    if rows:
        with open(summary_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

    # ---- Print summary ----
    ok      = sum(1 for r in rows if r["status"] == "ok")
    skipped = sum(1 for r in rows if r["status"] == "skipped")
    failed  = sum(1 for r in rows if r["status"] == "failed")

    logger.info("=" * 60)
    logger.info("Done.  ok=%d  skipped=%d  failed=%d", ok, skipped, failed)
    logger.info("Summary CSV: %s", os.path.abspath(summary_path))

    # List output files
    nii_files = sorted(Path(args.output).glob("*.nii*"))
    logger.info("Output files (%d):", len(nii_files))
    for f in nii_files:
        size_mb = f.stat().st_size / (1024 ** 2)
        logger.info("  %-50s  %6.1f MB", f.name, size_mb)


if __name__ == "__main__":
    main()
