from fastapi import APIRouter
from .endpoint import router as endpoint_router

router = APIRouter()
router.include_router(endpoint_router, prefix="/api")