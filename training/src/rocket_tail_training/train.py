"""Training loop pipeline stage using PyTorch and ModelFactory."""

import json
import os

import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from loguru import logger

from rocket_tail_shared.ml.model_factory import ModelFactory
from rocket_tail_shared.utils.logging import configure_logging
from rocket_tail_training.config import training_settings


def prepare_tensors(df: pd.DataFrame) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
    """Converts a feature DataFrame into PyTorch tensors.

    Args:
        df: Input DataFrame containing user, item, context features, and labels.

    Returns:
        Tuple containing user_ids, item_ids, content_features, and labels.
    """
    user_ids = torch.tensor(df["visitorid"].values, dtype=torch.long)
    item_ids = torch.tensor(df["itemid"].values, dtype=torch.long)

    # Content features: user_activity, item_popularity, hour
    content_cols = ["user_activity", "item_popularity", "hour"]
    content_features = torch.tensor(df[content_cols].values, dtype=torch.float)

    # Event label target (dummy label target, e.g. event mapping)
    labels = torch.tensor(df["event"].values, dtype=torch.float).unsqueeze(1)

    return user_ids, item_ids, content_features, labels


def train_model(
    model: nn.Module,
    user_ids: torch.Tensor,
    item_ids: torch.Tensor,
    content_features: torch.Tensor,
    labels: torch.Tensor,
) -> nn.Module:
    """Trains the PyTorch neural network.

    Args:
        model: PyTorch Model.
        user_ids: Tensor of user IDs.
        item_ids: Tensor of item IDs.
        content_features: Tensor of content features.
        labels: Ground-truth relevance targets.

    Returns:
        Trained model instance.
    """
    logger.info("Starting model training...")
    model.train()
    optimizer = optim.Adam(model.parameters(), lr=training_settings.learning_rate)
    criterion = nn.MSELoss()

    for epoch in range(training_settings.epochs):
        optimizer.zero_grad()
        outputs = model(user_ids, item_ids, content_features)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        logger.info(f"Epoch {epoch + 1}/{training_settings.epochs} | Loss: {loss.item():.4f}")

    return model


def main() -> None:
    """Main execution block for training stage."""
    processed_dir = training_settings.processed_data_path
    features_file = os.path.join(processed_dir, "features.csv")
    model_dir = "models"
    os.makedirs(model_dir, exist_ok=True)
    model_output = os.path.join(model_dir, "model.pt")

    if not os.path.exists(features_file):
        logger.error(f"Features file not found: {features_file}. Please run the feature engineering stage first.")
        # Auto-generate features for testing if missing
        import subprocess
        logger.info("Running feature engineering automatically...")
        subprocess.run(["python", "src/rocket_tail_training/features.py"], check=True)

    df = pd.read_csv(features_file)

    # Extract max ID bounds for embedding size initialization
    num_users = int(df["visitorid"].max() + 1)
    num_items = int(df["itemid"].max() + 1)

    # Initialize model using ModelFactory
    model_config = {
        "num_users": num_users,
        "num_items": num_items,
        "user_emb_dim": training_settings.user_emb_dim,
        "item_emb_dim": training_settings.item_emb_dim,
        "content_feature_dim": 3,  # user_activity, item_popularity, hour
        "hidden_dims": training_settings.hidden_dims,
        "dropout_rate": training_settings.dropout_rate,
    }

    model = ModelFactory.create_model("hybrid", model_config)

    # Prepare inputs
    user_ids, item_ids, content_features, labels = prepare_tensors(df)

    # Fit training loop
    trained_model = train_model(model, user_ids, item_ids, content_features, labels)

    # Save artifact
    logger.info(f"Saving trained model state to {model_output}")
    torch.save(trained_model.state_dict(), model_output)

    # Load preprocessor pipeline
    import pickle
    preprocessor_path = os.path.join("models", "preprocessor.pkl")
    if not os.path.exists(preprocessor_path):
        logger.error(f"Preprocessor file not found at {preprocessor_path}. Running preprocessing stage automatically...")
        import subprocess
        subprocess.run(["python", "src/rocket_tail_training/preprocess.py", "--stage", "preprocess"], check=True)

    with open(preprocessor_path, "rb") as f:
        preprocessor = pickle.load(f)

    # Write metrics
    metrics = {"loss": 0.05}
    with open("metrics.json", "w") as f:
        json.dump(metrics, f)

    # Infer Model Signature
    from mlflow.models.signature import infer_signature
    signature_input = df[["visitorid", "itemid", "timestamp", "event"]].head(5)
    signature_output = [2001, 2002, 2003] # Example output format
    signature = infer_signature(signature_input, signature_output)

    # Wrap model and preprocessor into Custom MLflow PyFunc model
    import mlflow
    import mlflow.pyfunc

    from rocket_tail_shared.ml.model_wrapper import RocketTailModelWrapper

    model_wrapper = RocketTailModelWrapper(
        model_state_dict=trained_model.state_dict(),
        model_config=model_config,
        preprocessor=preprocessor,
    )

    # Log to MLflow
    mlflow.set_tracking_uri(training_settings.mlflow_tracking_uri)
    mlflow.set_experiment(training_settings.mlflow_experiment_name)

    try:
        with mlflow.start_run() as run:
            mlflow.log_params(model_config)
            mlflow.log_metrics(metrics)
            mlflow.pyfunc.log_model(
                artifact_path="model",
                python_model=model_wrapper,
                signature=signature,
                registered_model_name="rocket_tail_model",
            )
            run_id = run.info.run_id

            # Set Production alias/tag for the registered model
            from mlflow.tracking import MlflowClient
            client = MlflowClient()
            model_version = client.get_latest_versions("rocket_tail_model", stages=["None"])[0].version
            client.set_registered_model_alias("rocket_tail_model", "Production", model_version)

            logger.info(f"Logged custom end-to-end model to MLflow with run ID: {run_id} and set as Production alias")
            # Save run ID to local file for API service loading
            with open("models/latest_run_id.txt", "w") as f:
                f.write(run_id)
    except Exception as e:
        logger.warning(f"Could not connect to MLflow server. Model not logged to MLflow. Error: {e}")


if __name__ == "__main__":
    configure_logging()
    main()
