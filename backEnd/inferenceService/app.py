import os
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch

from infer import (
    load_model,
    predict,
    extract_nifti_patient_info,
    count_nodule_candidates,
    append_prediction_log,
)

app = FastAPI(title="DeepLungCT Python Service")

# Allow requests from the C# proxy (and direct dev access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL = None
CHECKPOINT_PATH = "checkpoints/resnet3d_latest.pth"
PREDICTION_LOG_PATH = os.path.join(
    os.path.dirname(__file__), "PredictOutPut", "PredicationOutPut.md"
)
# CHECKPOINT_PATH = "checkpoints/resnet3d_epoch_20.pth"


@app.on_event("startup")
def startup():
    global MODEL
    print(f"[startup] Loading model on {DEVICE} ...")
    MODEL = load_model(CHECKPOINT_PATH, DEVICE)
    print("[startup] Model ready.")


@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": MODEL is not None, "device": str(DEVICE)}


@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    if not (file.filename.endswith(".nii") or file.filename.endswith(".nii.gz")):
        raise HTTPException(
            status_code=400,
            detail="Only .nii or .nii.gz files are accepted.",
        )

    content = await file.read()

    try:
        out = predict(MODEL, DEVICE, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    # --- Prediction log ---
    try:
        patient_info = extract_nifti_patient_info(content)
        # Rebuild a minimal CAM from the peak coordinates to count clusters;
        # the full cam_3d is not returned by predict(), so we use a threshold
        # proxy: nodule count is stored via a separate infer call on the cached
        # volume.  For now we derive it from the peak value returned in `out`.
        # A value of 0 means the CAM was flat (benign, no activation).
        n_nodules = 1 if out["prediction"] == "Malignancy" else 0
        append_prediction_log(
            PREDICTION_LOG_PATH,
            filename=file.filename,
            patient_info=patient_info,
            n_nodules=n_nodules,
            result=out,
        )
    except Exception as log_err:
        print(f"[log] Could not write prediction log: {log_err}")

    return {
        "filename": file.filename,
        "content_type": file.content_type or "application/gzip",
        "size_bytes": len(content),
        **out,
    }