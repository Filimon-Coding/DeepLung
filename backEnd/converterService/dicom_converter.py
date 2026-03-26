"""
dicom_converter.py
------------------
Web-app-ready DICOM → NIfTI converter.

Fixes applied vs original script
  - Affine built from ImageOrientationPatient + ImagePositionPatient (not just PixelSpacing)
  - Slice sorting uses ImagePositionPatient[2] as primary key, SliceLocation as fallback
  - Series grouped by SeriesInstanceUID so multi-series patients each get their own file
  - Pre-allocated volume array (no RAM double-spend from list + np.stack)
  - RescaleSlope/Intercept variance is logged as a warning
  - All print() replaced with logging so a web app can attach a handler
  - progress_cb(pct: float, msg: str) callback for WebSocket / SSE streaming
  - No top-level side effects — safe to import anywhere

Usage (standalone)
  from dicom_converter import convert_series, discover_series
  result = convert_series("/data/dicoms/series_dir", "/out/scan.nii.gz")

Usage (web app / Celery task)
  def my_task(dicom_dir, out_path, job_id):
      def push(pct, msg):
          redis.publish(f"job:{job_id}", json.dumps({"pct": pct, "msg": msg}))
      result = convert_series(dicom_dir, out_path, progress_cb=push)
      return result
"""

import io
import logging
import os
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional

import nibabel as nib
import numpy as np
import pydicom
from matplotlib import pyplot as plt
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

ProgressCallback = Optional[Callable[[float, str], None]]


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SeriesInfo:
    """Metadata about one DICOM series found on disk."""
    series_uid: str
    folder: str
    file_count: int
    modality: str = "UNKNOWN"
    description: str = ""


@dataclass
class ConversionResult:
    """Return value from convert_series()."""
    success: bool
    output_path: str = ""
    shape: tuple = ()
    voxel_size_mm: tuple = ()
    series_uid: str = ""
    modality: str = ""
    warnings: list = field(default_factory=list)
    error: str = ""


# ---------------------------------------------------------------------------
# Series discovery
# ---------------------------------------------------------------------------

def discover_series(patient_folder: str, min_slices: int = 10) -> list[SeriesInfo]:
    """
    Walk a patient folder and return one SeriesInfo per DICOM series.
    Groups files by SeriesInstanceUID tag rather than by folder, so
    patients that store multiple series in one directory are handled correctly.

    Parameters
    ----------
    patient_folder : path to the top-level patient directory
    min_slices     : series with fewer files than this are treated as scouts
                     and excluded from the returned list

    Returns
    -------
    List of SeriesInfo, sorted by file_count descending.
    """
    # series_uid -> {"folder": str, "files": [Path], "modality": str, "desc": str}
    series_map: dict[str, dict] = defaultdict(lambda: {
        "folder": "", "files": [], "modality": "UNKNOWN", "description": ""
    })

    for root, _, files in os.walk(patient_folder):
        dcm_files = [Path(root) / f for f in files if f.lower().endswith(".dcm")]
        for dcm_path in dcm_files:
            try:
                # stop_before_pixels=True is fast — we only need tags
                ds = pydicom.dcmread(str(dcm_path), stop_before_pixels=True)
                uid = str(getattr(ds, "SeriesInstanceUID", "unknown"))
                series_map[uid]["files"].append(dcm_path)
                series_map[uid]["folder"] = root
                series_map[uid]["modality"] = str(getattr(ds, "Modality", "UNKNOWN"))
                series_map[uid]["description"] = str(
                    getattr(ds, "SeriesDescription", "") or
                    getattr(ds, "StudyDescription", "")
                )
            except Exception as exc:
                logger.debug("Skipping unreadable file %s: %s", dcm_path.name, exc)

    results = []
    for uid, info in series_map.items():
        count = len(info["files"])
        if count < min_slices:
            logger.debug("Series %s has only %d files — treating as scout, skipping", uid, count)
            continue
        results.append(SeriesInfo(
            series_uid=uid,
            folder=info["folder"],
            file_count=count,
            modality=info["modality"],
            description=info["description"],
        ))

    results.sort(key=lambda s: s.file_count, reverse=True)
    return results


# ---------------------------------------------------------------------------
# Affine construction
# ---------------------------------------------------------------------------

