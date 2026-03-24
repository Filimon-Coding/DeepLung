from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import torch

from infer import load_model, predict

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

    return {
        "filename": file.filename,
        "content_type": file.content_type or "application/gzip",
        "size_bytes": len(content),
        **out,
    }