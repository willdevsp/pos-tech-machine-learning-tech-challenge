"""Recommendation service logic handling model loading and predictions."""

import os
import threading
import time

import mlflow
import pandas as pd
from loguru import logger

from rocket_tail_shared.ml.baselines import PopularityBaseline


class RecommendationService:
    """Service class managing inference, MLflow model loading, and fallback baselines."""

    def __init__(self) -> None:
        """Initializes the Recommendation Service and attempts to load the MLflow model."""
        self.model = None
        self.fallback_model = PopularityBaseline()

        # Seed the popularity fallback model with dummy mock items for initial deploy state
        self.fallback_model.fit([2001, 2001, 2001, 2002, 2002, 2003])

        # Track currently loaded version to avoid unnecessary reloads
        self.current_model_version = None

        # Initial synchronous model load
        self._load_model()

        # Start background polling thread for dynamic model updates
        self.polling_thread = threading.Thread(target=self._poll_model_updates, daemon=True)
        self.polling_thread.start()

    def _load_model(self) -> None:
        """Loads the MLflow model from the tracking server."""
        try:
            # Use MLflow Client to check for the version with stage=Production tag
            tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
            mlflow.set_tracking_uri(tracking_uri)            

            model_uri = f"models:/rocket_tail_model@Production"
            logger.info(f"Attempting to load MLflow model from URI: {model_uri}")
            new_model = mlflow.sklearn.load_model(model_uri)
            self.model = new_model            
            logger.info(f"Custom end-to-end MLflow model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load MLflow model from tag stage=Production. Error: {e}")
            raise e

    def _poll_model_updates(self) -> None:
        """Periodically polls MLflow for model updates."""
        while True:
            time.sleep(300)  # Check every 5 minutes
            logger.debug("Polling MLflow for new model versions...")
            self._load_model()

    def get_recommendations(self, visitorid: int, k: int = 10) -> list[int]:
        """Retrieves top-K recommended item IDs for a given user.

        Args:
            visitorid: The unique identifier for the user.
            k: The maximum number of recommendations to retrieve.

        Returns:
            List of recommended item IDs.
        """
        logger.info(f"Generating top-{k} recommendations for visitor: {visitorid}")

        if self.model is None:
            # Fallback to popularity baseline
            return self.fallback_model.predict(k=k)

        try:
            # Obtain candidate items to score (e.g. from the popularity baseline)
            candidate_items = self.fallback_model.predict(k=20)
            if not candidate_items:
                candidate_items = [2001, 2002, 2003, 2004, 2005]

            # Construct raw DataFrame to send to MLflow model (contains preprocessing steps)
            candidates_df = pd.DataFrame({
                "visitorid": [visitorid] * len(candidate_items),
                "itemid": candidate_items,
                "timestamp": [1433221332] * len(candidate_items),
                "event": ["view"] * len(candidate_items),
            })

            # Score and rank candidates end-to-end (preprocessing + neural model predict)
            logger.debug("Running end-to-end custom MLflow PyFunc model predict...")
            ranked_recs = self.model.predict(candidates_df)
            return ranked_recs[:k]
        except Exception as e:
            logger.error(f"Error during MLflow model inference: {e}. Falling back to baseline.")
            return self.fallback_model.predict(k=k)
