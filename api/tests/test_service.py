"""Tests for the recommendation service logic."""

from rocket_tail_api.service import RecommendationService


def test_get_recommendations_fallback() -> None:
    """Verifies service falls back to popularity model if model is not loaded."""
    service = RecommendationService()

    # Model is None initially in test environment since weights don't exist
    assert service.model is None

    recs = service.get_recommendations(visitorid=123, k=3)
    assert len(recs) == 3
    assert set(recs).issubset({2001, 2002, 2003})
