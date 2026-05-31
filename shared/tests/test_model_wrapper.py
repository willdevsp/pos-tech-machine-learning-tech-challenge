"""Tests for custom MLflow RocketTailModelWrapper."""

import pandas as pd

from rocket_tail_shared.data.preprocessing import PipelineBuilder
from rocket_tail_shared.ml.model_wrapper import RocketTailModelWrapper
from rocket_tail_shared.models.hybrid import HybridNN


def test_model_wrapper_predict() -> None:
    """Verifies that the end-to-end wrapper runs preprocessing and torch model."""
    # 1. Setup preprocessor
    builder = PipelineBuilder(target_columns=["event"], id_columns=["visitorid", "itemid"])
    preprocessor = builder.create_preprocessor()

    # 2. Setup mock PyTorch weights
    model_config = {
        "num_users": 100,
        "num_items": 100,
        "user_emb_dim": 8,
        "item_emb_dim": 8,
        "content_feature_dim": 3,
        "hidden_dims": [16],
    }
    model = HybridNN(
        num_users=100,
        num_items=100,
        user_emb_dim=8,
        item_emb_dim=8,
        content_feature_dim=3,
        hidden_dims=[16],
    )
    state_dict = model.state_dict()

    # 3. Create wrapper
    wrapper = RocketTailModelWrapper(
        model_state_dict=state_dict,
        model_config=model_config,
        preprocessor=preprocessor,
    )

    # 4. Mock inputs
    input_df = pd.DataFrame(
        {
            "visitorid": [1, 2, 3],
            "itemid": [10, 11, 12],
            "event": ["view", "addtocart", "transaction"],
            "user_activity": [1.0, 2.0, 3.0],
            "item_popularity": [5.0, 2.0, 1.0],
            "hour": [12, 13, 14],
        }
    )

    # Fit preprocessor to fit scikit-learn pipeline internal state
    preprocessor.fit(input_df)

    # 5. Predict
    recs = wrapper.predict(None, input_df)

    assert isinstance(recs, list)
    assert len(recs) == 3
    assert set(recs).issubset({10, 11, 12})
