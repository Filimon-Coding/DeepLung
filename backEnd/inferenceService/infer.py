import os
import tempfile
import io
import base64
import datetime
import pathlib
import uuid
import numpy as np
import torch
import torch.nn.functional as F
import torchio as tio
from PIL import Image

from model import ResNet3D

CAM_CACHE_DIR = pathlib.Path(__file__).parent / "cam_cache"

CLASS_NAMES = ["Benign", "Malignancy"]

# Preprocessing must exactly match the training script at commit 95f593dd:
#   - No HU clamping (raw values are normalised directly)
#   - RescaleIntensity to [0, 1] on the full unclamped volume
#   - CropOrPad to 192×192×192 (the crop size used during training)
preprocess = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad((192, 192, 192)),
])


def load_model(checkpoint_path: str, device: torch.device) -> torch.nn.Module:
    model = ResNet3D().to(device)
    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)

    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state = ckpt["model_state_dict"]
    elif isinstance(ckpt, dict):
        state = ckpt
    else:
        raise ValueError(f"Unsupported checkpoint type: {type(ckpt)}")

    model.load_state_dict(state, strict=True)
    model.eval()
    return model


def nifti_bytes_to_tensor(nifti_bytes: bytes):
    """Returns (preprocessed tensor, preprocessed affine, original tensor, original affine)."""
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp_path = tmp.name

        subject = tio.Subject(mri=tio.ScalarImage(tmp_path))

        original_tensor = subject.mri.data.clone()        # (1, X, Y, Z) full resolution
        original_affine = subject.mri.affine.copy()       # affine before any crop/pad

        subject = preprocess(subject)

        return subject.mri.data, subject.mri.affine, original_tensor, original_affine

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def compute_gradcam(
    model: torch.nn.Module,
    x_batch: torch.Tensor,
    pred_idx: int,
) -> np.ndarray:
    activations: dict = {}
    gradients: dict = {}

    def fwd_hook(module, inp, out):
        activations["feat"] = out

    def bwd_hook(module, grad_in, grad_out):
        gradients["feat"] = grad_out[0]

    h_f = model.layer3.register_forward_hook(fwd_hook)
    h_b = model.layer3.register_full_backward_hook(bwd_hook)

    try:
        model.zero_grad()
        logits = model(x_batch)
        score = logits[0, pred_idx]
        score.backward()

        acts = activations["feat"]
        grads = gradients["feat"]

        # GradCAM++ weights — sharper localization than plain mean(grads)
        grads_sq  = grads.pow(2)
        grads_cb  = grads.pow(3)
        act_sum   = acts.sum(dim=(2, 3, 4), keepdim=True)
        alpha     = grads_sq / (2.0 * grads_sq + act_sum * grads_cb + 1e-7)
        weights   = (alpha * F.relu(grads)).sum(dim=(2, 3, 4), keepdim=True)
        cam = F.relu((weights * acts).sum(dim=1).squeeze())

        # Upsample back to input volume size
        target_size = tuple(x_batch.shape[2:])
        cam_up = F.interpolate(
            cam.detach().cpu().unsqueeze(0).unsqueeze(0),
            size=target_size,
            mode="trilinear",
            align_corners=False,
        ).squeeze().numpy()

        # Keep only the top 1 % of activations (99th percentile of non-zero values).
        # The model's final feature map is only 6³, so each activation cell covers
        # a huge region after upsampling — a tight percentile is required to isolate
        # actual peak regions rather than broad gradients.
        if cam_up.max() > 0:
            nonzero = cam_up[cam_up > 0]
            thr = float(np.percentile(nonzero, 99.5)) if len(nonzero) > 0 else 0.0
            cam_up[cam_up < thr] = 0.0
            c_max = cam_up.max()
            if c_max > 0:
                cam_up = cam_up / c_max
            cam_up[cam_up < 0.6] = 0.0

        return cam_up

    except Exception as e:
        print(f"[Grad-CAM] Error: {e}")
        return np.zeros(tuple(x_batch.shape[2:]), dtype=np.float32)

    finally:
        h_f.remove()
        h_b.remove()
        model.zero_grad()


