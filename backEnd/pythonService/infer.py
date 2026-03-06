import os
import tempfile
import io
import numpy as np
import torch
import torch.nn.functional as F
import torchio as tio
import SimpleITK as sitk

from model import ResNetShort

CLASS_NAMES = ["Benign", "Malignancy"]

preprocess = tio.Compose([
    tio.RescaleIntensity(out_min_max=(0, 1)),
    tio.CropOrPad((128, 128, 128)),
])

def load_model(checkpoint_path: str, device: torch.device) -> torch.nn.Module:
    model = ResNetShort().to(device)
    ckpt = torch.load(checkpoint_path, map_location=device)

    if isinstance(ckpt, dict) and ("model_state_dict" in ckpt):
        state = ckpt["model_state_dict"]
    elif isinstance(ckpt, dict):
        state = ckpt
    else:
        raise ValueError(f"Unsupported checkpoint type: {type(ckpt)}")

    model.load_state_dict(state, strict=True)
    model.eval()
    return model

def nifti_bytes_to_tensor(nifti_bytes: bytes) -> torch.Tensor:
    """
    SimpleITK wants a filepath, so we write bytes to a temp file first.
    Returns tensor (1, 128, 128, 128).
    """
    tmp_path = None
    try:
        # Write uploaded bytes to temp .nii.gz file
        with tempfile.NamedTemporaryFile(suffix=".nii.gz", delete=False) as tmp:
            tmp.write(nifti_bytes)
            tmp_path = tmp.name

        img = sitk.ReadImage(tmp_path)
        arr = sitk.GetArrayFromImage(img).astype(np.float32)  # (D, H, W)

        t = torch.from_numpy(arr).unsqueeze(0)  # (C=1, D, H, W)
        subject = tio.Subject(mri=tio.ScalarImage(tensor=t))
        subject = preprocess(subject)

        return subject.mri.data  # (1, 128, 128, 128)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.remove(tmp_path)

@torch.no_grad()
def predict(model: torch.nn.Module, device: torch.device, nifti_bytes: bytes):
    x = nifti_bytes_to_tensor(nifti_bytes)   # (1, D,H,W)
    x = x.unsqueeze(0).to(device)            # (B=1, C=1, D,H,W)

    logits = model(x)
    probs = F.softmax(logits, dim=1).cpu().numpy()[0]

    pred_idx = int(np.argmax(probs))
    return {
        "prediction": CLASS_NAMES[pred_idx],
        "confidence": float(probs[pred_idx]),
        "prob_benign": float(probs[0]),
        "prob_malignancy": float(probs[1]),
    }