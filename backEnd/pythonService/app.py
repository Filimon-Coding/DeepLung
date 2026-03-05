from fastapi import FastAPI, UploadFile, File, HTTPException
import torch

from infer import load_model, predict

app = FastAPI(title="DeepLungCT Python Service")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL = None

CHECKPOINT_PATH = "checkpoints/resnet3d_latest.pth"

@app.on_event("startup")
def startup():
    global MODEL
    MODEL = load_model(CHECKPOINT_PATH, DEVICE)

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    if MODEL is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    # For now: enforce nifti uploads
    if not (file.filename.endswith(".nii") or file.filename.endswith(".nii.gz")):
        raise HTTPException(status_code=400, detail="Please upload a .nii or .nii.gz file")

    content = await file.read()

    try:
        out = predict(MODEL, DEVICE, content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed: {str(e)}")

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        **out
    }