def _to_b64_png(img_array_rgb_or_gray: np.ndarray) -> str:
    if img_array_rgb_or_gray.ndim == 2:
        pil_img = Image.fromarray(img_array_rgb_or_gray.astype(np.uint8), mode="L")
    else:
        pil_img = Image.fromarray(img_array_rgb_or_gray.astype(np.uint8), mode="RGB")

    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode("utf-8")


def _resize_gray(arr: np.ndarray, size: int) -> np.ndarray:
    img = Image.fromarray(arr.astype(np.uint8), mode="L")
    img = img.resize((size, size), Image.Resampling.BILINEAR)
    return np.array(img)


def _jet_colormap(gray_u8: np.ndarray) -> np.ndarray:
    """Standard piecewise-linear jet colormap (blue→cyan→green→yellow→red)."""
    x = gray_u8.astype(np.float32) / 255.0
    xp = [0.0,  0.125, 0.375, 0.625, 0.875, 1.0]
    rp = [0.0,  0.0,   0.0,   1.0,   1.0,   0.5]
    gp = [0.0,  0.0,   1.0,   1.0,   0.0,   0.0]
    bp = [0.5,  1.0,   1.0,   0.0,   0.0,   0.0]
    r = np.interp(x, xp, rp)
    g = np.interp(x, xp, gp)
    b = np.interp(x, xp, bp)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def tensor_to_middle_slice_b64(volume: torch.Tensor, size: int = 512) -> str:
    vol = volume.squeeze().numpy()
    mid = vol.shape[2] // 2
    sl = vol[:, :, mid].astype(np.float32)

    v_min, v_max = sl.min(), sl.max()
    if v_max > v_min:
        sl = (sl - v_min) / (v_max - v_min)

    sl_u8 = (sl * 255).astype(np.uint8)
    sl_u8 = _resize_gray(sl_u8, size)
    return _to_b64_png(sl_u8)


def gradcam_overlay_b64(
    cam_3d: np.ndarray,
    volume: torch.Tensor,
    size: int = 256,
) -> str:
    vol = volume.squeeze().numpy()
    mid_vol = vol.shape[2] // 2
    mid_cam = cam_3d.shape[2] // 2

    vol_sl = vol[:, :, mid_vol].astype(np.float32)
    cam_sl = cam_3d[:, :, mid_cam].astype(np.float32)

    v_min, v_max = vol_sl.min(), vol_sl.max()
    if v_max > v_min:
        vol_sl = (vol_sl - v_min) / (v_max - v_min)

    vol_u8 = (vol_sl * 255).astype(np.uint8)
    vol_u8 = _resize_gray(vol_u8, size)

    cam_u8 = (cam_sl * 255).astype(np.uint8)
    cam_u8 = _resize_gray(cam_u8, size)

    heatmap_rgb = _jet_colormap(cam_u8)

    # Per-pixel blend: cam intensity controls how much heatmap replaces CT.
    # Zero-activation pixels stay as pure CT grayscale; peak activations
    # become up to 85% vivid heatmap color so anatomy stays readable.
    cam_weight = cam_u8.astype(np.float32) / 255.0
    cam_weight = cam_weight[:, :, np.newaxis] * 0.85

    vol_rgb = np.stack([vol_u8] * 3, axis=-1).astype(np.float32)
    blend = vol_rgb * (1.0 - cam_weight) + heatmap_rgb.astype(np.float32) * cam_weight
    blend = np.clip(blend, 0, 255).astype(np.uint8)

    return _to_b64_png(blend)


