from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter(tags=["auth"])

# Hardcoded demo users (with email as username)
USERS = {
    "admin@crai.com": {
        "password": "test123",
        "role": "admin"
    },
    "doctor@crai.com": {
        "password": "test123",
        "role": "doctor"
    },
}

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/login")
def login(data: LoginRequest):
    user = USERS.get(data.email)

    if not user or user["password"] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    return {
        "email": data.email,
        "role": user["role"]
    }