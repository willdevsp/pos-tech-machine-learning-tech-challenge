"""Logging configuration using loguru."""

import sys

from loguru import logger


def configure_logging(level: str = "INFO") -> None:
    """Configures the global logger formatting.

    Args:
        level: Minimum severity level to log (e.g. "DEBUG", "INFO", "WARNING").
    """
    logger.remove()
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level:7}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=level,
    )
    logger.info(f"Logging configured at level {level}")
