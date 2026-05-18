BASE="/media/neov/NewDisk/NewDownload/manifest-1600709154662/LIDC-IDRI"
OUT="/media/neov/NewDisk/NewDownload/nifti_output_usingDcm2niixx"
patient_dir="$BASE/LIDC-IDRI-0086"
patient_id="LIDC-IDRI-0086"

best_series_dir="$(
  find "$patient_dir" -type f -name "*.dcm" -printf '%h\0' \
  | sort -z | uniq -z -c | sort -z -nr | head -z -n 1 \
  | sed -z 's/^[[:space:]]*[0-9]\+[[:space:]]*//' | tr -d '\0'
)"

echo "$best_series_dir"
dcm2niix -z y -o "$OUT" -f "${patient_id}_CT" "$best_series_dir"
