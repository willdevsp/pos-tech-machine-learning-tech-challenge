from __future__ import annotations

import argparse
from pathlib import Path

import mlflow.sklearn
import pandas as pd

from churn_stage1.stage1_baselines import (
    clean_telco_like_dataset,
    drop_target_leakage_columns,
    load_dataset,
)


def resolve_customer_id(raw_df: pd.DataFrame) -> pd.Series:
    for col in ("customerID", "CustomerID"):
        if col in raw_df.columns:
            return raw_df[col].astype(str)
    return pd.Series(range(len(raw_df)), name="row_id")


def predict_churn(
    model_uri: str,
    data_path: Path,
    output_path: Path,
    target_col: str | None,
    threshold: float,
) -> pd.DataFrame:
    raw_df = load_dataset(data_path)
    customer_id = resolve_customer_id(raw_df)

    df = clean_telco_like_dataset(raw_df)
    if target_col and target_col in df.columns:
        X = df.drop(columns=[target_col])
    else:
        X = df.copy()
    X = drop_target_leakage_columns(X, target_col=target_col or "")

    model = mlflow.sklearn.load_model(model_uri)
    churn_score = model.predict_proba(X)[:, 1]
    churn_pred = (churn_score >= threshold).astype(int)

    result = pd.DataFrame(
        {
            "customer_id": customer_id,
            "churn_score": churn_score,
            "churn_pred": churn_pred,
        }
    ).sort_values(by="churn_score", ascending=False)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(output_path, index=False)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Predicao de churn via MLflow model URI")
    parser.add_argument(
        "--model-uri",
        type=str,
        required=True,
        help=(
            "URI do modelo no MLflow. Exemplos:\n"
            "  runs:/<run_id>/model\n"
            "  models:/churn_logistic_regression/latest"
        ),
    )
    parser.add_argument("--data-path", type=Path, required=True, help="Arquivo .csv/.xlsx para inferencia")
    parser.add_argument(
        "--output-path",
        type=Path,
        default=Path("models/churn_predictions.csv"),
        help="Arquivo de saida com scores",
    )
    parser.add_argument(
        "--target-col",
        type=str,
        default="Churn Value",
        help="Opcional: coluna target para remover antes da inferencia",
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.5,
        help="Threshold para classe positiva (default: 0.5)",
    )
    args = parser.parse_args()

    result = predict_churn(
        model_uri=args.model_uri,
        data_path=args.data_path,
        output_path=args.output_path,
        target_col=args.target_col,
        threshold=args.threshold,
    )
    print(result.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
