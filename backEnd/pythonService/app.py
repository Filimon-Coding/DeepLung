from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io

app = FastAPI(title="DeepLungCT Python Service")

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Read bytes
    content = await file.read()

    # Example: load image (replace with your model pipeline)
    img = Image.open(io.BytesIO(content)).convert("RGB")
    w, h = img.size

    # TODO: run model inference here
    prediction = "Normal"
    confidence = 0.83

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "prediction": prediction,
        "confidence": confidence,
        "image_width": w,
        "image_height": h,
    }