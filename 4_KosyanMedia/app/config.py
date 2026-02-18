"""Application configuration loaded from environment."""

import os
from pathlib import Path
from urllib.parse import quote, quote_plus, urlparse

from dotenv import load_dotenv

BASE_DIR: Path = Path(__file__).resolve().parent.parent
_env_path: Path = BASE_DIR / '.env'

# Load .env with UTF-8 first; on Russian/other Windows it may be saved as CP1251
if _env_path.exists():
    try:
        load_dotenv(_env_path, encoding='utf-8')
    except UnicodeDecodeError:
        load_dotenv(_env_path, encoding='cp1251')
else:
    load_dotenv()

# Avoid psycopg2 UnicodeDecodeError on Windows (DSN/env encoding issues)
os.environ.setdefault('PGCLIENTENCODING', 'UTF8')

_DEFAULT_URL: str = 'postgresql://postgres:postgres@127.0.0.1:5432/via_compare'


def _to_ascii(value: str) -> str:
    """Leave only ASCII to avoid encoding errors in psycopg2/libpq on Windows."""
    return value.encode('ascii', errors='replace').decode('ascii')


def _build_ascii_database_url() -> str:
    """Build a strictly ASCII DATABASE_URL to avoid psycopg2 UnicodeDecodeError on Windows."""
    # Вариант 1: отдельные переменные — собираем URL только из них (пароль WinSer2016 и т.д.)
    host = os.getenv('PGHOST')
    user = os.getenv('PGUSER')
    password = os.getenv('PGPASSWORD')
    port = os.getenv('PGPORT', '5432')
    db = os.getenv('PGDATABASE', 'via_compare')
    if host and user and password is not None:
        host = _to_ascii(host)
        user = quote(_to_ascii(user), safe='')
        password = quote(_to_ascii(password), safe='')
        port = _to_ascii(port)
        db = _to_ascii(db)
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'

    # Вариант 2: DATABASE_URL — разбираем и пересобираем в ASCII
    raw: str | None = os.getenv('DATABASE_URL')
    if not raw:
        return _DEFAULT_URL
    try:
        parsed = urlparse(raw)
        if not parsed.hostname:
            return _DEFAULT_URL
        user = quote(parsed.username or 'postgres', safe='')
        password = quote(parsed.password or 'postgres', safe='')
        host = _to_ascii(parsed.hostname)
        port = parsed.port or 5432
        db = (parsed.path or '/via_compare').strip('/') or 'via_compare'
        db = _to_ascii(db)
        return f'postgresql://{user}:{password}@{host}:{port}/{db}'
    except Exception:
        return _DEFAULT_URL


DATABASE_URL: str = _build_ascii_database_url()

XML_DIR: Path = Path(
    os.getenv('XML_DIR', str(BASE_DIR)),
)
