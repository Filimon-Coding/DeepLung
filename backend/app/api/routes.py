from fastapi import APIRouter, UploadFile, File, HTTPException
from .auth import router as auth_router

# This is the single API router that main.py includes with prefix="/api"
api_router = APIRouter()

# Include auth routes (e.g., POST /login)
api_router.include_router(auth_router)

@api_router.post("/analyze")
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