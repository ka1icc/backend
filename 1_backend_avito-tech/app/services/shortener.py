"""Бизнес-логика сокращения URL."""

ALLOWED_SCHEMES = ("http://", "https://")


def is_valid_target_url(raw_url: str) -> bool:
    """Проверяет, что строка — допустимый целевой URL (http/https)."""
    return raw_url.strip().startswith(ALLOWED_SCHEMES)


def normalize_target_url(raw_url: str) -> str:
    """Возвращает URL без завершающего слэша для единообразия (опционально)."""
    return raw_url.strip().rstrip("/")
