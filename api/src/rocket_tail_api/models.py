"""Pydantic request and response schemas for FastAPI endpoints."""


from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    """Schema representing a recommendation request."""

    visitorid: int = Field(..., description="Unique user/visitor identifier.")
    k: int | None = Field(
        default=10,
        description="Number of recommendations to return.",
        gt=0,
        le=100,
    )


class RecommendResponse(BaseModel):
    """Schema representing a recommendation response."""

    visitorid: int = Field(..., description="Unique user/visitor identifier.")
    recommendations: list[int] = Field(
        ...,
        description="Ranked list of recommended item IDs.",
    )
