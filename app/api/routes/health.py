from fastapi import APIRouter
from app.utils.logger import logger

router = APIRouter()

@router.get("/health", summary="Health check")
async def health_check():
    logger.info("Health check requested")
    return {"status": "ok", "message": "Notes automation backend is running"}
