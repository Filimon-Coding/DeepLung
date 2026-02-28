from pydantic import BaseModel, EmailStr

class RegisterRequest(BaseModel):
    email: str
    password: str
    confirm_password: str
    role: str = "doctor"  # default
    
class RegisterResponse(BaseModel):
    email: str
    role: str
    
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