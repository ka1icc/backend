import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.crud import create_short_url, get_url_by_code
from app.db import Base, engine, get_db
from app.domain.schemas import URLCreate, URLResponse

Base.metadata.create_all(bind=engine)

app = FastAPI(title="URL Shortener API")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def root() -> FileResponse:
    html_path = os.path.join("app", "static", "index.html")
    return FileResponse(html_path)

@app.post("/shorten", response_model=URLResponse)
def shorten(
    payload: URLCreate,
    request: Request,
    db: Session = Depends(get_db),
) -> URLResponse:
    if not payload.target.startswith(("http://", "https://")):
        raise HTTPException(
            status_code=400,
            detail="Invalid URL",
        )
    url = create_short_url(db, payload.target)
    base_url = str(request.base_url).rstrip('/')
    return URLResponse(
        code=url.code,
        target=url.target,
        short_url=f"{base_url}/{url.code}",
    )

@app.get("/{code}")
def redirect(
    code: str,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    url = get_url_by_code(db, code)
    if not url:
        raise HTTPException(
            status_code=404,
            detail="Not found",
        )
    return RedirectResponse(url.target)
