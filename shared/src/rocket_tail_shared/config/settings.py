"""Configuration Settings for RocketTail Recommendation System."""


from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration Settings model using Pydantic Settings.

    Enables environment-variable driven configurations with local fallback.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # General configuration
    app_name: str = "RocketTail Recommendation System"
    env: str = "development"

    # MLflow Tracking settings
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "rocket-tail-recommender"

    # PyTorch Model parameters
    user_emb_dim: int = 32
    item_emb_dim: int = 32
    hidden_dims: list[int] = [128, 64, 32]
    dropout_rate: float = 0.2

    # Data configurations
    raw_data_path: str = "data/raw"
    processed_data_path: str = "data/processed"


# Instantiate a singleton settings object
settings = Settings()
