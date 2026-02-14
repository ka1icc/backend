"""Health check endpoint."""
from fastapi import APIRouter

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    """Status of the backend. Always OK."""
    return {"status": "OK"}
