from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine

# Absolute path to backend/ (because this file is backend/app/database/db.py)
BASE_DIR = Path(__file__).resolve().parents[2]  # -> backend/
DB_PATH = (BASE_DIR / "crai.db").resolve()

DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session