def cam_to_nifti_b64(cam_3d: np.ndarray, affine: np.ndarray | None = None) -> str:
    """Serialize a 3-D Grad-CAM array as a gzip-compressed .nii.gz, base64-encoded.

    Using .nii.gz is critical: the full-res CAM volume is mostly zeros after
    thresholding, so gzip shrinks it from ~300 MB to a few MB.
    """
    import nibabel as nib

    nib_affine = affine if affine is not None else np.eye(4)
    nib_img = nib.Nifti1Image(cam_3d.astype(np.float32), nib_affine)

    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as tmp:
            tmp_path = tmp.name
        nib.save(nib_img, tmp_path)
        with open(tmp_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def _save_cam_to_cache(cam_full: np.ndarray, affine: np.ndarray) -> str:
    """Persist cam_full + affine as a compressed .npz file. Returns the absolute path."""
    CAM_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    path = CAM_CACHE_DIR / f"{uuid.uuid4().hex}.npz"
    np.savez_compressed(str(path), cam=cam_full.astype(np.float32), affine=affine)
    return str(path)


def load_cam_from_cache(cam_cache_path: str) -> tuple[np.ndarray, np.ndarray]:
    """Load cam_full and affine from a .npz cache file."""
    data = np.load(cam_cache_path)
    return data["cam"], data["affine"]


def predict(model: torch.nn.Module, device: torch.device, nifti_bytes: bytes) -> dict:
    volume, affine, original_volume, original_affine = nifti_bytes_to_tensor(nifti_bytes)
    x_batch = volume.unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(x_batch)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]
        pred_idx = int(np.argmax(probs))

    cam_3d = compute_gradcam(model, x_batch, pred_idx)

    # Upsample CAM to original CT dimensions so the NIfTI overlay matches exactly —
    # avoids the bounding-box border artifact NiiVue shows when overlaying a smaller volume
    orig_shape = tuple(original_volume.shape[1:])   # (X, Y, Z)
    cam_full = F.interpolate(
        torch.from_numpy(cam_3d).float().unsqueeze(0).unsqueeze(0),
        size=orig_shape,
        mode="trilinear",
        align_corners=False,
    ).squeeze().numpy()

    # Re-threshold after trilinear upsampling smears the sparse hotspots.
    # Use percentile of NON-ZERO values only — the volume is mostly zeros so
    # percentile-of-all would return 0.0 and remove nothing.
    if cam_full.max() > 0:
        nonzero = cam_full[cam_full > 0]
        if len(nonzero) > 0:
            thr = float(np.percentile(nonzero, 85))
            cam_full[cam_full < thr] = 0.0
        c_max = cam_full.max()
        if c_max > 0:
            cam_full = cam_full / c_max
        cam_full[cam_full < 0.5] = 0.0

    orig_vol_np = original_volume.squeeze().numpy()
    slice_total = int(orig_vol_np.shape[2])
    slice_index = slice_total // 2
    slice_b64 = tensor_to_middle_slice_b64(original_volume)

    gradcam_b64 = gradcam_overlay_b64(cam_3d, volume)

    # Save full-res CAM + affine to disk so the NIfTI can be built on demand
    # without blocking the analyze response (cam_to_nifti_b64 is slow for large volumes).
    cam_cache_path = _save_cam_to_cache(cam_full, original_affine)

    # Peak activation in full-res space
    peak_flat = int(np.argmax(cam_full))
    pz, py, px = np.unravel_index(peak_flat, cam_full.shape)

    return {
        "prediction": CLASS_NAMES[pred_idx],
        "confidence": float(probs[pred_idx]),
        "prob_benign": float(probs[0]),
        "prob_malignancy": float(probs[1]),
        "middle_slice_b64": slice_b64,
        "gradcam_b64": gradcam_b64,
        "cam_cache_path": cam_cache_path,
        "slice_index": slice_index,
        "slice_total": slice_total,
        "cam_peak_x": int(px),
        "cam_peak_y": int(py),
        "cam_peak_z": int(pz),
    }


