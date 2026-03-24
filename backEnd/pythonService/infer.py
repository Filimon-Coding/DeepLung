import os
import tempfile
import io
import base64
import numpy as np
import torch
import torch.nn.functional as F
import torchio as tio
import SimpleITK as sitk
from PIL import Image

from model import ResNet3D

CLASS_NAMES = ["Benign", "Malignancy"]

preprocess = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad((128, 128, 128)),
])


def load_model(checkpoint_path: str, device: torch.device) -> torch.nn.Module:
    model = ResNet3D().to(device)
    ckpt = torch.load(checkpoint_path, map_location=device)

    if isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state = ckpt["model_state_dict"]
    elif isinstance(ckpt, dict):
        state = ckpt
    else:
        raise ValueError(f"Unsupported checkpoint type: {type(ckpt)}")

    model.load_state_dict(state, strict=True)
    model.eval()
    return model


def nifti_bytes_to_tensor(nifti_bytes: bytes) -> torch.Tensor:
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp_path = tmp.name

        img = sitk.ReadImage(tmp_path)
        arr = sitk.GetArrayFromImage(img).astype(np.float32)  # (D, H, W)

        t = torch.from_numpy(arr).unsqueeze(0)  # (1, D, H, W)
        subject = tio.Subject(mri=tio.ScalarImage(tensor=t))
        subject = preprocess(subject)

        return subject.mri.data  # (1, 128, 128, 128)

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

        weights = grads.mean(dim=(2, 3, 4), keepdim=True)
        cam = (weights * acts).sum(dim=1).squeeze()
        cam = F.relu(cam)

        # Upsample small feature-map CAM (e.g. 8x8x8) back to full volume size
        target_size = tuple(x_batch.shape[2:])   # (128, 128, 128)
        cam_up = F.interpolate(
            cam.detach().cpu().unsqueeze(0).unsqueeze(0),
            size=target_size,
            mode="trilinear",
            align_corners=False,
        ).squeeze().numpy()

        c_min, c_max = cam_up.min(), cam_up.max()
        if c_max > c_min:
            cam_up = (cam_up - c_min) / (c_max - c_min)

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
    """
    Simple approximate jet colormap without OpenCV.
    Input: uint8 grayscale image
    Output: RGB uint8 image
    """
    x = gray_u8.astype(np.float32) / 255.0

    r = np.clip(1.5 - np.abs(4 * x - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * x - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * x - 1), 0, 1)

    rgb = np.stack([r, g, b], axis=-1)
    return (rgb * 255).astype(np.uint8)


def tensor_to_middle_slice_b64(volume: torch.Tensor, size: int = 256) -> str:
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
    alpha: float = 0.45,
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

    vol_rgb = np.stack([vol_u8] * 3, axis=-1).astype(np.float32)
    blend = ((1 - alpha) * vol_rgb + alpha * heatmap_rgb.astype(np.float32))
    blend = np.clip(blend, 0, 255).astype(np.uint8)

    return _to_b64_png(blend)


def cam_to_nifti_b64(cam_3d: np.ndarray) -> str:
    """Serialize a 3-D Grad-CAM array (D,H,W) as a .nii file, base64-encoded."""
    sitk_img = sitk.GetImageFromArray(cam_3d.astype(np.float32))
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".nii", delete=False) as tmp:
            tmp_path = tmp.name
        sitk.WriteImage(sitk_img, tmp_path)
        with open(tmp_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def predict(model: torch.nn.Module, device: torch.device, nifti_bytes: bytes) -> dict:
    volume = nifti_bytes_to_tensor(nifti_bytes)
    x_batch = volume.unsqueeze(0).to(device)

    with torch.no_grad():
        logits = model(x_batch)
        probs = F.softmax(logits, dim=1).cpu().numpy()[0]
        pred_idx = int(np.argmax(probs))

    cam_3d = compute_gradcam(model, x_batch, pred_idx)

    slice_b64 = tensor_to_middle_slice_b64(volume)
    gradcam_b64 = gradcam_overlay_b64(cam_3d, volume)
    gradcam_nifti_b64 = cam_to_nifti_b64(cam_3d)

    return {
        "prediction": CLASS_NAMES[pred_idx],
        "confidence": float(probs[pred_idx]),
        "prob_benign": float(probs[0]),
        "prob_malignancy": float(probs[1]),
        "middle_slice_b64": slice_b64,
        "gradcam_b64": gradcam_b64,
        "gradcam_nifti_b64": gradcam_nifti_b64,
    }