"""
Database setup for the RaizDigital backend.

This module exposes an asynchronous SQLAlchemy ``Engine`` and a
dependency to provide scoped sessions in FastAPI routes.  A helper
function ``init_db`` can be called at startup to run asynchronous
migrations or to create initial tables if using SQLAlchemy's
``metadata.create_all``.  In a production deployment, migrations
should be handled via Alembic.
"""
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.asyncio import async_sessionmaker as _async_sessionmaker
from sqlalchemy.orm import declarative_base

from .config import get_settings


settings = get_settings()

# Base class for our ORM models
Base = declarative_base()

# Create the asynchronous engine
engine = create_async_engine(
    settings.database_url,
    echo=False,
)

# Create an asynchronous session factory
async_session_maker = _async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a transactional SQLAlchemy session."""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialise database (e.g. create tables) in an asynchronous context."""
    # In a real project, use Alembic for migrations. For development,
    # we can create all tables automatically.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
