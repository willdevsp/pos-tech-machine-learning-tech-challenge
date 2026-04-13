from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def load_dataset(data_path: Path) -> pd.DataFrame:
    suffix = data_path.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(data_path)
    if suffix in {".xlsx", ".xls"}:
        return pd.read_excel(data_path)

    raise ValueError(
        "Formato de arquivo nao suportado. Use .csv, .xlsx ou .xls."
    )


def dataset_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_target(series: pd.Series) -> pd.Series:
    if series.dtype == "bool":
        return series.astype(int)

    as_str = series.astype(str).str.strip().str.lower()
    mapping = {
        "yes": 1,
        "true": 1,
        "1": 1,
        "churn": 1,
        "no": 0,
        "false": 0,
        "0": 0,
        "stay": 0,
    }

    mapped = as_str.map(mapping)
    if mapped.isna().any():
        msg = (
            "A coluna target possui valores nao mapeaveis para classificacao binaria. "
            "Valores esperados incluem Yes/No, True/False, 1/0."
        )
        raise ValueError(msg)

    return mapped.astype(int)


def build_preprocessor(X: pd.DataFrame) -> ColumnTransformer:
    cat_cols = X.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    num_cols = [c for c in X.columns if c not in cat_cols]

    numeric_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical_pipe = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    return ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, num_cols),
            ("cat", categorical_pipe, cat_cols),
        ]
    )


def clean_telco_like_dataset(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = df.copy()

    # customerID e um identificador e nao deve ser usado como feature.
    id_cols = ["customerID", "CustomerID"]
    drop_ids = [c for c in id_cols if c in cleaned.columns]
    if drop_ids:
        cleaned = cleaned.drop(columns=drop_ids)

    # No dataset Telco, TotalCharges pode vir com espacos em branco.
    charge_cols = ["TotalCharges", "Total Charges"]
    for col in charge_cols:
        if col in cleaned.columns:
            cleaned[col] = pd.to_numeric(cleaned[col], errors="coerce")

    return cleaned


def drop_target_leakage_columns(df: pd.DataFrame, target_col: str) -> pd.DataFrame:
    cleaned = df.copy()
    leakage_cols = [
        c for c in cleaned.columns if "churn" in c.lower() and c != target_col
    ]
    if leakage_cols:
        cleaned = cleaned.drop(columns=leakage_cols)
    return cleaned


def evaluate(y_true: np.ndarray, y_proba: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    return {
        "auc_roc": float(roc_auc_score(y_true, y_proba)),
        "pr_auc": float(average_precision_score(y_true, y_proba)),
        "f1": float(f1_score(y_true, y_pred)),
    }


def run_stage1(
    data_path: Path,
    target_col: str,
    experiment_name: str,
    test_size: float,
    random_state: int,
) -> tuple[pd.DataFrame, str]:
    df = load_dataset(data_path)
    df = clean_telco_like_dataset(df)
    if target_col not in df.columns:
        raise ValueError(f"Coluna target '{target_col}' nao encontrada em {data_path}.")

    y = normalize_target(df[target_col])
    X = df.drop(columns=[target_col])
    X = drop_target_leakage_columns(X, target_col=target_col)

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )

    preprocessor = build_preprocessor(X_train)

    models: dict[str, Any] = {
        "dummy_most_frequent": DummyClassifier(strategy="most_frequent", random_state=random_state),
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
    }

    mlflow.set_experiment(experiment_name)

    rows: list[dict[str, Any]] = []
    best_run_id: str = ""
    for model_name, model in models.items():
        pipeline = Pipeline(
            steps=[
                ("preprocessor", preprocessor),
                ("model", model),
            ]
        )

        with mlflow.start_run(run_name=model_name) as run:
            pipeline.fit(X_train, y_train)

            if hasattr(pipeline, "predict_proba"):
                y_proba = pipeline.predict_proba(X_test)[:, 1]
            else:
                y_proba = pipeline.decision_function(X_test)

            y_pred = pipeline.predict(X_test)
            metrics = evaluate(y_test.to_numpy(), y_proba, y_pred)

            mlflow.log_params(
                {
                    "model_name": model_name,
                    "target_col": target_col,
                    "test_size": test_size,
                    "random_state": random_state,
                    "rows": len(df),
                    "cols": df.shape[1],
                    "dataset_sha256": dataset_sha256(data_path),
                }
            )
            mlflow.log_metrics(metrics)

            # Salva uma amostra de predicoes como artefato para auditoria.
            sample_pred = pd.DataFrame(
                {
                    "y_true": y_test.to_numpy(),
                    "y_pred": y_pred,
                    "y_proba": y_proba,
                }
            ).head(50)
            sample_file = Path("models") / f"{model_name}_pred_sample.csv"
            sample_file.parent.mkdir(parents=True, exist_ok=True)
            sample_pred.to_csv(sample_file, index=False)
            mlflow.log_artifact(sample_file)

            mlflow.sklearn.log_model(
                sk_model=pipeline,
                artifact_path="model",
                registered_model_name=f"churn_{model_name}",
            )

            if model_name == "logistic_regression":
                best_run_id = run.info.run_id

            rows.append({"model": model_name, **metrics})

    metrics_df = pd.DataFrame(rows).sort_values(by="auc_roc", ascending=False)
    out_file = Path("models") / "stage1_baselines_metrics.csv"
    out_file.parent.mkdir(parents=True, exist_ok=True)
    metrics_df.to_csv(out_file, index=False)

    eda_summary = {
        "rows": int(df.shape[0]),
        "columns": int(df.shape[1]),
        "missing_values_total": int(df.isna().sum().sum()),
        "missing_by_column": df.isna().sum().to_dict(),
        "target_distribution": y.value_counts(normalize=True).to_dict(),
    }
    eda_file = Path("docs") / "stage1_eda_summary.json"
    eda_file.parent.mkdir(parents=True, exist_ok=True)
    eda_file.write_text(json.dumps(eda_summary, indent=2), encoding="utf-8")

    return metrics_df, best_run_id


def main() -> None:
    parser = argparse.ArgumentParser(description="Etapa 1: EDA + baselines + MLflow")
    parser.add_argument("--data-path", type=Path, required=True, help="CSV com dados de churn")
    parser.add_argument("--target-col", type=str, default="Churn", help="Coluna target binaria")
    parser.add_argument(
        "--experiment-name",
        type=str,
        default="tech_challenge_stage1_baselines",
        help="Nome do experimento no MLflow",
    )
    parser.add_argument("--test-size", type=float, default=0.2)
    parser.add_argument("--random-state", type=int, default=42)
    args = parser.parse_args()

    np.random.seed(args.random_state)

    result, run_id = run_stage1(
        data_path=args.data_path,
        target_col=args.target_col,
        experiment_name=args.experiment_name,
        test_size=args.test_size,
        random_state=args.random_state,
    )
    print(result.to_string(index=False))
    print(f"\nMLflow run_id (logistic_regression): {run_id}")


if __name__ == "__main__":
    main()
