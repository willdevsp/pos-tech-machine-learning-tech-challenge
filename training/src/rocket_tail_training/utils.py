"""Helper utilities for training workflows."""

import os
from typing import Any

import torch


def save_checkpoint(state: dict[str, Any], filepath: str) -> None:
    """Saves training checkpoint.

    Args:
        state: Dictionary containing training state (epoch, weights, optimizer state).
        filepath: Target filepath to save checkpoint file.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    torch.save(state, filepath)


def load_checkpoint(filepath: str) -> dict[str, Any]:
    """Loads a previously saved training checkpoint.

    Args:
        filepath: Filepath of the checkpoint to load.

    Returns:
        Dictionary of loaded checkpoint details.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Checkpoint file not found: {filepath}")
    return torch.load(filepath)
