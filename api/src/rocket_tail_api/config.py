"""API-specific configurations extending shared settings."""

from rocket_tail_shared.config.settings import Settings


class ApiSettings(Settings):
    """Configuration settings specific to uvicorn and FastAPI setup."""

    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 1
    model_path: str = "models/model.pt"


api_settings = ApiSettings()
