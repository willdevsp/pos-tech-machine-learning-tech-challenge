"""Training loop pipeline stage using PyTorch and ModelFactory."""

import json
import os
import sys

# Reconfigure stdout/stderr to UTF-8 to prevent encoding errors on Windows when printing emojis (like the mlflow runner emoji)
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

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

    # Evaluate model and calculate recommendation metrics
    logger.info("Evaluating model and calculating recommendation metrics...")
    trained_model.eval()

    from rocket_tail_shared.ml.metrics import precision_at_k, recall_at_k, ndcg_at_k, mean_reciprocal_rank

    unique_users = df["visitorid"].unique()
    all_items = df["itemid"].unique().tolist()

    precisions = []
    recalls = []
    ndcgs = []
    mrrs = []

    for user_id in unique_users:
        actual_items = df[df["visitorid"] == user_id]["itemid"].unique().tolist()

        user_candidates = pd.DataFrame({
            "visitorid": [user_id] * len(all_items),
            "itemid": all_items,
        })

        user_feats = df[df["visitorid"] == user_id][["visitorid", "user_activity", "hour"]].drop_duplicates().head(1)
        if user_feats.empty:
            user_activity = 0.0
            hour = 12.0
        else:
            user_activity = user_feats["user_activity"].values[0]
            hour = user_feats["hour"].values[0]

        user_candidates["user_activity"] = user_activity
        user_candidates["hour"] = hour

        pop_map = df[["itemid", "item_popularity"]].drop_duplicates().set_index("itemid")["item_popularity"].to_dict()
        user_candidates["item_popularity"] = user_candidates["itemid"].map(pop_map).fillna(0.0)

        u_ids = torch.tensor(user_candidates["visitorid"].values, dtype=torch.long)
        i_ids = torch.tensor(user_candidates["itemid"].values, dtype=torch.long)
        c_feats = torch.tensor(user_candidates[["user_activity", "item_popularity", "hour"]].values, dtype=torch.float)

        with torch.no_grad():
            scores = trained_model(u_ids, i_ids, c_feats).squeeze(1).numpy()

        user_candidates["score"] = scores
        ranked_items = user_candidates.sort_values(by="score", ascending=False)["itemid"].tolist()

        k = 5
        precisions.append(precision_at_k(actual_items, ranked_items, k))
        recalls.append(recall_at_k(actual_items, ranked_items, k))
        ndcgs.append(ndcg_at_k(actual_items, ranked_items, k))
        mrrs.append(mean_reciprocal_rank(actual_items, ranked_items))

    avg_precision = sum(precisions) / len(precisions) if precisions else 0.0
    avg_recall = sum(recalls) / len(recalls) if recalls else 0.0
    avg_ndcg = sum(ndcgs) / len(ndcgs) if ndcgs else 0.0
    avg_mrr = sum(mrrs) / len(mrrs) if mrrs else 0.0

    with torch.no_grad():
        train_outputs = trained_model(user_ids, item_ids, content_features)
        criterion = nn.MSELoss()
        real_loss = float(criterion(train_outputs, labels).item())

    metrics = {
        "loss": real_loss,
        "precision_at_5": avg_precision,
        "recall_at_5": avg_recall,
        "ndcg_at_5": avg_ndcg,
        "mrr": avg_mrr,
    }

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

            # Set Production tag for the registered model version (MLflow 3.x tag-based stage management)
            from mlflow.tracking import MlflowClient
            client = MlflowClient()

            # Fetch all versions and select the highest version number
            versions = client.search_model_versions("name='rocket_tail_model'")
            if versions:
                model_version = max(versions, key=lambda x: int(x.version)).version
            else:
                model_version = "1"

            # Remove stage=Production tag from any other versions
            for v in versions:
                if v.tags.get("stage") == "Production":
                    try:
                        client.delete_model_version_tag("rocket_tail_model", v.version, "stage")
                        logger.info(f"Removed Production tag from older version {v.version}")
                    except Exception as tag_err:
                        logger.warning(f"Could not remove tag from version {v.version}: {tag_err}")

            # Assign stage=Production tag to the newly registered version
            client.set_model_version_tag("rocket_tail_model", model_version, "stage", "Production")

            logger.info(f"Logged custom end-to-end model to MLflow with run ID: {run_id} and set stage=Production tag")
            # Save run ID to local file for API service loading
            with open("models/latest_run_id.txt", "w") as f:
                f.write(run_id)
    except Exception as e:
        logger.warning(f"Could not connect to MLflow server. Model not logged to MLflow. Error: {e}")


if __name__ == "__main__":
    configure_logging()
    main()
