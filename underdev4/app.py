import os
import torch
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from infer import load_model, predict

app = FastAPI(title="DeepLungCT — MedicalNet ResNet-18 test")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL = None

# Drop any .pth from MedicalNet (or your own trained weights) into underdev4/checkpoints/
# and update the filename below. Backbone-only weights load fine with strict=False.
# CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "checkpoints", "resnet_18.pth")
CHECKPOINT_PATH = os.path.join(os.path.dirname(__file__), "checkpoints", "medicalnet_finetuned_latest.pth")


@app.on_event("startup")
def startup():
    global MODEL
    print(f"[startup] Loading MedicalNet ResNet-18 on {DEVICE} ...")
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
        raise HTTPException(status_code=400, detail="Only .nii or .nii.gz files accepted.")

    content = await file.read()
    try:
        out = predict(MODEL, DEVICE, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    return {"filename": file.filename, "size_bytes": len(content), **out}
