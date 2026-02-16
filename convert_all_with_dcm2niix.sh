#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# INPUT + OUTPUT (absolute)
# ----------------------------
BASE="/media/neov/NewDisk/NewDownload/manifest-1600709154662/LIDC-IDRI"
OUT="/media/neov/NewDisk/NewDownload/nifti_output_usingDcm2niixx"

mkdir -p "$OUT"

echo "BASE: $BASE"
echo "OUT : $OUT"
echo

# ----------------------------
# Loop through patients
# ----------------------------
for patient_dir in "$BASE"/LIDC-IDRI-*; do
  patient_id="$(basename "$patient_dir")"

  # ----------------------------
  # Pick series folder with most .dcm files (NULL-safe for spaces)
  # ----------------------------
  best_series_dir="$(
    find "$patient_dir" -type f -name "*.dcm" -printf '%h\0' \
      | sort -z \
      | uniq -z -c \
      | sort -z -nr \
      | head -z -n 1 \
      | sed -z 's/^[[:space:]]*[0-9]\+[[:space:]]*//' \
      | tr -d '\0'
  )"

  if [ -z "$best_series_dir" ]; then
    echo "Skipping $patient_id (no .dcm files found)"
    echo
    continue
  fi

  echo "Converting $patient_id"
  echo "  Series: $best_series_dir"

  # If output already exists, skip (optional but helpful)
  if [ -f "$OUT/${patient_id}_CT.nii.gz" ]; then
    echo "  Already exists, skipping: $OUT/${patient_id}_CT.nii.gz"
    echo
    continue
  fi

  # ----------------------------
  # Convert using dcm2niix
  # ----------------------------
  # Don't let one failure stop everything
  if dcm2niix -z y -o "$OUT" -f "${patient_id}_CT" "$best_series_dir" >/dev/null 2>&1; then
    if [ -f "$OUT/${patient_id}_CT.nii.gz" ]; then
      echo "  Saved: $OUT/${patient_id}_CT.nii.gz"
    else
      echo "  Warning: dcm2niix ran but output not found for $patient_id"
    fi
  else
    echo "  ERROR: dcm2niix failed for $patient_id"
    echo "  (Check series folder manually if needed)"
  fi

  echo
done

echo "Done. Output folder: $OUT"
