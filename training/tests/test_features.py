"""Tests for training feature engineering stage."""

import pandas as pd

from rocket_tail_training.features import engineer_features


def test_engineer_features() -> None:
    """Verifies feature engineering computes stats and contextual fields."""
    df = pd.DataFrame(
        {
            "timestamp": [1433221332, 1433221333, 1433221334],
            "visitorid": [1001, 1002, 1001],
            "itemid": [2001, 2001, 2002],
            "event": ["view", "view", "transaction"],
        }
    )

    feat_df = engineer_features(df)

    assert "user_activity" in feat_df.columns
    assert "item_popularity" in feat_df.columns
    assert "hour" in feat_df.columns

    # User 1001 has 2 activities, user 1002 has 1 activity
    assert feat_df[feat_df["visitorid"] == 1001]["user_activity"].iloc[0] == 2
    assert feat_df[feat_df["visitorid"] == 1002]["user_activity"].iloc[0] == 1

    # Item 2001 has 2 interactions, item 2002 has 1 interaction
    assert feat_df[feat_df["itemid"] == 2001]["item_popularity"].iloc[0] == 2
    assert feat_df[feat_df["itemid"] == 2002]["item_popularity"].iloc[0] == 1
