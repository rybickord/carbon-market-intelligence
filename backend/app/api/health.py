"""
Health check endpoint.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Carbon Market Intelligence API",
        "version": "1.0.0"
    }