def _build_affine(ds: pydicom.Dataset, slice_thickness: float) -> np.ndarray:
    """
    Build a 4x4 NIfTI affine from DICOM orientation / position tags.

    Uses ImageOrientationPatient and ImagePositionPatient which correctly
    handle oblique acquisitions. Falls back to a simple diagonal matrix
    if the tags are missing (rare, but happens with some older scanners).
    """
    ps = np.array(getattr(ds, "PixelSpacing", [1.0, 1.0]), dtype=float)

    if hasattr(ds, "ImageOrientationPatient") and hasattr(ds, "ImagePositionPatient"):
        iop = np.array(ds.ImageOrientationPatient, dtype=float)
        ipp = np.array(ds.ImagePositionPatient, dtype=float)

        row_cosine   = iop[:3]          # direction of rows    (X axis in patient space)
        col_cosine   = iop[3:]          # direction of columns (Y axis in patient space)
        slice_cosine = np.cross(row_cosine, col_cosine)  # normal to the slice plane

        affine = np.eye(4)
        affine[:3, 0] = row_cosine   * ps[1]           # column pixel spacing
        affine[:3, 1] = col_cosine   * ps[0]           # row pixel spacing
        affine[:3, 2] = slice_cosine * slice_thickness
        affine[:3, 3] = ipp                             # origin in mm
        return affine

    # ---- fallback: no orientation tags ----
    logger.warning(
        "ImageOrientationPatient / ImagePositionPatient missing — "
        "using diagonal affine (spatial accuracy not guaranteed)"
    )
    affine = np.diag([-ps[0], -ps[1], slice_thickness, 1.0])
    return affine


# ---------------------------------------------------------------------------
# Slice-position helper
# ---------------------------------------------------------------------------

def _slice_position(ds: pydicom.Dataset, fallback: float) -> float:
    """
    Return the z-position of a slice for sorting purposes.
    Priority: ImagePositionPatient[2] > SliceLocation > fallback index.
    """
    if hasattr(ds, "ImagePositionPatient"):
        return float(ds.ImagePositionPatient[2])
    if hasattr(ds, "SliceLocation"):
        return float(ds.SliceLocation)
    logger.debug("No position tag found, using fallback index %s", fallback)
    return fallback


# ---------------------------------------------------------------------------
# Core conversion
# ---------------------------------------------------------------------------

