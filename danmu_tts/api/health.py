"""Health check endpoints."""

from fastapi import APIRouter

from ..models.responses import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthResponse)
async def root_health_check():
    """Root health check endpoint."""
    return HealthResponse(
        status="ok",
        message="Danmu TTS Server is running"
    )


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="ok", 
        message="Danmu TTS Server is running"
    )