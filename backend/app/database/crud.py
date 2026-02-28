from typing import Optional
from fastapi import HTTPException
from sqlmodel import Session, select
from .models import User

def get_user_by_email(session: Session, email: str) -> Optional[User]:
    return session.exec(select(User).where(User.email == email)).first()

def authenticate(session: Session, email: str) -> Optional[User]:
    # For login: get user, dont check password here
    return get_user_by_email(session, email)

def create_user(session: Session, email: str, password: str, role: str = "doctor") -> User:
    existing = get_user_by_email(session, email)
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=email,
        role=role,
        password=password,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user