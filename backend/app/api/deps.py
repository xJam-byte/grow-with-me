from typing import Optional
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.telegram import parse_and_validate_init_data
from app.config import Settings, get_settings
from app.database import get_db
from app.models.user import User
from app.repositories.user import UserRepository


async def get_current_user(
    authorization: Optional[str] = Header(None, alias="Authorization"),
    db: AsyncSession = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> User:
    """
    Extracts and validates Telegram initData from 'Authorization: tma <initData>' header.
    Returns or registers the authenticated User.
    """
    if not authorization:
        # If in development mode and no auth provided, use fallback dev user
        if settings.is_dev:
            user_repo = UserRepository(db)
            return await user_repo.get_or_create(
                telegram_id=settings.owner_telegram_id or 123456789,
                username="owner",
                first_name="Owner",
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = authorization.partition(" ")
    if scheme.lower() not in ("tma", "bearer"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization scheme. Expected 'tma <initData>'",
        )

    parsed_user = parse_and_validate_init_data(
        init_data_raw=token,
        bot_token=settings.telegram_bot_token,
        allow_dev_fallback=settings.is_dev,
    )

    if not parsed_user or "id" not in parsed_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Telegram initData or signature verification failed",
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_or_create(
        telegram_id=parsed_user["id"],
        username=parsed_user.get("username"),
        first_name=parsed_user.get("first_name"),
        last_name=parsed_user.get("last_name"),
    )
    return user

