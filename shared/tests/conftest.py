"""Pytest fixtures for testing the shared library."""

import pandas as pd
import pytest


@pytest.fixture
def sample_events_df() -> pd.DataFrame:
    """Fixture returning a small mock events DataFrame.

    Returns:
        DataFrame with visitorid, itemid, event and timestamp.
    """
    return pd.DataFrame(
        {
            "timestamp": [1433221332, 1433221333, 1433221334, 1433221335],
            "visitorid": [1001, 1002, 1003, 1001],
            "event": ["view", "addtocart", "transaction", "view"],
            "itemid": [2001, 2002, 2003, 2001],
            "transactionid": [None, None, 5001, None],
        }
    )
