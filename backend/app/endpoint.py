from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlmodel import Session

from .request import (
    LoginRequest, LoginResponse,
    RegisterRequest, RegisterResponse,
    AnalyzeResponse
)

from .database.db import get_session
from .database.crud import authenticate, create_user

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    user = create_user(session, email=data.email, password=data.password, role=data.role)
    return {"email": user.email, "role": user.role}

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):

    user = authenticate(session, data.email)

    if not user or user.password != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {"email": user.email, "role": user.role}


@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Please upload an image file.")

    content = await file.read()

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
        "prediction": "benign",
        "confidence": 0.84,
    }