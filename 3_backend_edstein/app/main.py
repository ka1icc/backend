"""FastAPI application entry point."""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response

from app.database import init_db
from app.routers import health, weather

_STATIC_DIR = Path(__file__).resolve().parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: create DB tables. Shutdown: none."""
    try:
        await init_db()
    except Exception:
        pass
    yield


app = FastAPI(
    title="Weather Backend",
    description="Backend для погоды на базе AccuWeather API (Казань). "
    "Swagger: /docs. Ожидаемая нагрузка ~5 RPS.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request, exc: Exception) -> JSONResponse:
    """Необработанное исключение → 503. HTTPException отдаём как есть."""
    if isinstance(exc, HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
        )
    return JSONResponse(
        status_code=503,
        content={"detail": "Service temporarily unavailable"},
    )


app.include_router(health.router)
app.include_router(weather.router)


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Браузер запрашивает иконку вкладки — отвечаем 204, без 404 в логах."""
    return Response(status_code=204)


@app.get("/", include_in_schema=False)
async def index():
    """Minimalist web UI (blue, black, gray)."""
    path = _STATIC_DIR / "index.html"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Not found")
    return FileResponse(path, media_type="text/html")
