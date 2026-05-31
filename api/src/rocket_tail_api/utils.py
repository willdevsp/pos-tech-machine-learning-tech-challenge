"""Helper utilities for RocketTail REST API."""

from typing import Any


def format_api_error(message: str, code: int) -> dict[str, Any]:
    """Helper to format JSON error payloads.

    Args:
        message: Descriptive error message.
        code: HTTP status code or custom internal code.

    Returns:
        Dictionary of the formatted error.
    """
    return {"error": {"message": message, "code": code}}