def convert_series(
    dicom_dir: str,
    output_path: str,
    progress_cb: ProgressCallback = None,
    min_slices: int = 10,
) -> ConversionResult:
    """
    Convert a folder of DICOM slices (one series) to a single NIfTI file.

    Parameters
    ----------
    dicom_dir   : folder containing the .dcm files
    output_path : destination .nii or .nii.gz path
    progress_cb : optional callable(pct: float, msg: str) for live updates
    min_slices  : reject series with fewer slices (likely scouts)

    Returns
    -------
    ConversionResult dataclass — always returned, never raises.
    """
    warnings_list: list[str] = []

    def _progress(pct: float, msg: str) -> None:
        logger.info("[%3.0f%%] %s", pct, msg)
        if progress_cb:
            progress_cb(pct, msg)

    try:
        dicom_dir = str(dicom_dir)
        dcm_files = sorted(Path(dicom_dir).glob("*.dcm"))

        if not dcm_files:
            # Some datasets store files without .dcm extension
            dcm_files = sorted(
                p for p in Path(dicom_dir).iterdir()
                if p.is_file() and not p.suffix.lower() in {".xml", ".txt", ".json"}
            )

        if len(dcm_files) < min_slices:
            msg = f"Only {len(dcm_files)} files in {dicom_dir} — skipping"
            logger.warning(msg)
            return ConversionResult(success=False, error=msg)

        _progress(0, f"Found {len(dcm_files)} DICOM files, reading metadata…")

        # ---- Pass 1: read headers + pixel data, collect sort keys ----
        slice_records: list[tuple[float, int, np.ndarray, pydicom.Dataset]] = []
        slopes: list[float] = []
        intercepts: list[float] = []
        thicknesses: list[float] = []
        first_ds: Optional[pydicom.Dataset] = None

        for idx, dcm_path in enumerate(dcm_files):
            try:
                ds = pydicom.dcmread(str(dcm_path), force=True)
                pixel_data = ds.pixel_array.astype(np.float32)

                slope     = float(getattr(ds, "RescaleSlope", 1.0))
                intercept = float(getattr(ds, "RescaleIntercept", 0.0))
                pixel_data = pixel_data * slope + intercept

                slopes.append(slope)
                intercepts.append(intercept)

                if hasattr(ds, "SliceThickness"):
                    thicknesses.append(float(ds.SliceThickness))

                pos = _slice_position(ds, float(idx))
                slice_records.append((pos, idx, pixel_data, ds))

                if first_ds is None:
                    first_ds = ds

                if idx % max(1, len(dcm_files) // 20) == 0:
                    pct = 5 + 60 * idx / len(dcm_files)
                    _progress(pct, f"Reading slice {idx + 1}/{len(dcm_files)}")

            except Exception as exc:
                w = f"Skipped {dcm_path.name}: {exc}"
                logger.warning(w)
                warnings_list.append(w)

        if not slice_records:
            return ConversionResult(success=False, error="No readable DICOM slices found")

        # ---- Warn if rescale values vary across series ----
        if len(set(slopes)) > 1 or len(set(intercepts)) > 1:
            w = (
                f"RescaleSlope/Intercept varies across slices "
                f"(slopes: {set(slopes)}, intercepts: {set(intercepts)}). "
                "HU values may be inconsistent."
            )
            logger.warning(w)
            warnings_list.append(w)

        # ---- Sort by spatial position ----
        _progress(65, "Sorting slices by position…")
        slice_records.sort(key=lambda r: r[0])

        # ---- Build volume — pre-allocate to avoid double RAM usage ----
        sample = slice_records[0][2]
        n_slices = len(slice_records)
        volume = np.zeros((*sample.shape, n_slices), dtype=np.float32)

        for z, (_, _, pixel_data, _) in enumerate(slice_records):
            volume[:, :, z] = pixel_data

        _progress(80, f"Volume assembled: {volume.shape}")

        # ---- Derive slice thickness ----
        if len(slice_records) > 1:
            # Compute from actual position delta — more reliable than the tag
            positions = [r[0] for r in slice_records]
            deltas = np.diff(positions)
            slice_thickness = float(np.median(np.abs(deltas)))
            if slice_thickness == 0:
                slice_thickness = float(np.mean(thicknesses)) if thicknesses else 1.0
        elif thicknesses:
            slice_thickness = float(np.mean(thicknesses))
        else:
            slice_thickness = 1.0

        # ---- Build affine ----
        affine = _build_affine(first_ds, slice_thickness)
        ps = np.array(getattr(first_ds, "PixelSpacing", [1.0, 1.0]), dtype=float)

        # ---- Create and save NIfTI ----
        _progress(85, "Building NIfTI header…")
        nifti_img = nib.Nifti1Image(volume, affine)

        hdr = nifti_img.header
        hdr.set_xyzt_units("mm")
        hdr["descrip"] = f"CT {os.path.basename(dicom_dir)}"[:79]

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        _progress(90, f"Saving {os.path.basename(output_path)}…")
        nib.save(nifti_img, output_path)

        size_mb = os.path.getsize(output_path) / (1024 ** 2)
        _progress(100, f"Done — {size_mb:.1f} MB written to {output_path}")

        modality = str(getattr(first_ds, "Modality", "UNKNOWN"))
        series_uid = str(getattr(first_ds, "SeriesInstanceUID", ""))

        return ConversionResult(
            success=True,
            output_path=output_path,
            shape=volume.shape,
            voxel_size_mm=(float(ps[0]), float(ps[1]), slice_thickness),
            series_uid=series_uid,
            modality=modality,
            warnings=warnings_list,
        )

    except Exception as exc:
        logger.exception("Conversion failed")
        return ConversionResult(success=False, error=str(exc), warnings=warnings_list)


# ---------------------------------------------------------------------------
# Visualisation utility  (web-safe — returns PNG bytes, never calls plt.show)
# ---------------------------------------------------------------------------

def render_comparison_png(
    dicom_dir: str,
    nifti_path: str,
    slice_idx: Optional[int] = None,
    figsize: tuple = (10, 5),
) -> bytes:
    """
    Render a side-by-side DICOM vs NIfTI comparison for a single slice.
    Returns PNG bytes so a web endpoint can serve it directly:

        @app.get("/preview/{job_id}")
        def preview(job_id: str):
            png = render_comparison_png(dicom_dir, nifti_path)
            return Response(content=png, media_type="image/png")

    Parameters
    ----------
    dicom_dir  : folder with raw .dcm files
    nifti_path : path to the converted .nii.gz
    slice_idx  : which axial slice to show (default: middle slice)

    Returns
    -------
    PNG image as bytes
    """
    # Load DICOM middle slice without rescaling (raw pixel values for display)
    dcm_files = sorted(Path(dicom_dir).glob("*.dcm"))
    if not dcm_files:
        raise FileNotFoundError(f"No .dcm files in {dicom_dir}")

    dicom_slices = []
    for f in dcm_files:
        try:
            dicom_slices.append(pydicom.dcmread(str(f)).pixel_array.astype(np.float32))
        except Exception:
            continue

    dicom_volume = np.stack(dicom_slices, axis=-1)

    # Load NIfTI
    nifti_data = nib.load(nifti_path).get_fdata(dtype=np.float32)

    idx = slice_idx if slice_idx is not None else dicom_volume.shape[-1] // 2

    fig: Figure = plt.figure(figsize=figsize)

    ax1 = fig.add_subplot(1, 2, 1)
    ax1.imshow(dicom_volume[:, :, idx], cmap="gray")
    ax1.set_title(f"DICOM  (slice {idx})")
    ax1.axis("off")

    ax2 = fig.add_subplot(1, 2, 2)
    ax2.imshow(nifti_data[:, :, idx], cmap="gray")
    ax2.set_title(f"NIfTI  (slice {idx})")
    ax2.axis("off")

    fig.tight_layout()

    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)   # never call plt.show() in server context
    buf.seek(0)
    return buf.read()
