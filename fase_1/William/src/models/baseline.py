"""Modelos baseline para Telco Churn com MLflow tracking."""

import mlflow
import mlflow.sklearn
import numpy as np
import os
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    roc_auc_score, 
    average_precision_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report
)
import pandas as pd
from typing import Tuple, Dict, Any
from xgboost import XGBClassifier
from sklearn.model_selection import RandomizedSearchCV
from imblearn.over_sampling import SMOTE


class BaselineExperiment:
    """Treina e registra modelos baseline com MLflow."""

    def __init__(self, experiment_name="Telco Churn - Baselines", mlflow_uri="../mlruns"):
        """
        Inicializa experimento MLflow.

        Args:
            experiment_name: Nome do experimento
            mlflow_uri: URI para armazenar artefatos MLflow
        """
        # Criar pasta se não existir
        os.makedirs(mlflow_uri, exist_ok=True)
        
        self.experiment_name = experiment_name
        self.mlflow_uri = mlflow_uri
        mlflow.set_tracking_uri(mlflow_uri)

        # Obter ou criar experimento
        experiment = mlflow.get_experiment_by_name(experiment_name)
        if experiment is None:
            exp_id = mlflow.create_experiment(experiment_name)
        else:
            exp_id = experiment.experiment_id
        
        mlflow.set_experiment(experiment_name)
        self.resultados = {}

    def treinar_modelo(self, modelo, X_train, X_test, y_train, y_test, 
                      nome_modelo: str, X_train_modificado=None, y_train_modificado=None) -> Tuple:
        """
        Método genérico para treinar qualquer modelo.

        Args:
            modelo: Instância do modelo (sklearn, xgboost, etc)
            X_train: Features de treino
            X_test: Features de teste
            y_train: Labels de treino
            y_test: Labels de teste
            nome_modelo: Nome descritivo do modelo
            X_train_modificado: Features de treino modificadas (ex: SMOTE) - opcional
            y_train_modificado: Labels de treino modificados (ex: SMOTE) - opcional

        Returns:
            (modelo_treinado, metricas)
        """
        with mlflow.start_run(run_name=nome_modelo):
            # Usar dados modificados se fornecidos (ex: SMOTE)
            X_treino = X_train_modificado if X_train_modificado is not None else X_train
            y_treino = y_train_modificado if y_train_modificado is not None else y_train

            # Log de parâmetros do modelo
            parametros = modelo.get_params()
            for param_name, param_value in parametros.items():
                mlflow.log_param(param_name, param_value)

            # Dataset info
            mlflow.log_dict({
                'churn_rate_train': float(y_treino.mean()),
                'churn_rate_test': float(y_test.mean()),
                'n_train_samples': X_treino.shape[0],
                'n_test_samples': X_test.shape[0],
                'n_features': X_treino.shape[1],
            }, artifact_file="data_info.json")

            # Treinar modelo
            modelo.fit(X_treino, y_treino)

            # Predicoes
            y_pred = modelo.predict(X_test)
            y_pred_proba = modelo.predict_proba(X_test)[:, 1]

            # Calcular métricas
            metricas = {
                'test_auc_roc': roc_auc_score(y_test, y_pred_proba),
                'test_pr_auc': average_precision_score(y_test, y_pred_proba),
                'test_accuracy': accuracy_score(y_test, y_pred),
                'test_precision': precision_score(y_test, y_pred),
                'test_recall': recall_score(y_test, y_pred),
                'test_f1_score': f1_score(y_test, y_pred),
            }

            mlflow.log_metrics(metricas)

            # Exibir resultados
            print(f"\n[OK] {nome_modelo} treinado")
            print(f"  - AUC-ROC: {metricas['test_auc_roc']:.4f}")
            print(f"  - PR-AUC: {metricas['test_pr_auc']:.4f}")
            print(f"  - Acurácia: {metricas['test_accuracy']:.4f}")
            print(f"  - Precision: {metricas['test_precision']:.4f}")
            print(f"  - Recall: {metricas['test_recall']:.4f}")
            print(f"  - F1-Score: {metricas['test_f1_score']:.4f}")

            # Log de feature importance (se disponível)
            if hasattr(modelo, 'feature_importances_'):
                feature_importance = pd.DataFrame({
                    'feature': range(X_treino.shape[1]),
                    'importance': modelo.feature_importances_
                }).sort_values('importance', ascending=False)

                mlflow.log_dict(feature_importance.to_dict(), 
                              artifact_file="feature_importance.json")

                print(f"  - Top 5 features (importância):")
                for idx, row in feature_importance.head(5).iterrows():
                    print(f"    Feature {row['feature']}: {row['importance']:.4f}")

            # Log de coeficientes (se disponível)
            elif hasattr(modelo, 'coef_'):
                coeficientes = pd.DataFrame({
                    'feature': range(X_treino.shape[1]),
                    'coef': modelo.coef_[0]
                }).sort_values('coef', ascending=False)

                mlflow.log_dict(coeficientes.to_dict(), artifact_file="top_features.json")

                print(f"  - Top 5 features (coeficientes):")
                for idx, row in coeficientes.head(5).iterrows():
                    print(f"    Feature {row['feature']}: {row['coef']:.4f}")

            # Registrar modelo
            mlflow.sklearn.log_model(modelo, artifact_path="model")
            self.resultados[nome_modelo] = metricas

            return modelo, metricas

    def treinar_esteira_completa(self, X_train, X_test, y_train, y_test, 
                                 include_tuning=False, n_iter_tuning=5, cv_tuning=3):
        """
        Treina todos os modelos em uma esteira usando método genérico.

        Args:
            X_train, X_test, y_train, y_test: Dados de treino e teste
            include_tuning: Se True, inclui modelos com tuning (mais lento)
            n_iter_tuning: Número de iterações para RandomizedSearchCV
            cv_tuning: Número de folds para cross-validation

        Returns:
            DataFrame com comparação de todos os modelos
        """
        print("\n" + "="*70)
        print("🚀 INICIANDO ESTEIRA DE MODELOS")
        print("="*70)

        # 1. DummyClassifier (most_frequent)
        print("\n[1/6] Treinando DummyClassifier (most_frequent)...")
        dummy_clf = DummyClassifier(strategy='most_frequent', random_state=42)
        self.treinar_modelo(dummy_clf, X_train, X_test, y_train, y_test, 
                           nome_modelo="DummyClassifier-most_frequent")

        # 2. LogisticRegression (simples)
        print("\n[2/6] Treinando LogisticRegression (simples)...")
        logreg_clf = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
        self.treinar_modelo(logreg_clf, X_train, X_test, y_train, y_test,
                           nome_modelo="LogisticRegression-simples")

        # 3. LogisticRegression (balanced)
        print("\n[3/6] Treinando LogisticRegression (balanced)...")
        logreg_balanced = LogisticRegression(max_iter=1000, class_weight='balanced', 
                                            random_state=42, n_jobs=-1)
        self.treinar_modelo(logreg_balanced, X_train, X_test, y_train, y_test,
                           nome_modelo="LogisticRegression-balanced")

        # 4. LogisticRegression (com SMOTE)
        print("\n[4/6] Treinando LogisticRegression com SMOTE...")
        smote = SMOTE(random_state=42)
        X_train_smote, y_train_smote = smote.fit_resample(X_train, y_train)
        logreg_smote = LogisticRegression(max_iter=1000, random_state=42, n_jobs=-1)
        self.treinar_modelo(logreg_smote, X_train, X_test, y_train, y_test,
                           nome_modelo="LogisticRegression-SMOTE",
                           X_train_modificado=X_train_smote,
                           y_train_modificado=y_train_smote)

        # 5. RandomForest
        print("\n[5/6] Treinando RandomForestClassifier...")
        rf_clf = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1)
        self.treinar_modelo(rf_clf, X_train, X_test, y_train, y_test,
                           nome_modelo="RandomForestClassifier")

        # 6. XGBoost
        print("\n[6/6] Treinando XGBoostClassifier...")
        xgb_clf = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1,
                               random_state=42, use_label_encoder=False,
                               eval_metric='logloss', n_jobs=-1)
        self.treinar_modelo(xgb_clf, X_train, X_test, y_train, y_test,
                           nome_modelo="XGBoostClassifier")

        # 7. Tuning (opcional)
        if include_tuning:
            print("\n[7a] Treinando RandomForestClassifier com tuning...")
            self._treinar_com_tuning_rf(X_train, X_test, y_train, y_test,
                                       n_iter=n_iter_tuning, cv=cv_tuning)

            print("\n[7b] Treinando XGBoostClassifier com tuning...")
            self._treinar_com_tuning_xgb(X_train, X_test, y_train, y_test,
                                        n_iter=n_iter_tuning, cv=cv_tuning)

        return self.comparar_baselines(self.resultados)

    def _treinar_com_tuning_rf(self, X_train, X_test, y_train, y_test, 
                               n_iter=10, cv=3):
        """Treina RandomForest com tuning de hiperparâmetros."""
        with mlflow.start_run(run_name="RandomForestClassifier-Tuned"):
            param_dist = {
                'n_estimators': [100, 200, 300],
                'max_depth': [None, 10, 20],
                'min_samples_split': [2, 5, 10],
                'min_samples_leaf': [1, 2, 4],
                'bootstrap': [True, False]
            }

            print("[INFO] Executando RandomizedSearchCV (pode levar alguns minutos)...")
            rf = RandomForestClassifier(random_state=42, n_jobs=-1)
            random_search = RandomizedSearchCV(
                estimator=rf, param_distributions=param_dist,
                n_iter=n_iter, cv=cv, random_state=42, n_jobs=-1, verbose=1
            )
            random_search.fit(X_train, y_train)

            best_model = random_search.best_estimator_
            
            # Log dos melhores parâmetros
            for param_name, param_value in random_search.best_params_.items():
                mlflow.log_param(f"best_{param_name}", param_value)

            y_pred = best_model.predict(X_test)
            y_pred_proba = best_model.predict_proba(X_test)[:, 1]

            metricas = {
                'test_auc_roc': roc_auc_score(y_test, y_pred_proba),
                'test_pr_auc': average_precision_score(y_test, y_pred_proba),
                'test_accuracy': accuracy_score(y_test, y_pred),
                'test_precision': precision_score(y_test, y_pred),
                'test_recall': recall_score(y_test, y_pred),
                'test_f1_score': f1_score(y_test, y_pred),
            }

            mlflow.log_metrics(metricas)
            mlflow.sklearn.log_model(best_model, artifact_path="model")

            print(f"\n[OK] RandomForestClassifier-Tuned treinado")
            print(f"  - AUC-ROC: {metricas['test_auc_roc']:.4f}")
            print(f"  - Melhores parâmetros: {random_search.best_params_}")

            self.resultados['RandomForestClassifier-Tuned'] = metricas

    def _treinar_com_tuning_xgb(self, X_train, X_test, y_train, y_test,
                                n_iter=10, cv=3):
        """Treina XGBoost com tuning de hiperparâmetros."""
        with mlflow.start_run(run_name="XGBoostClassifier-Tuned"):
            param_dist = {
                'n_estimators': [100, 200, 300],
                'max_depth': [3, 5, 7],
                'learning_rate': [0.01, 0.1, 0.2],
                'subsample': [0.8, 1.0],
                'colsample_bytree': [0.8, 1.0]
            }

            print("[INFO] Executando RandomizedSearchCV (pode levar alguns minutos)...")
            xgb = XGBClassifier(random_state=42, use_label_encoder=False,
                               eval_metric='logloss', n_jobs=-1)
            random_search = RandomizedSearchCV(
                estimator=xgb, param_distributions=param_dist,
                n_iter=n_iter, cv=cv, random_state=42, n_jobs=-1, verbose=1
            )
            random_search.fit(X_train, y_train)

            best_model = random_search.best_estimator_

            # Log dos melhores parâmetros
            for param_name, param_value in random_search.best_params_.items():
                mlflow.log_param(f"best_{param_name}", param_value)

            y_pred = best_model.predict(X_test)
            y_pred_proba = best_model.predict_proba(X_test)[:, 1]

            metricas = {
                'test_auc_roc': roc_auc_score(y_test, y_pred_proba),
                'test_pr_auc': average_precision_score(y_test, y_pred_proba),
                'test_accuracy': accuracy_score(y_test, y_pred),
                'test_precision': precision_score(y_test, y_pred),
                'test_recall': recall_score(y_test, y_pred),
                'test_f1_score': f1_score(y_test, y_pred),
            }

            mlflow.log_metrics(metricas)
            mlflow.sklearn.log_model(best_model, artifact_path="model")

            print(f"\n[OK] XGBoostClassifier-Tuned treinado")
            print(f"  - AUC-ROC: {metricas['test_auc_roc']:.4f}")
            print(f"  - Melhores parâmetros: {random_search.best_params_}")

            self.resultados['XGBoostClassifier-Tuned'] = metricas

    def comparar_baselines(self, resultados: dict) -> pd.DataFrame:
        """
        Compara resultados de todos os baselines.

        Args:
            resultados: Dicionário com resultados de cada modelo

        Returns:
            DataFrame com comparação
        """
        print("\n" + "="*70)
        print("COMPARAÇÃO DE BASELINES")
        print("="*70 + "\n")

        df_comparacao = pd.DataFrame(resultados).T
        df_comparacao = df_comparacao.sort_values('test_auc_roc', ascending=False)

        print(df_comparacao.to_string())
        print("\n" + "="*70)

        return df_comparacao
