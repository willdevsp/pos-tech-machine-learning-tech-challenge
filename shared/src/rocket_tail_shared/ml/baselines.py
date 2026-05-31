"""Baseline model implementations for recommendation comparison."""

import numpy as np


class PopularityBaseline:
    """Popularity-based recommendation baseline.

    Recommends the most frequently interacted items to all users.
    """

    def __init__(self) -> None:
        """Initializes the baseline."""
        self.popular_items: list[int] = []

    def fit(self, item_interactions: list[int]) -> None:
        """Fits the model by counting item interaction frequencies.

        Args:
            item_interactions: List of item IDs representing interactions.
        """
        items, counts = np.unique(item_interactions, return_counts=True)
        # Sort items in descending order of counts
        sorted_indices = np.argsort(-counts)
        self.popular_items = items[sorted_indices].tolist()

    def predict(self, k: int = 10) -> list[int]:
        """Predicts the top-K recommended items.

        Args:
            k: Number of recommendations to return.

        Returns:
            List of the top-K item IDs.
        """
        return self.popular_items[:k]


class RandomBaseline:
    """Random recommendation baseline.

    Recommends random items from the vocabulary of known items.
    """

    def __init__(self) -> None:
        """Initializes the baseline."""
        self.unique_items: list[int] = []

    def fit(self, item_interactions: list[int]) -> None:
        """Fits the model by gathering the unique item IDs.

        Args:
            item_interactions: List of item IDs.
        """
        self.unique_items = list(set(item_interactions))

    def predict(self, k: int = 10) -> list[int]:
        """Predicts random top-K recommendations.

        Args:
            k: Number of recommendations to return.

        Returns:
            List of K randomly selected item IDs.
        """
        if not self.unique_items:
            return []
        size = min(k, len(self.unique_items))
        return list(np.random.choice(self.unique_items, size=size, replace=False))
