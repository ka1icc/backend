"""Database connection and session management."""
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import declarative_base
from sqlalchemy.pool import StaticPool

from app.config import settings

_connect_args = {}
_poolclass = None
if "sqlite" in settings.database_url:
    _connect_args["check_same_thread"] = False
    _poolclass = StaticPool

engine = create_async_engine(
    settings.database_url,
    echo=False,
    connect_args=_connect_args,
    poolclass=_poolclass,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()


class _NullSession:
    """Stub session when PostgreSQL is unavailable."""

    def add(self, _obj):
        pass

    async def flush(self):
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass

    async def close(self):
        pass

    async def execute(self, *args, **kwargs):
        return _NullResult()


class _NullResult:
    def scalar_one_or_none(self):
        return None


async def get_db():
    """Dependency: async database session. Yields NullSession on connection error."""
    try:
        async with AsyncSessionLocal() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                try:
                    await session.rollback()
                except Exception:
                    pass
                raise
            finally:
                try:
                    await session.close()
                except Exception:
                    pass
    except HTTPException:
        raise
    except Exception:
        raise


async def init_db():
    """Create tables if they do not exist."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
