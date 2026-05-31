"""Evaluation metrics for recommendation systems."""

from typing import Any

import numpy as np


def precision_at_k(actual: list[Any], predicted: list[Any], k: int) -> float:
    """Calculates Precision at K.

    Precision@K is the fraction of recommended items in the top-K that are relevant.

    Args:
        actual: List of ground-truth relevant items.
        predicted: List of recommended items in order of relevance.
        k: Cut-off value.

    Returns:
        Precision@K score as a float.
    """
    if not predicted or not actual or k <= 0:
        return 0.0

    pred_k = predicted[:k]
    num_relevant = sum(1 for item in pred_k if item in actual)
    return num_relevant / k


def recall_at_k(actual: list[Any], predicted: list[Any], k: int) -> float:
    """Calculates Recall at K.

    Recall@K is the fraction of ground-truth relevant items that are in the top-K recommendations.

    Args:
        actual: List of ground-truth relevant items.
        predicted: List of recommended items in order of relevance.
        k: Cut-off value.

    Returns:
        Recall@K score as a float.
    """
    if not predicted or not actual or k <= 0:
        return 0.0

    pred_k = predicted[:k]
    num_relevant = sum(1 for item in pred_k if item in actual)
    return num_relevant / len(actual)


def ndcg_at_k(actual: list[Any], predicted: list[Any], k: int) -> float:
    """Calculates Normalized Discounted Cumulative Gain (NDCG) at K.

    Measures the quality of ranking in top-K recommendations.

    Args:
        actual: List of ground-truth relevant items.
        predicted: List of recommended items in order of relevance.
        k: Cut-off value.

    Returns:
        NDCG@K score between 0.0 and 1.0.
    """
    if not predicted or not actual or k <= 0:
        return 0.0

    pred_k = predicted[:k]
    # Binary relevance: 1 if recommended item is in actual, 0 otherwise
    relevance = [1.0 if item in actual else 0.0 for item in pred_k]

    # Calculate Discounted Cumulative Gain (DCG)
    dcg = sum(rel / np.log2(idx + 2) for idx, rel in enumerate(relevance))

    # Calculate Ideal DCG (IDCG) - all actual items ranked at top
    ideal_relevance = sorted([1.0] * min(len(actual), k), reverse=True)
    idcg = sum(rel / np.log2(idx + 2) for idx, rel in enumerate(ideal_relevance))

    if idcg == 0.0:
        return 0.0

    return dcg / idcg


def mean_reciprocal_rank(actual: list[Any], predicted: list[Any]) -> float:
    """Calculates Reciprocal Rank (RR) for a single query.

    Calculates the reciprocal of the rank of the first correct recommendation.

    Args:
        actual: List of ground-truth relevant items.
        predicted: List of recommended items.

    Returns:
        Reciprocal rank score as a float.
    """
    if not predicted or not actual:
        return 0.0

    for idx, item in enumerate(predicted):
        if item in actual:
            return 1.0 / (idx + 1)

    return 0.0
