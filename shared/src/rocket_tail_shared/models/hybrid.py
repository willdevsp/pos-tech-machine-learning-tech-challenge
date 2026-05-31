"""PyTorch deep neural network model architectures for RocketTail recommendation system."""

import torch
import torch.nn as nn


class EmbeddingLayer(nn.Module):
    """Embedding wrapper layer for user and item IDs.

    Handles high-cardinality categorical features by mapping them to dense vectors.
    """

    def __init__(self, num_embeddings: int, embedding_dim: int) -> None:
        """Initializes the embedding layer.

        Args:
            num_embeddings: Vocabulary size (number of unique categories).
            embedding_dim: Dimension size of the embedding vector.
        """
        super().__init__()
        self.embedding = nn.Embedding(
            num_embeddings=num_embeddings,
            embedding_dim=embedding_dim,
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass.

        Args:
            x: Integer tensor of shape (batch_size,).

        Returns:
            Dense embedding tensor of shape (batch_size, embedding_dim).
        """
        return self.embedding(x)


class HybridNN(nn.Module):
    """Deep Hybrid Neural Network model for recommendations.

    Combines collaborative filtering (user and item ID embeddings)
    with content-based features (demographics, context, item metadata).
    """

    def __init__(
        self,
        num_users: int,
        num_items: int,
        user_emb_dim: int,
        item_emb_dim: int,
        content_feature_dim: int,
        hidden_dims: list[int] | None = None,
        dropout_rate: float = 0.2,
    ) -> None:
        """Initializes the Hybrid Neural Network.

        Args:
            num_users: Total number of unique users.
            num_items: Total number of unique items.
            user_emb_dim: Size of user embedding vector (0 to disable user embedding).
            item_emb_dim: Size of item embedding vector (0 to disable item embedding).
            content_feature_dim: Dimension of additional content/side features (0 to disable).
            hidden_dims: List of hidden layers dimensions (defaults to [128, 64, 32]).
            dropout_rate: Dropout rate for regularization.
        """
        super().__init__()
        if hidden_dims is None:
            hidden_dims = [128, 64, 32]

        self.user_embedding = EmbeddingLayer(num_users, user_emb_dim) if user_emb_dim > 0 else None
        self.item_embedding = EmbeddingLayer(num_items, item_emb_dim) if item_emb_dim > 0 else None

        # Input dimension is user_emb + item_emb + content_features
        input_dim = user_emb_dim + item_emb_dim + content_feature_dim
        if input_dim <= 0:
            raise ValueError("Input dimension must be greater than zero.")

        layers: list[nn.Module] = []
        prev_dim = input_dim

        for h_dim in hidden_dims:
            layers.append(nn.Linear(prev_dim, h_dim))
            layers.append(nn.BatchNorm1d(h_dim))
            layers.append(nn.ReLU())
            layers.append(nn.Dropout(p=dropout_rate))
            prev_dim = h_dim

        # Final regression or classification layer
        layers.append(nn.Linear(prev_dim, 1))

        self.mlp = nn.Sequential(*layers)

    def forward(
        self,
        user_ids: torch.Tensor,
        item_ids: torch.Tensor,
        content_features: torch.Tensor,
    ) -> torch.Tensor:
        """Forward pass of the Hybrid Neural Network.

        Args:
            user_ids: Tensor of user indices of shape (batch_size,).
            item_ids: Tensor of item indices of shape (batch_size,).
            content_features: Float tensor of side features of shape (batch_size, content_dim).

        Returns:
            Output prediction tensor (scores) of shape (batch_size, 1).
        """
        features_to_concat = []
        if self.user_embedding is not None:
            features_to_concat.append(self.user_embedding(user_ids))
        if self.item_embedding is not None:
            features_to_concat.append(self.item_embedding(item_ids))
        if content_features.shape[1] > 0:
            features_to_concat.append(content_features)

        # Concatenate collaborative embeddings and content-based features
        x = torch.cat(features_to_concat, dim=1)

        return self.mlp(x)
