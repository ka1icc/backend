import secrets
import string

from sqlalchemy.orm import Session

from app.domain.models import URL


def generate_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))


def create_short_url(db: Session, target: str) -> URL:
    while True:
        code = generate_code()
        existing_url = db.query(URL).filter(URL.code == code).first()
        if existing_url is None:
            break

    url = URL(code=code, target=target)
    db.add(url)
    db.commit()
    db.refresh(url)
    return url


def get_url_by_code(db: Session, code: str) -> URL | None:
    return db.query(URL).filter(URL.code == code).first()
