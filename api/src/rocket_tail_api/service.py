"""Recommendation service logic handling model loading and predictions."""

import os
import threading
import time

import mlflow.pyfunc
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
        self.model_alias_uri = "models:/rocket_tail_model@Production"

        # Initial synchronous model load
        self._load_model()
        
        # Start background polling thread for dynamic model updates
        self.polling_thread = threading.Thread(target=self._poll_model_updates, daemon=True)
        self.polling_thread.start()

    def _load_model(self) -> None:
        """Loads the MLflow model from the tracking server."""
        try:
            logger.info(f"Attempting to load MLflow model from URI: {self.model_alias_uri}")
            mlflow.pyfunc.set_env({})  # Avoid environment restore issues in this context
            
            # Use MLflow Client to check if there is a new version before downloading the entire model
            from mlflow.tracking import MlflowClient
            try:
                client = MlflowClient()
                model_version_details = client.get_model_version_by_alias("rocket_tail_model", "Production")
                latest_version = model_version_details.version
                
                if self.current_model_version == latest_version:
                    logger.debug("Model version unchanged. Skipping reload.")
                    return
            except Exception as e:
                logger.debug(f"Could not check version alias, continuing to load: {e}")
                latest_version = None
                
            new_model = mlflow.pyfunc.load_model(self.model_alias_uri)
            self.model = new_model
            self.current_model_version = latest_version
            logger.info(f"Custom end-to-end MLflow model loaded successfully. Version: {self.current_model_version}")
        except Exception as e:
            logger.error(f"Failed to load MLflow model from {self.model_alias_uri}. Error: {e}")

            # Fallback to local files if MLflow server load failed
            if self.model is None:
                self._load_fallback_model()
                
    def _load_fallback_model(self) -> None:
        """Loads local fallback model."""
        run_id_file = "models/latest_run_id.txt"
        model_uri = None

        if os.path.exists(run_id_file):
            with open(run_id_file) as f:
                run_id = f.read().strip()
                if run_id:
                    model_uri = f"runs:/{run_id}/model"
                    
        if model_uri:
            try:
                logger.info(f"Loading local fallback MLflow model from URI: {model_uri}")
                mlflow.pyfunc.set_env({})
                self.model = mlflow.pyfunc.load_model(model_uri)
                logger.info("Local fallback model loaded successfully.")
            except Exception as ex:
                logger.error(f"Failed to load fallback MLflow model from {model_uri}. Error: {ex}")
                logger.warning("Inference will use popularity fallback model.")
        else:
            logger.warning("No local fallback run ID found. Inference will use popularity fallback model.")

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
