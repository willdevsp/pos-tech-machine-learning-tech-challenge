"""Transformador de features para conversão de dicionário nomeado para array 30D.

Converte features nomeadas (ex: {"Gender": "Male", ...}) em arrays numéricos
ordenados (30 elementos) compatíveis com o modelo de ML.

Processo:
  1. Recebe dicionário com 19 features nomeadas
  2. Aplica binary encoding (Yes/No -> 1/0)
  3. Aplica one-hot encoding (drop_first=True)
  4. Normaliza com StandardScaler
  5. Retorna array 30D pronto para predição
"""

import numpy as np
import pickle
import pandas as pd
from typing import Dict, Union, List
from pathlib import Path
from sklearn.preprocessing import StandardScaler as SKStandardScaler

# Ordem exata das 30 features após TelcoDataPreprocessor
FEATURE_ORDER = [
    "Gender", "Senior Citizen", "Partner", "Dependents", "Tenure Months",
    "Phone Service", "Paperless Billing", "Monthly Charges", "Total Charges",
    "Multiple Lines_No phone service", "Multiple Lines_Yes",
    "Internet Service_Fiber optic", "Internet Service_No",
    "Online Security_No internet service", "Online Security_Yes",
    "Online Backup_No internet service", "Online Backup_Yes",
    "Device Protection_No internet service", "Device Protection_Yes",
    "Tech Support_No internet service", "Tech Support_Yes",
    "Streaming TV_No internet service", "Streaming TV_Yes",
    "Streaming Movies_No internet service", "Streaming Movies_Yes",
    "Contract_One year", "Contract_Two year",
    "Payment Method_Credit card (automatic)", "Payment Method_Electronic check",
    "Payment Method_Mailed check"
]


def _create_scaler_from_dataset() -> SKStandardScaler:
    """Cria StandardScaler ajustado aos dados codificados do dataset.
    
    O scaler é recalculado durante inicialização para garantir normalização
    consistente entre treinamento e inferência.
    """
    from src.data.preprocessing import TelcoDataPreprocessor
    
    # Carregar dados
    preprocessor = TelcoDataPreprocessor()
    df = preprocessor.load_data('data/processed/telco_churn_processed.csv')
    df = preprocessor.drop_leakage_columns(df)
    X, y = preprocessor.extract_target(df)
    
    # Codificar
    X = preprocessor.encode_binary_features(X)
    X = preprocessor.encode_categorical_features(X)
    
    # Fit scaler nos dados codificados (SEM normalizar)
    scaler = SKStandardScaler()
    scaler.fit(X)
    
    print("[OK] StandardScaler recriado a partir do dataset")
    return scaler


class FeatureTransformer:
    """Transforma features nomeadas em arrays numéricos 30D normalizados.
    
    Atributos:
        feature_order: Lista de 30 nomes de features na ordem esperada
        scaler: StandardScaler para normalização dos dados
    """
    
    def __init__(self):
        self.feature_order = FEATURE_ORDER
        self.n_features = len(FEATURE_ORDER)
        self.scaler = None
        
        # Criar scaler recalculado a partir dos dados
        try:
            self.scaler = _create_scaler_from_dataset()
        except Exception as e:
            print(f"⚠️ Não foi possível criar scaler: {e}")
    
    def _encode(self, features_dict: Dict[str, Union[str, int, float]]) -> np.ndarray:
        """Codifica features nominais em formato numérico.
        
        Aplica binary encoding (Yes/No -> 1/0) e one-hot encoding com drop_first.
        Não realiza normalização (feita em transform).
        """
        features = []
        
        # 1. Gender (Male -> 0, Female -> 1)
        gender = 0 if str(features_dict["Gender"]).strip().lower() == "male" else 1
        features.append(gender)
        
        # 2-4. Binary features
        features.append(1 if str(features_dict["Senior Citizen"]).strip().lower() == "yes" else 0)
        features.append(1 if str(features_dict["Partner"]).strip().lower() == "yes" else 0)
        features.append(1 if str(features_dict["Dependents"]).strip().lower() == "yes" else 0)
        
        # 5-9. Numeric features
        features.append(float(features_dict["Tenure Months"]))
        features.append(1 if str(features_dict["Phone Service"]).strip().lower() == "yes" else 0)
        features.append(1 if str(features_dict["Paperless Billing"]).strip().lower() == "yes" else 0)
        features.append(float(features_dict["Monthly Charges"]))
        features.append(float(features_dict["Total Charges"]))
        
        # 10-11. Multiple Lines (drop_first="No")
        ml = str(features_dict["Multiple Lines"]).strip().lower()
        features.extend([1, 0] if ml == "no phone service" else ([0, 1] if ml == "yes" else [0, 0]))
        
        # 12-13. Internet Service (drop_first="DSL")
        inet = str(features_dict["Internet Service"]).strip().lower()
        features.extend([1, 0] if inet == "fiber optic" else ([0, 1] if inet == "no" else [0, 0]))
        
        # 14-15 to 24-25. Services (drop_first="No")
        for service in ["Online Security", "Online Backup", "Device Protection", "Tech Support", "Streaming TV", "Streaming Movies"]:
            val = str(features_dict[service]).strip().lower()
            features.extend([1, 0] if val == "no internet service" else ([0, 1] if val == "yes" else [0, 0]))
        
        # 26-27. Contract (drop_first="Month-to-month")
        contract = str(features_dict["Contract"]).strip().lower()
        features.extend([1, 0] if contract == "one year" else ([0, 1] if contract == "two year" else [0, 0]))
        
        # 28-30. Payment Method (drop_first="Bank transfer")
        pm = str(features_dict["Payment Method"]).strip().lower()
        if "credit card" in pm:
            features.extend([1, 0, 0])
        elif "electronic check" in pm:
            features.extend([0, 1, 0])
        elif "mailed check" in pm:
            features.extend([0, 0, 1])
        else:
            features.extend([0, 0, 0])
        
        assert len(features) == 30, f"Expected 30 features, got {len(features)}"
        return np.array(features, dtype=np.float32).reshape(1, -1)
    
    def transform(self, features_dict: Dict[str, Union[str, int, float]]) -> np.ndarray:
        """Transforma dicionário de features em array 30D normalizado.
        
        Args:
            features_dict: Dicionário com 19 features nomeadas
            
        Returns:
            Array numpy (1, 30) normalizado e pronto para predição
        """
        # Codificar
        X = self._encode(features_dict)
        
        # Normalizar com o scaler recalculado
        if self.scaler is not None:
            X = self.scaler.transform(X)
        
        return X
    
    def transform_batch(self, features_list: List[Dict[str, Union[str, int, float]]]) -> np.ndarray:
        """Transforma lista de dicionários em array 2D normalizado.
        
        Args:
            features_list: Lista de dicionários com features nomeadas
            
        Returns:
            Array numpy (n_samples, 30) normalizado
        """
        encoded = np.array([self._encode(f)[0] for f in features_list], dtype=np.float32)
        
        # Normalizar
        if self.scaler is not None:
            encoded = self.scaler.transform(encoded)
        
        return encoded


# Instância global
feature_transformer = FeatureTransformer()
