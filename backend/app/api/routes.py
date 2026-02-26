from fastapi import APIRouter, UploadFile, File, HTTPException

router = APIRouter(prefix="/api")


@router.post("/analyze")
async def analyze_image(file: UploadFile = File(...)):
    # Basic validation
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    # Read file bytes (later you send this to the AI model)
    data = await file.read()

    # Dummy response for now
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(data),
        "prediction": "benign",
        "confidence": 0.84,
    }