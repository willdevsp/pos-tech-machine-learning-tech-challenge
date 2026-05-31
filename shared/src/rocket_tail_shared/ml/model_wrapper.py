"""MLflow custom PythonModel wrapper encapsulating preprocessing and PyTorch inference."""

from typing import Any

import mlflow.pyfunc
import pandas as pd
import torch

from rocket_tail_shared.ml.model_factory import ModelFactory


class RocketTailModelWrapper(mlflow.pyfunc.PythonModel):
    """Custom MLflow PythonModel wrapping preprocessing and PyTorch model.

    Enables end-to-end serving directly from MLflow loader without training-serving skew.
    """

    def __init__(
        self,
        model_state_dict: dict[str, Any],
        model_config: dict[str, Any],
        preprocessor: Any,
    ) -> None:
        """Initializes the wrapper.

        Args:
            model_state_dict: Dictionary containing PyTorch model weights.
            model_config: Dictionary containing model architecture configuration.
            preprocessor: Fitted scikit-learn Pipeline / DataPreprocessor.
        """
        self.model_state_dict = model_state_dict
        self.model_config = model_config
        self.preprocessor = preprocessor
        self.model = None

    def load_context(self, context: Any) -> None:
        """Loads the PyTorch model inside serving context.

        Args:
            context: MLflow context object.
        """
        # Recreate PyTorch model structure and load state dict
        self.model = ModelFactory.create_model("hybrid", self.model_config)
        self.model.load_state_dict(self.model_state_dict)
        self.model.eval()

    def predict(self, context: Any, model_input: pd.DataFrame) -> list[int]:
        """Applies preprocessing, runs forward pass, and ranks recommended item IDs.

        Args:
            context: MLflow context.
            model_input: Pandas DataFrame containing raw candidates (visitorid, itemid, etc.).

        Returns:
            Ranked list of recommended item IDs.
        """
        if self.model is None:
            # Lazy initialize if load_context wasn't called (e.g. during local tests)
            self.load_context(None)

        # 1. Run preprocessing pipeline on model_input
        processed_df = self.preprocessor.transform(model_input)

        # 2. Extract values and convert to PyTorch tensors
        user_ids = torch.tensor(processed_df["visitorid"].values, dtype=torch.long)
        item_ids = torch.tensor(processed_df["itemid"].values, dtype=torch.long)

        # Content features: user_activity, item_popularity, hour
        content_cols = ["user_activity", "item_popularity", "hour"]
        # Ensure all columns exist, fillna if necessary
        for col in content_cols:
            if col not in processed_df.columns:
                processed_df[col] = 0.0

        content_features = torch.tensor(
            processed_df[content_cols].values, dtype=torch.float
        )

        # 3. Model forward pass
        with torch.no_grad():
            scores = self.model(user_ids, item_ids, content_features).squeeze(1).numpy()

        # 4. Generate ranked recommendation list
        processed_df["score"] = scores
        # Sort items descending by predicted score
        ranked_df = processed_df.sort_values(by="score", ascending=False)
        return ranked_df["itemid"].unique().tolist()
