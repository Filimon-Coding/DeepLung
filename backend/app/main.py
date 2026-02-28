from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .router import router as api_router

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

# Include api routes (everything under /api)
app.include_router(api_router)

@app.get("/")
def root():
    return {"message": "CRAI backend is running"}