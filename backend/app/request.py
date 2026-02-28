from pydantic import BaseModel, EmailStr

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    email: str
    role: str

class AnalyzeResponse(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    prediction: str
    confidence: float