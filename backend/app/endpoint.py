from fastapi import APIRouter, UploadFile, File, HTTPException
from .request import LoginRequest, LoginResponse, AnalyzeResponse

router = APIRouter()

# Hardcoded demo users (email as username)
USERS = {
    "admin@crai.com": {"password": "test123", "role": "admin"},
    "doctor@crai.com": {"password": "test123", "role": "doctor"},
}

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest):
    user = USERS.get(str(data.email))
    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"email": data.email, "role": user["role"]}

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    data = await file.read()

    # Dummy response for now
    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(data),
        "prediction": "benign",
        "confidence": 0.84,
    }