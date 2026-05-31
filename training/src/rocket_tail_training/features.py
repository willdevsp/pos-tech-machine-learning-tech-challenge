"""Feature engineering pipeline stage."""

import os

import pandas as pd
from loguru import logger

from rocket_tail_shared.utils.logging import configure_logging
from rocket_tail_training.config import training_settings


def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    """Performs feature engineering on the cleaned events.

    Generates user interaction counts, item popularity features, etc.

    Args:
        df: Input DataFrame containing cleaned events.

    Returns:
        DataFrame containing user, item IDs and engineered features.
    """
    logger.info("Computing interaction count features...")

    # Calculate user activity features
    user_counts = df.groupby("visitorid").size().reset_index(name="user_activity")

    # Calculate item popularity features
    item_counts = df.groupby("itemid").size().reset_index(name="item_popularity")

    # Merge features back into interactions
    df_features = df.merge(user_counts, on="visitorid", how="left")
    df_features = df_features.merge(item_counts, on="itemid", how="left")

    # Additional contextual features: hour of the day from timestamp
    df_features["hour"] = pd.to_datetime(df_features["timestamp"], unit="s").dt.hour

    return df_features


def main() -> None:
    """Main execution block for feature engineering stage."""
    processed_dir = training_settings.processed_data_path
    input_file = os.path.join(processed_dir, "cleaned_events.csv")
    output_file = os.path.join(processed_dir, "features.csv")

    if not os.path.exists(input_file):
        logger.error(f"Input file not found: {input_file}. Please run the preprocess stage first.")
        # Create dummy input for testing if missing
        import subprocess
        logger.info("Running preprocessing stage automatically to generate dependencies...")
        subprocess.run(["python", "src/rocket_tail_training/preprocess.py", "--stage", "preprocess"], check=True)

    df = pd.read_csv(input_file)
    features_df = engineer_features(df)

    logger.info(f"Saving features dataset of shape {features_df.shape} to {output_file}")
    features_df.to_csv(output_file, index=False)


if __name__ == "__main__":
    configure_logging()
    main()
