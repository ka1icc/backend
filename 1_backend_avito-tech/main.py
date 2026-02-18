"""Точка входа: создание приложения и подключение роутеров."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.db import Base, engine
from app.routers import shortener


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Создание таблиц при старте."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(title="URL Shortener API", lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(shortener.router, tags=["shortener"])
