"""Training-specific configurations extending shared settings."""

from rocket_tail_shared.config.settings import Settings


class TrainingSettings(Settings):
    """Configuration settings specific to model training."""

    epochs: int = 10
    batch_size: int = 256
    learning_rate: float = 0.001
    val_split: float = 0.2
    test_split: float = 0.1
    random_state: int = 42


training_settings = TrainingSettings()
