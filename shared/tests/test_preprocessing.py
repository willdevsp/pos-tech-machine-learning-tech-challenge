"""Tests for native scikit-learn preprocessing pipeline builder."""

import pandas as pd

from rocket_tail_shared.data.preprocessing import PipelineBuilder


def test_pipeline_builder_initialization() -> None:
    """Verifies PipelineBuilder initializes with defaults."""
    builder = PipelineBuilder()
    assert builder.target_columns == ["event"]
    assert builder.id_columns == ["visitorid", "itemid"]


def test_pipeline_builder_creation() -> None:
    """Verifies PipelineBuilder creates a scikit-learn Pipeline."""
    builder = PipelineBuilder()
    pipeline = builder.create_preprocessor()
    
    # Check it is a sklearn Pipeline
    from sklearn.pipeline import Pipeline
    assert isinstance(pipeline, Pipeline)
    
    # Check that ColumnTransformer is the first step
    from sklearn.compose import ColumnTransformer
    assert isinstance(pipeline.named_steps["preprocessor"], ColumnTransformer)


def test_pipeline_transform(sample_events_df: pd.DataFrame) -> None:
    """Verifies the pipeline processes events DataFrame and outputs Pandas DataFrame."""
    builder = PipelineBuilder(target_columns=["event"], id_columns=["visitorid", "itemid"])
    pipeline = builder.create_preprocessor()
    
    # Add a null row to test imputation (using float('nan') for compatibility)
    df_with_nulls = pd.concat([
        sample_events_df, 
        pd.DataFrame([{"visitorid": float('nan'), "itemid": float('nan'), "event": float('nan'), "timestamp": float('nan')}])
    ], ignore_index=True)
    
    pipeline.fit(df_with_nulls)
    processed = pipeline.transform(df_with_nulls)
    
    # Result should be a pandas DataFrame
    assert isinstance(processed, pd.DataFrame)
    
    # Nulls should have been imputed (no NaNs in target/id columns)
    assert not processed["event"].isnull().any()
    assert not processed["visitorid"].isnull().any()
    
    # event should be ordinally encoded (numeric)
    assert processed["event"].dtype in ["float64", "int64", "int32"]
