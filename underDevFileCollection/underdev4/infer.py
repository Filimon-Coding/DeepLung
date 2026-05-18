import os
import sys
import tempfile
import io
import base64
import numpy as np
import torch
import torch.nn.functional as F
import torchio as tio
import SimpleITK as sitk
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from underDevFileCollection.underdev4.model import ResNet3D

CLASS_NAMES = ["Benign", "Malignancy"]

HU_MIN, HU_MAX = -1000, 400

preprocess = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad((96, 96, 96)),
])


def load_model(checkpoint_path: str, device: torch.device) -> torch.nn.Module:
    model = ResNet3D().to(device)

    ckpt = torch.load(checkpoint_path, map_location=device, weights_only=False)

    # MedicalNet format: {'state_dict': {'module.<key>': tensor, ...}}
    # Strip DataParallel 'module.' prefix so keys match our model
    if isinstance(ckpt, dict) and "state_dict" in ckpt:
        raw = ckpt["state_dict"]
        state = {k.replace("module.", ""): v for k, v in raw.items()}
    elif isinstance(ckpt, dict) and "model_state_dict" in ckpt:
        state = ckpt["model_state_dict"]
    elif isinstance(ckpt, dict):
        state = {k.replace("module.", ""): v for k, v in ckpt.items()}
    else:
        raise ValueError(f"Unsupported checkpoint type: {type(ckpt)}")

    # strict=False: MedicalNet has no classifier head — those layers stay randomly init
    missing, unexpected = model.load_state_dict(state, strict=False)
    print(f"[load_model] Missing keys  : {missing}")
    print(f"[load_model] Unexpected keys: {unexpected}")

    model.eval()
    return model


def nifti_bytes_to_tensor(nifti_bytes: bytes):
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp_path = tmp.name

        subject = tio.Subject(mri=tio.ScalarImage(tmp_path))
        original_tensor = subject.mri.data.clone()
        original_affine = subject.mri.affine.copy()

        subject.mri.set_data(torch.clamp(subject.mri.data, HU_MIN, HU_MAX))
        subject = preprocess(subject)

        return subject.mri.data, subject.mri.affine, original_tensor, original_affine
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)


def compute_gradcam(model, x_batch, pred_idx):
    activations, gradients = {}, {}

    def fwd_hook(module, inp, out):
        activations["feat"] = out

    def bwd_hook(module, grad_in, grad_out):
        gradients["feat"] = grad_out[0]

    # Use layer4 — deepest feature map, best for CAM
    h_f = model.layer4.register_forward_hook(fwd_hook)
    h_b = model.layer4.register_full_backward_hook(bwd_hook)

    try:
        model.zero_grad()
        logits = model(x_batch)
        score = logits[0, pred_idx]
        score.backward()

        acts = activations["feat"]
        grads = gradients["feat"]

        grads_sq = grads.pow(2)
        grads_cb = grads.pow(3)
        act_sum  = acts.sum(dim=(2, 3, 4), keepdim=True)
        alpha    = grads_sq / (2.0 * grads_sq + act_sum * grads_cb + 1e-7)
        weights  = (alpha * F.relu(grads)).sum(dim=(2, 3, 4), keepdim=True)
        cam = F.relu((weights * acts).sum(dim=1).squeeze())

        target_size = tuple(x_batch.shape[2:])
        cam_up = F.interpolate(
            cam.detach().cpu().unsqueeze(0).unsqueeze(0),
            size=target_size,
            mode="trilinear",
            align_corners=False,
        ).squeeze().numpy()

        if cam_up.max() > 0:
            nonzero = cam_up[cam_up > 0]
            thr = float(np.percentile(nonzero, 90)) if len(nonzero) > 0 else 0.0
            cam_up[cam_up < thr] = 0.0
            c_max = cam_up.max()
            if c_max > 0:
                cam_up = cam_up / c_max

        return cam_up

    except Exception as e:
        print(f"[Grad-CAM] Error: {e}")
        return np.zeros(tuple(x_batch.shape[2:]), dtype=np.float32)
    finally:
        h_f.remove()
        h_b.remove()
        model.zero_grad()


