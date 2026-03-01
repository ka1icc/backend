"""Database engine and session factory."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    Session,
    sessionmaker,
)

from app.config import DATABASE_URL

engine = create_engine(
    DATABASE_URL,
    echo=False,
    connect_args={'options': '-c client_encoding=UTF8'},
)

session_factory = sessionmaker(
    bind=engine,
    class_=Session,
)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def get_db() -> Generator[Session, None, None]:
    """Provide a transactional database session."""
    session = session_factory()
    try:  # noqa: WPS501
        yield session
    finally:
        session.close()
