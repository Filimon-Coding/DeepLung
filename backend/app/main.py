from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .router import router as api_router
from .data.db import create_db_and_tables, engine
from .data.models import User  # <- sørg for at denne finnes
from .data.security import hash_password  # <- hvis du hasher passord (anbefalt)

app = FastAPI(title="CRAI Backend", version="0.1.0")

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

def seed_users():
    demo_users = [
        {"email": "admin@crai.com", "password": "test123", "role": "admin"},
        {"email": "doctor@crai.com", "password": "test123", "role": "doctor"},
    ]

    with Session(engine) as session:
        for u in demo_users:
            exists = session.exec(select(User).where(User.email == u["email"])).first()
            if exists:
                continue

            user = User(
                email=u["email"],
                role=u["role"],
                hashed_password=hash_password(u["password"]),  # eller password=u["password"] hvis demo
            )
            session.add(user)

        session.commit()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    seed_users()

@app.get("/")
def root():
    return {"message": "CRAI backend is running"}