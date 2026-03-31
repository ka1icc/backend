"""Эндпоинты для создания коротких ссылок и редиректа."""

import os

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_short_link, get_link_by_code
from app.db import get_db
from app.domain.schemas import URLCreate, URLResponse
from app.services.shortener import is_valid_target_url, normalize_target_url

router = APIRouter()


@router.get("/")
async def root() -> FileResponse:
    """Отдаёт главную страницу (веб-интерфейс)."""
    html_path = os.path.join("app", "static", "index.html")
    return FileResponse(html_path)


@router.post("/shorten", response_model=URLResponse)
async def shorten(
    payload: URLCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> URLResponse:
    """
    Создаёт короткую ссылку для переданного URL.
    Возвращает код, целевой URL и полную короткую ссылку.
    """
    if not is_valid_target_url(payload.target):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL",
        )
    target_url = normalize_target_url(payload.target)
    link = await create_short_link(db, target_url)
    base_url = str(request.base_url).rstrip("/")
    return URLResponse(
        code=link.short_code,
        target=link.target_url,
        short_url=f"{base_url}/{link.short_code}",
    )


@router.get("/{code}")
async def redirect(
    code: str,
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """Редирект по короткому коду на целевой URL."""
    link = await get_link_by_code(db, code)
    if link is None:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return RedirectResponse(link.target_url)
