"""Factory Pattern for creating recommendation models."""

from typing import Any

import torch.nn as nn

from rocket_tail_shared.models.hybrid import HybridNN


class ModelFactory:
    """Factory to create different variations of the recommendation models.

    Supports:
        - "mlp_collaborative": User-item collaborative filtering embeddings only.
        - "mlp_content_based": User/item metadata features only.
        - "hybrid": Joint embeddings and content features.
    """

    @staticmethod
    def create_model(model_type: str, config: dict[str, Any]) -> nn.Module:
        """Instantiates and returns a configured recommendation model.

        Args:
            model_type: Name of the model structure ("mlp_collaborative", "mlp_content_based", "hybrid").
            config: Configuration parameters such as num_users, num_items, dims.

        Returns:
            An instance of torch.nn.Module.

        Raises:
            ValueError: If an unsupported model_type is provided.
        """
        model_type = model_type.lower()

        # Extract common settings with fallbacks
        num_users = config.get("num_users", 0)
        num_items = config.get("num_items", 0)
        user_emb_dim = config.get("user_emb_dim", 32)
        item_emb_dim = config.get("item_emb_dim", 32)
        content_feature_dim = config.get("content_feature_dim", 0)
        hidden_dims = config.get("hidden_dims", [128, 64, 32])
        dropout_rate = config.get("dropout_rate", 0.2)

        if model_type == "mlp_collaborative":
            # Collaborative filtering only: disable content features
            return HybridNN(
                num_users=num_users,
                num_items=num_items,
                user_emb_dim=user_emb_dim,
                item_emb_dim=item_emb_dim,
                content_feature_dim=0,
                hidden_dims=hidden_dims,
                dropout_rate=dropout_rate,
            )

        elif model_type == "mlp_content_based":
            # Content-based filtering only: disable user/item ID embeddings
            if content_feature_dim <= 0:
                raise ValueError(
                    "content_feature_dim must be > 0 for mlp_content_based"
                )
            return HybridNN(
                num_users=0,
                num_items=0,
                user_emb_dim=0,
                item_emb_dim=0,
                content_feature_dim=content_feature_dim,
                hidden_dims=hidden_dims,
                dropout_rate=dropout_rate,
            )

        elif model_type == "hybrid":
            # Hybrid model using both ID embeddings and content features
            if content_feature_dim <= 0:
                raise ValueError("content_feature_dim must be > 0 for hybrid")
            return HybridNN(
                num_users=num_users,
                num_items=num_items,
                user_emb_dim=user_emb_dim,
                item_emb_dim=item_emb_dim,
                content_feature_dim=content_feature_dim,
                hidden_dims=hidden_dims,
                dropout_rate=dropout_rate,
            )

        else:
            raise ValueError(f"Unsupported model_type: {model_type}")
