"""Pydantic-схемы для запросов и ответов API."""

from pydantic import BaseModel


class URLCreate(BaseModel):
    """Тело запроса на создание короткой ссылки."""

    target: str


class URLResponse(BaseModel):
    """Ответ с данными созданной короткой ссылки."""

    code: str
    target: str
    short_url: str

    class Config:
        from_attributes = True
