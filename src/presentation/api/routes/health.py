from fastapi import APIRouter

from src.presentation.api.schemas.responses import HealthResponse

router = APIRouter(prefix="/api", tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="AI Photo Generation"
    )
