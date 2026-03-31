"""Модели доменного слоя (ORM)."""

from sqlalchemy import Column, Integer, String

from app.db import Base


class ShortLink(Base):
    """
    Модель короткой ссылки: короткий код и целевой URL.
    """

    __tablename__ = "short_links"

    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String, unique=True, index=True, nullable=False)
    target_url = Column(String, nullable=False)
