import asyncio
import sys
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.config import get_settings
from app.models.base import Base

settings = get_settings()

# Use NullPool for tests so each test has fresh connections without event-loop leaks
test_engine = create_async_engine(
    settings.database_url,
    poolclass=NullPool,
    echo=False,
)

TestSession = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture
async def db_session():
    async with TestSession() as session:
        yield session
        await session.rollback()
