"""FastAPI application entry point for RocketTail Recommendation service."""

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from loguru import logger

from rocket_tail_api.config import api_settings
from rocket_tail_api.models import RecommendRequest, RecommendResponse
from rocket_tail_api.service import RecommendationService
from rocket_tail_shared.utils.logging import configure_logging

# Global service instance holder
service: RecommendationService = None  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for FastAPI startup/shutdown tasks."""
    global service
    configure_logging()
    logger.info(f"Starting {api_settings.app_name} on env: {api_settings.env}")
    service = RecommendationService()
    yield
    logger.info(f"Shutting down {api_settings.app_name}")


app = FastAPI(
    title=api_settings.app_name,
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health", status_code=status.HTTP_200_OK)
def health_check() -> dict[str, str]:
    """Verification health check endpoint.

    Returns:
        Dictionary indicating status is "healthy".
    """
    return {"status": "healthy", "model_loaded": str(service.model is not None)}


@app.post(
    "/recommend",
    response_model=RecommendResponse,
    status_code=status.HTTP_200_OK,
)
def recommend(request: RecommendRequest) -> RecommendResponse:
    """Recommends relevant items for the specified user ID.

    Args:
        request: RecommendRequest containing visitorid and k.

    Returns:
        RecommendResponse containing visitorid and recommendations.

    Raises:
        HTTPException: 500 error if service fails to respond.
    """
    try:
        recommendations = service.get_recommendations(
            visitorid=request.visitorid,
            k=request.k or 10,
        )
        return RecommendResponse(
            visitorid=request.visitorid,
            recommendations=recommendations,
        )
    except Exception as e:
        logger.error(f"Error handling recommendation request: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error generating recommendations.",
        )
