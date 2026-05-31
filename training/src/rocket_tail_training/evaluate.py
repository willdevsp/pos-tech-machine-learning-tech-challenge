"""Evaluation script comparing trained models against baselines."""

from typing import Any

from loguru import logger

from rocket_tail_shared.ml.baselines import PopularityBaseline
from rocket_tail_shared.ml.metrics import ndcg_at_k, precision_at_k, recall_at_k
from rocket_tail_shared.utils.logging import configure_logging


def evaluate_predictions(
    actual: list[Any],
    predicted: list[Any],
    k: int = 10,
) -> dict[str, float]:
    """Calculates all comparison metrics for evaluation.

    Args:
        actual: List of ground-truth relevant items.
        predicted: List of recommended items in rank order.
        k: Maximum recommendations cutoff.

    Returns:
        Dictionary of computed metric names mapped to their float scores.
    """
    logger.info(f"Evaluating predictions at K={k}")
    return {
        "precision": precision_at_k(actual, predicted, k),
        "recall": recall_at_k(actual, predicted, k),
        "ndcg": ndcg_at_k(actual, predicted, k),
    }


def main() -> None:
    """Main baseline evaluation simulation."""
    # Dummy verification run
    actual = [101, 102, 103]
    predicted = [105, 101, 203, 102, 103, 999]

    # Evaluate
    metrics = evaluate_predictions(actual, predicted, k=5)
    logger.info(f"Computed evaluation metrics: {metrics}")

    # Verify baseline setup
    baseline = PopularityBaseline()
    baseline.fit([1, 1, 1, 2, 2, 3])
    recs = baseline.predict(k=2)
    logger.info(f"Popularity baseline recommendations: {recs}")


if __name__ == "__main__":
    configure_logging()
    main()
