"""CRUD-операции для коротких ссылок."""

import secrets
import string

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models import ShortLink


def generate_code(length: int = 6) -> str:
    """Генерирует случайный буквенно-цифровой код заданной длины."""
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


async def create_short_link(
    db: AsyncSession,
    target_url: str,
) -> ShortLink:
    """
    Создаёт короткую ссылку для заданного URL.
    Подбирает уникальный код, пока не найдётся свободный.
    """
    existing_link = True
    while existing_link is not None:
        code = generate_code()
        result = await db.execute(
            select(ShortLink).where(ShortLink.short_code == code)
        )
        existing_link = result.scalar_one_or_none()

    link = ShortLink(short_code=code, target_url=target_url)
    db.add(link)
    await db.commit()
    await db.refresh(link)
    return link


async def get_link_by_code(db: AsyncSession, short_code: str) -> ShortLink | None:
    """Возвращает запись по короткому коду или None."""
    result = await db.execute(
        select(ShortLink).where(ShortLink.short_code == short_code)
    )
    return result.scalar_one_or_none()
