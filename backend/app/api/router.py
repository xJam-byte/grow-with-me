from fastapi import APIRouter

from app.api import profile

api_router = APIRouter()

@api_router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Grow With Me API",
        "version": "0.1.0",
    }

api_router.include_router(profile.router)
