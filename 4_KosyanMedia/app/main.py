"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api import router
from app.database import Base, engine

app = FastAPI(
    title='Via.com Route Comparison',
    description=(
        'Comparison of flight routes '
        'from Via.com API responses'
    ),
)

Base.metadata.create_all(bind=engine)

app.include_router(router)
