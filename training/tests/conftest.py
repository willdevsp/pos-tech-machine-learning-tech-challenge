"""Pytest configuration for the training package."""

import os
import sys

# Add src/ to sys.path so rocket_tail_training imports correctly
sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")),
)