def _to_b64_png(arr):
    if arr.ndim == 2:
        pil = Image.fromarray(arr.astype(np.uint8), mode="L")
    else:
        pil = Image.fromarray(arr.astype(np.uint8), mode="RGB")
    buf = io.BytesIO()
    pil.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def _resize_gray(arr, size):
    img = Image.fromarray(arr.astype(np.uint8), mode="L")
    return np.array(img.resize((size, size), Image.Resampling.BILINEAR))


def _jet_colormap(gray_u8):
    x = gray_u8.astype(np.float32) / 255.0
    r = np.clip(1.5 - np.abs(4 * x - 3), 0, 1)
    g = np.clip(1.5 - np.abs(4 * x - 2), 0, 1)
    b = np.clip(1.5 - np.abs(4 * x - 1), 0, 1)
    return (np.stack([r, g, b], axis=-1) * 255).astype(np.uint8)


def tensor_to_middle_slice_b64(volume, size=512):
    vol = volume.squeeze().numpy()
    mid = vol.shape[2] // 2
    sl = vol[:, :, mid].astype(np.float32)
    v_min, v_max = sl.min(), sl.max()
    if v_max > v_min:
        sl = (sl - v_min) / (v_max - v_min)
    return _to_b64_png(_resize_gray((sl * 255).astype(np.uint8), size))


def gradcam_overlay_b64(cam_3d, volume, size=256, alpha=0.45):
    vol = volume.squeeze().numpy()
    mid_vol = vol.shape[2] // 2
    mid_cam = cam_3d.shape[2] // 2

    vol_sl = vol[:, :, mid_vol].astype(np.float32)
    cam_sl = cam_3d[:, :, mid_cam].astype(np.float32)

    v_min, v_max = vol_sl.min(), vol_sl.max()
    if v_max > v_min:
        vol_sl = (vol_sl - v_min) / (v_max - v_min)

    vol_u8 = _resize_gray((vol_sl * 255).astype(np.uint8), size)
    cam_u8 = _resize_gray((cam_sl * 255).astype(np.uint8), size)
    heatmap = _jet_colormap(cam_u8)
    vol_rgb = np.stack([vol_u8] * 3, axis=-1).astype(np.float32)
    blend = np.clip((1 - alpha) * vol_rgb + alpha * heatmap.astype(np.float32), 0, 255).astype(np.uint8)
    return _to_b64_png(blend)


def predict(model, device, nifti_bytes: bytes) -> dict:
    tensor, affine, orig_tensor, orig_affine = nifti_bytes_to_tensor(nifti_bytes)

    x = tensor.unsqueeze(0).to(device)  # (1, 1, 96, 96, 96)

    with torch.no_grad():
        logits = model(x)
        probs = torch.softmax(logits, dim=1)[0].cpu().numpy()

    pred_idx = int(probs.argmax())
    prediction = CLASS_NAMES[pred_idx]
    confidence = float(probs[pred_idx])

    model.train()
    cam_3d = compute_gradcam(model, x, pred_idx)
    model.eval()

    mid = orig_tensor.shape[-1] // 2
    cam_peak = np.unravel_index(np.argmax(cam_3d), cam_3d.shape) if cam_3d.max() > 0 else (0, 0, 0)

    return {
        "prediction":      prediction,
        "confidence":      round(confidence, 4),
        "prob_benign":     round(float(probs[0]), 4),
        "prob_malignancy": round(float(probs[1]), 4),
        "middle_slice_b64": tensor_to_middle_slice_b64(orig_tensor),
        "gradcam_b64":     gradcam_overlay_b64(cam_3d, orig_tensor),
        "slice_index":     mid,
        "slice_total":     orig_tensor.shape[-1],
        "cam_peak_x":      int(cam_peak[0]),
        "cam_peak_y":      int(cam_peak[1]),
        "cam_peak_z":      int(cam_peak[2]),
    }
