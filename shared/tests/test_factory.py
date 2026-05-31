"""Tests for ModelFactory implementation."""

import pytest
import torch

from rocket_tail_shared.ml.model_factory import ModelFactory
from rocket_tail_shared.models.hybrid import HybridNN


def test_create_model_collaborative() -> None:
    """Verifies collaborative model creation and structure."""
    config = {
        "num_users": 100,
        "num_items": 50,
        "user_emb_dim": 16,
        "item_emb_dim": 16,
        "hidden_dims": [32, 16],
    }

    model = ModelFactory.create_model("mlp_collaborative", config)
    assert isinstance(model, HybridNN)
    assert model.user_embedding is not None
    assert model.item_embedding is not None

    # Test forward pass with fake tensors
    user_ids = torch.randint(0, 100, (8,))
    item_ids = torch.randint(0, 50, (8,))
    content_feats = torch.zeros((8, 0))  # Empty side features

    out = model(user_ids, item_ids, content_feats)
    assert out.shape == (8, 1)


def test_create_model_content_based() -> None:
    """Verifies content-based model creation and structure."""
    config = {
        "content_feature_dim": 10,
        "hidden_dims": [32, 16],
    }

    model = ModelFactory.create_model("mlp_content_based", config)
    assert isinstance(model, HybridNN)
    assert model.user_embedding is None
    assert model.item_embedding is None

    # Test forward pass
    user_ids = torch.zeros((8,), dtype=torch.long)
    item_ids = torch.zeros((8,), dtype=torch.long)
    content_feats = torch.randn((8, 10))

    out = model(user_ids, item_ids, content_feats)
    assert out.shape == (8, 1)


def test_create_model_hybrid() -> None:
    """Verifies hybrid model creation and structure."""
    config = {
        "num_users": 100,
        "num_items": 50,
        "user_emb_dim": 16,
        "item_emb_dim": 16,
        "content_feature_dim": 5,
        "hidden_dims": [32, 16],
    }

    model = ModelFactory.create_model("hybrid", config)
    assert isinstance(model, HybridNN)
    assert model.user_embedding is not None
    assert model.item_embedding is not None

    # Test forward pass
    user_ids = torch.randint(0, 100, (8,))
    item_ids = torch.randint(0, 50, (8,))
    content_feats = torch.randn((8, 5))

    out = model(user_ids, item_ids, content_feats)
    assert out.shape == (8, 1)


def test_invalid_model_type() -> None:
    """Ensures factory raises error on invalid model types."""
    with pytest.raises(ValueError, match="Unsupported model_type"):
        ModelFactory.create_model("invalid_type", {})
