from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import api_router

app = FastAPI(title="CRAI Backend", version="0.1.0")

# Allow requests from your Vite frontend
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

# Include API routes (everything under /api)
app.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    return {"message": "CRAI backend is running"}