def extract_nifti_patient_info(nifti_bytes: bytes) -> dict:
    """
    Reads NIfTI header fields that may contain patient/study metadata.
    Most public/test NIfTI files leave these blank; real DICOM-derived
    files may populate descrip, db_name, aux_file, etc.
    """
    tmp_path = None
    info = {"patient_id": "N/A", "study_description": "N/A", "aux_file": "N/A"}
    try:
        import nibabel as nib
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp_path = tmp.name
        img = nib.load(tmp_path)
        hdr = img.header
        descrip = hdr.get("descrip", b"").tobytes().decode("utf-8", errors="ignore").strip("\x00").strip()
        db_name = hdr.get("db_name", b"").tobytes().decode("utf-8", errors="ignore").strip("\x00").strip()
        aux_file = hdr.get("aux_file", b"").tobytes().decode("utf-8", errors="ignore").strip("\x00").strip()
        if db_name:
            info["patient_id"] = db_name
        if descrip:
            info["study_description"] = descrip
        if aux_file:
            info["aux_file"] = aux_file
    except Exception:
        pass
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)
    return info


def count_nodule_candidates(cam_3d: np.ndarray, threshold: float = 0.4) -> int:
    """
    Counts the number of distinct high-activation clusters in the Grad-CAM
    volume as a proxy for the number of suspicious nodule regions.
    Uses scipy connected-components; falls back to 1 if scipy is unavailable.
    """
    try:
        from scipy import ndimage
        binary_mask = cam_3d >= threshold
        _, n_clusters = ndimage.label(binary_mask)
        return max(0, n_clusters)
    except ImportError:
        # Fallback: report 1 if any activation above threshold exists
        return 1 if float(cam_3d.max()) >= threshold else 0


_MD_HEADER = (
    "| # | Timestamp | Filename | Patient ID | Study Description "
    "| Nodules (CAM) | Benign % | Malignancy % | Prediction | Confidence % "
    "| CAM Peak (x, y, z) |\n"
    "|---|-----------|----------|------------|------------------"
    "|--------------|---------|--------------|------------|-------------|"
    "--------------------|"
)


def append_prediction_log(
    md_path: str,
    filename: str,
    patient_info: dict,
    n_nodules: int,
    result: dict,
) -> None:
    """Appends one row to the prediction log markdown table."""
    md_file = pathlib.Path(md_path)
    md_file.parent.mkdir(parents=True, exist_ok=True)

    # Count existing data rows to assign a sequential number
    existing_rows = 0
    if md_file.exists():
        content = md_file.read_text(encoding="utf-8")
        # Rows start with "| <digit>"
        existing_rows = sum(
            1 for line in content.splitlines()
            if line.startswith("|") and not line.startswith("| #") and not line.startswith("|---")
        )

    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row_num = existing_rows + 1
    benign_pct = f"{result['prob_benign'] * 100:.1f}%"
    mal_pct = f"{result['prob_malignancy'] * 100:.1f}%"
    confidence_pct = f"{result['confidence'] * 100:.1f}%"
    location = f"({result['cam_peak_x']}, {result['cam_peak_y']}, {result['cam_peak_z']})"
    prediction = result["prediction"]
    patient_id = patient_info.get("patient_id", "N/A") or "N/A"
    study_desc = patient_info.get("study_description", "N/A") or "N/A"

    new_row = (
        f"| {row_num} | {ts} | {filename} | {patient_id} | {study_desc} "
        f"| {n_nodules} | {benign_pct} | {mal_pct} | {prediction} | {confidence_pct} "
        f"| {location} |"
    )

    if not md_file.exists() or md_file.stat().st_size == 0:
        md_file.write_text(
            "# Prediction Output Log\n\n" + _MD_HEADER + "\n" + new_row + "\n",
            encoding="utf-8",
        )
    else:
        with md_file.open("a", encoding="utf-8") as f:
            f.write(new_row + "\n")