"""Schemas Pydantic para validação de requests e responses da API.

Define modelos de dados para:
  - Health check
  - Predição simples (single)
  - Predição em lote (batch)
"""

from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Union, Any
from enum import Enum


class HealthCheckResponse(BaseModel):
    """Response do endpoint de health check.
    
    Indica status da API e se modelo está carregado.
    """
    status: str = Field(..., description="Status da API")
    version: str = Field(..., description="Versão da API")
    model_loaded: bool = Field(..., description="Se modelo está carregado")


class PredictionRequest(BaseModel):
    """Request para predição de churn de um cliente.
    
    Features são enviadas como dicionário com nomes intuitívos
    (ex: Gender, Senior Citizen, Contract, etc).
    """
    features: Dict[str, Union[str, int, float]] = Field(
        ..., 
        description="Dicionário com features nomeadas",
        example={
            "Gender": "Male",
            "Senior Citizen": "No",
            "Partner": "No",
            "Dependents": "No",
            "Tenure Months": 2,
            "Phone Service": "Yes",
            "Multiple Lines": "No",
            "Internet Service": "DSL",
            "Online Security": "Yes",
            "Online Backup": "Yes",
            "Device Protection": "No",
            "Tech Support": "No",
            "Streaming TV": "No",
            "Streaming Movies": "No",
            "Contract": "Month-to-month",
            "Paperless Billing": "Yes",
            "Payment Method": "Mailed check",
            "Monthly Charges": 53.85,
            "Total Charges": 108.15
        }
    )
    return_probability: bool = Field(default=True, description="Retornar probabilidades?")
    
    @validator('features')
    def features_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Features não pode estar vazio")
        return v


class PredictionResponse(BaseModel):
    """Response com resultado de predição de churn.
    
    Retorna: predição (0/1), probabilidade opcional e tempo de processamento.
    """
    prediction: int = Field(..., description="0=No Churn, 1=Churn")
    probability: Optional[float] = Field(None, description="Probabilidade de churn (0-1)")
    confidence: Optional[float] = Field(None, description="Confiança da predição (0-1)")
    processing_time_ms: float = Field(..., description="Tempo de processamento em ms")


class BatchPredictionRequest(BaseModel):
    """Request para predição em lote.
    
    Aceita lista de clientes para predição simultânea.
    """
    samples: List[Dict[str, Union[str, int, float]]] = Field(
        ..., 
        description="Lista de dicionários com features nomeadas"
    )
    return_probabilities: bool = Field(default=True, description="Retornar probabilidades?")
    
    @validator('samples')
    def samples_not_empty(cls, v):
        if not v or len(v) == 0:
            raise ValueError("Samples não pode estar vazio")
        return v


class BatchPredictionResponse(BaseModel):
    """Response com resultado de predições em lote.
    
    Retorna: lista de predições, probabilidades opcionais, tamanho do lote e tempo.
    """
    predictions: List[int] = Field(..., description="Lista de predições")
    probabilities: Optional[List[float]] = Field(None, description="Lista de probabilidades")
    batch_size: int = Field(..., description="Número de amostras processadas")
    processing_time_ms: float = Field(..., description="Tempo total em ms")


class ModelInfoResponse(BaseModel):
    """Informações do modelo."""
    model_type: str = Field(..., description="Tipo de modelo")
    model_version: str = Field(..., description="Versão do modelo")
    n_features: int = Field(..., description="Número de features")
    features_used: List[str] = Field(..., description="Nomes das features")


class ErrorResponse(BaseModel):
    """Response de erro."""
    error: str = Field(..., description="Mensagem de erro")
    status_code: int = Field(..., description="Código HTTP")
    timestamp: str = Field(..., description="Timestamp do erro")


class ChurnReasonResponse(BaseModel):
    """Explicação de predição de churn."""
    churn_probability: float = Field(..., description="Probabilidade de churn")
    top_risk_factors: List[dict] = Field(..., description="Fatores de risco mais importantes")
    recommendation: str = Field(..., description="Recomendação de ação")
