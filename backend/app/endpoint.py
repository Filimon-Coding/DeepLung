from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from sqlmodel import Session

from .request import LoginRequest, LoginResponse, AnalyzeResponse
from .database.db import get_session
from .database.crud import authenticate

from .request import RegisterRequest, RegisterResponse
from .database.models import User
from .database.security import hash_password
from sqlmodel import select

router = APIRouter()

@router.post("/register", response_model=RegisterResponse)
def register(data: RegisterRequest, session: Session = Depends(get_session)):

    # Validate password
    if data.password != data.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # Checks if user exits
    existing = session.exec(
        select(User).where(User.email == data.email)
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="User already exists")

    # Create user
    user = User(
        email=data.email,
        role=data.role,
        hashed_password=hash_password(data.password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    return {"email": user.email, "role": user.role}

@router.post("/login", response_model=LoginResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = authenticate(session, data.email, data.password)

    if not user:
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