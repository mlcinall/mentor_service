import os
from typing import AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import (AsyncEngine, AsyncSession,
                                   async_sessionmaker,
                                   create_async_engine)
from sqlalchemy.pool import NullPool

from settings.settings import settings

# Check if we have a specific SQLite connection string
sqlite_url = os.environ.get("APP_DATABASE_URL")

if sqlite_url and sqlite_url.startswith("sqlite"):
    # Use SQLite
    engine = create_async_engine(
        sqlite_url.replace('sqlite://', 'sqlite+aiosqlite://'),
        future=True,
        echo=False,
    )
    logger.info(f"Using SQLite database: {sqlite_url}")
else:
    # Use PostgreSQL (default)
    POSTGRES_USER = settings.pg.username
    POSTGRES_PASSWORD = settings.pg.password
    POSTGRES_HOST = settings.pg.host
    POSTGRES_PORT = settings.pg.port
    POSTGRES_DB = settings.pg.database

    DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

    engine = create_async_engine(
        DATABASE_URL,
        future=True,
        echo=False,
        poolclass=NullPool,
    )
    logger.info(f"Using PostgreSQL database at {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")

async_session = async_sessionmaker(engine, expire_on_commit=False)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session 