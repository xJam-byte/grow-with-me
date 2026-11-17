from fastapi import APIRouter

from app.api import ai, habits, journal, knowledge, notes, profile, spiritual

api_router = APIRouter()

@api_router.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "service": "Grow With Me API",
        "version": "0.1.0",
    }

api_router.include_router(profile.router)
api_router.include_router(habits.router)
api_router.include_router(knowledge.router)
api_router.include_router(spiritual.router)
api_router.include_router(journal.router)
api_router.include_router(notes.router)
api_router.include_router(ai.router)
