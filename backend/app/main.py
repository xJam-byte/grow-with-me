import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import api_router
from app.bot.bot import dp, get_bot
from app.config import get_settings
from app.database import engine
from app.models.base import Base
from app.services.notification_scheduler import start_scheduler, stop_scheduler

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("grow_with_me")

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up Grow With Me backend...")
    
    # In development, auto-create tables if they don't exist
    if settings.is_dev:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables verified.")
        except Exception as e:
            logger.warning(f"Could not connect to database on startup: {e}. Check DATABASE_URL.")

    # Start Telegram bot polling and notification scheduler in background if token is provided
    bot_task = None
    bot_instance = get_bot()
    if bot_instance:
        logger.info("Telegram Bot token found. Starting bot polling in background...")
        bot_task = asyncio.create_task(dp.start_polling(bot_instance))
        start_scheduler()
    else:
        logger.info("No TELEGRAM_BOT_TOKEN set. Skipping bot startup.")

    yield

    logger.info("Shutting down Grow With Me backend...")
    stop_scheduler()
    if bot_instance:
        try:
            await dp.stop_polling()
            await bot_instance.session.close()
        except Exception:
            pass
    if bot_task:
        bot_task.cancel()
        try:
            await bot_task
        except asyncio.CancelledError:
            pass
    await engine.dispose()


app = FastAPI(
    title="Grow With Me API",
    description="Personal Growth Operating System API",
    version="0.1.0",
    lifespan=lifespan,
)

# Global error handler for uncaught server errors
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (StarletteHTTPException, RequestValidationError)):
        raise exc
    logger.error(f"Unhandled error on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера. Пожалуйста, попробуйте позже."},
    )

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routes
app.include_router(api_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "Grow With Me API is running",
        "docs": "/docs",
        "health": "/api/health",
    }

