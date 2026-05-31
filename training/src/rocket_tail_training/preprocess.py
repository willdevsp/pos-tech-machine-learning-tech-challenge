"""Preprocess script for data loading and cleansing using shared strategies."""

import argparse
import os

import pandas as pd
from loguru import logger

from rocket_tail_shared.data.preprocessing import PipelineBuilder
from rocket_tail_shared.utils.logging import configure_logging
from rocket_tail_training.config import training_settings


def load_events(path: str, nrows: int | None = None) -> pd.DataFrame:
    """Loads the raw events dataset.

    Args:
        path: Path to the events CSV file.
        nrows: Maximum number of rows to load.

    Returns:
        DataFrame containing events data.

    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Raw data file not found at: {path}")

    logger.info(f"Loading raw events data from {path}")
    return pd.read_csv(path, nrows=nrows)


def run_preprocess() -> None:
    """Runs the data cleansing preprocessing pipeline stage."""
    raw_file = os.path.join(training_settings.raw_data_path, "events.csv")
    processed_dir = training_settings.processed_data_path
    os.makedirs(processed_dir, exist_ok=True)
    out_file = os.path.join(processed_dir, "cleaned_events.csv")

    try:
        df = load_events(raw_file)
    except FileNotFoundError:
        # Create a mock dataframe if raw file is missing for skeleton execution
        logger.warning(f"Raw file {raw_file} not found. Creating a mock skeleton dataset.")
        df = pd.DataFrame(
            {
                "timestamp": [1433221332, 1433221333, 1433221334],
                "visitorid": [1001, 1002, 1003],
                "event": ["view", "addtocart", "transaction"],
                "itemid": [2001, 2002, 2003],
                "transactionid": [None, None, 5001],
            }
        )
        os.makedirs(os.path.dirname(raw_file), exist_ok=True)
        df.to_csv(raw_file, index=False)

    # Initialize native Pipeline
    builder = PipelineBuilder(target_columns=["event"], id_columns=["visitorid", "itemid"])
    preprocessor = builder.create_preprocessor()

    logger.info("Executing preprocessing pipeline...")
    preprocessor.fit(df)
    cleaned_df = preprocessor.transform(df)

    logger.info(f"Saving cleaned dataset of shape {cleaned_df.shape} to {out_file}")
    cleaned_df.to_csv(out_file, index=False)

    # Save fitted preprocessor pipeline
    import pickle
    os.makedirs("models", exist_ok=True)
    preprocessor_path = "models/preprocessor.pkl"
    logger.info(f"Saving fitted preprocessor pipeline to {preprocessor_path}")
    with open(preprocessor_path, "wb") as f:
        pickle.dump(preprocessor, f)


def run_download() -> None:
    """Simulates downloading data by saving a skeleton raw dataset if not present."""
    raw_dir = training_settings.raw_data_path
    os.makedirs(raw_dir, exist_ok=True)
    raw_file = os.path.join(raw_dir, "events.csv")

    if os.path.exists(raw_file):
        logger.info(f"Raw events data already exists at {raw_file}")
        return

    logger.info(f"Downloading raw data skeleton to {raw_file}")
    # Mock data skeleton representation
    df = pd.DataFrame(
        {
            "timestamp": [1433221332, 1433221333, 1433221334],
            "visitorid": [1001, 1002, 1003],
            "event": ["view", "addtocart", "transaction"],
            "itemid": [2001, 2002, 2003],
            "transactionid": [None, None, 5001],
        }
    )
    df.to_csv(raw_file, index=False)


if __name__ == "__main__":
    configure_logging()
    parser = argparse.ArgumentParser(description="Preprocess pipeline stage.")
    parser.add_argument(
        "--stage",
        choices=["download", "preprocess"],
        required=True,
        help="Stage to run.",
    )
    args = parser.parse_args()

    if args.stage == "download":
        run_download()
    elif args.stage == "preprocess":
        run_preprocess()
