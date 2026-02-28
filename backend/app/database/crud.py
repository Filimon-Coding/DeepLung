from typing import Optional
from fastapi import HTTPException
from sqlmodel import Session, select

from .models import User
from .security import hash_password, verify_password


def authenticate(session: Session, email: str, password: str) -> Optional[User]:
    """
    Returns User if email exists AND password matches, else None.
    """
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None

    # If you store hashed passwords (recommended):
    if not verify_password(password, user.hashed_password):
        return None

    return user


def create_user(session: Session, email: str, password: str, role: str = "user") -> User:
    """
    Creates a new user in DB. Raises 409 if user already exists.
    """
    existing = session.exec(select(User).where(User.email == email)).first()
    if existing:
        raise HTTPException(status_code=409, detail="User already exists")

    user = User(
        email=email,
        role=role,
        hashed_password=hash_password(password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)
    return user