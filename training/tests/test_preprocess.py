"""Tests for training preprocessing functions."""

import pandas as pd
import pytest

from rocket_tail_training.preprocess import load_events


def test_load_events_not_found() -> None:
    """Verifies load_events raises FileNotFoundError on missing file."""
    with pytest.raises(FileNotFoundError):
        load_events("non_existent_file.csv")


def test_load_events_success(tmp_path) -> None:
    """Verifies load_events loads standard DataFrame successfully."""
    dummy_csv = tmp_path / "dummy.csv"
    df = pd.DataFrame({"visitorid": [1, 2], "itemid": [3, 4]})
    df.to_csv(dummy_csv, index=False)

    loaded = load_events(str(dummy_csv))
    assert loaded.shape == (2, 2)
    assert list(loaded.columns) == ["visitorid", "itemid"]
