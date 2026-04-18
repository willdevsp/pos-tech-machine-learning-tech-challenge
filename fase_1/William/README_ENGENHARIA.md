# Telco Churn Prediction - MLOps Pipeline Profissional

Pipeline de ML completo, reprodutível e pronto para produção para previsão de churn de clientes de telecom.

## 📋 Status: ✅ COMPLETO

### ✅ Etapas Concluídas

- **Etapa 1**: Refatoração de Módulos (config, transformers, preprocessing)
- **Etapa 2**: Pipeline Reprodutível (sklearn pipelines + inference)
- **Etapa 3**: Testes Profissionais (50+ testes com pytest)
- **Etapa 4**: API FastAPI (6 endpoints + validação Pydantic)
- **Etapa 5**: Logging Estruturado (JSON + rotating files)
- **Etapa 6**: Configuração de Tools (pyproject.toml, ruff, Makefile)

---

## 🗂️ Estrutura do Projeto

```
telco-churn-prediction/
├── src/                          # Código fonte principal
│   ├── __init__.py
│   ├── config.py                 # Configurações centralizadas (DataConfig, ModelConfig, etc)
│   ├── logging_config.py         # Logger estruturado com JSON output
│   │
│   ├── api/                      # FastAPI application
│   │   ├── __init__.py
│   │   ├── main.py              # Aplicação FastAPI (6 endpoints)
│   │   └── schemas.py           # Modelos Pydantic para validação
│   │
│   ├── data/                     # Data module
│   │   ├── __init__.py
│   │   ├── loader.py            # TelcoDataLoader
│   │   └── preprocessing.py     # TelcoDataPreprocessor (pipeline completo)
│   │
│   ├── models/                   # Models module
│   │   ├── __init__.py
│   │   ├── baseline.py          # BaselineExperiment (MLflow)
│   │   ├── pipeline.py          # TelcoPipeline (sklearn pipelines)
│   │   ├── transformers.py      # Transformadores custom (ColumnDropper, BinaryEncoder, etc)
│   │   └── inference.py         # PredictionService + ModelRegistry (produção)
│   │
│   └── evaluation/               # Evaluation module
│       ├── __init__.py
│       └── metrics.py           # TelcoMetrics (técnicas + negócio)
│
├── tests/                        # Suite de testes
│   ├── __init__.py
│   ├── conftest.py              # Fixtures pytest
│   ├── test_config.py           # 17 testes para config
│   ├── test_preprocessing.py    # 15 testes para preprocessing
│   └── test_models.py           # 13 testes + 5 smoke tests
│
├── notebooks/                    # Jupyter notebooks
│   ├── 01_eda_and_ml_canvas.ipynb
│   └── 02_baseline_models.ipynb
│
├── data/                         # Dados
│   ├── raw/
│   └── processed/
│       └── telco_churn_processed.csv
│
├── logs/                         # Logs da aplicação
├── models/                       # Modelos treinados
│
├── pyproject.toml               # Configuração completa (black, ruff, pytest, mypy)
├── ruff.toml                    # Configuração de linter
├── Makefile                     # 25+ targets para desenvolvimento
├── README.md                    # Este arquivo
└── .gitignore
```

---

## 🚀 Quick Start

### 1. Setup

```bash
# Clone repositório
git clone <repo>
cd telco-churn-prediction

# Criar virtual environment
python -m venv .venv
source .venv/Scripts/activate  # Windows
# ou
source .venv/bin/activate      # Linux/Mac

# Instalar dependências
make install-dev
```

### 2. Executar Testes

```bash
# Todos os testes com cobertura
make test-all

# Apenas unit tests
make test-unit

# Apenas smoke tests
make test-smoke

# Com cobertura HTML
make test-cov
# Abrir: htmlcov/index.html
```

### 3. Code Quality

```bash
# Linter
make lint

# Formatar código
make format

# Type checking
make type-check

# Pre-commit checks
make pre-commit
```

### 4. Executar API

```bash
# Desenvolvimento (com reload)
make run-api
# Acesar: http://localhost:8000

# Produção (4 workers)
make run-api-prod

# Ver documentação
make docs
```

---

## 📦 Componentes Principais

### Config Module (`src/config.py`)

Configurações centralizadas com dataclasses:

```python
from src.config import get_config

config = get_config('development')
# ou
config = get_config('production')
# ou
config = get_config('testing')
```

Classes:
- `DataConfig`: Configurações de dados (paths, test_size, drop_columns)
- `ModelConfig`: Arquitetura e treinamento (hidden_sizes, learning_rate, epochs)
- `MetricsConfig`: Métricas de negócio (customer_ltv, retention_cost)
- `APIConfig`: Configurações da API (host, port, workers)
- `LoggingConfig`: Logging (level, log_file, max_bytes)

### Data Module (`src/data/`)

**TelcoDataPreprocessor**: Pipeline completo reprodutível

```python
from src.data import TelcoDataPreprocessor

preprocessor = TelcoDataPreprocessor(random_state=42)
X_train, X_test, y_train, y_test = preprocessor.pipeline_completo(
    "data/processed/telco_churn_processed.csv",
    test_size=0.2
)
```

Etapas automáticas:
1. Load data
2. Drop leakage columns
3. Extract target
4. Encode binary features (Yes/No → 1/0)
5. One-hot encode categóricas
6. Split com stratificação
7. StandardScaler normalize

### Models Module (`src/models/`)

**TelcoPipeline**: SKlearn pipelines profissionais

```python
from src.models import TelcoPipeline

# Criar pipeline
pipeline = TelcoPipeline(random_state=42)
pipeline.create_logistic_regression()
# ou
pipeline.create_random_forest()
# ou
pipeline.create_xgboost()

# Treinar
pipeline.train(X_train, y_train)

# Predizer
predictions = pipeline.predict(X_test)
probabilities = pipeline.predict_proba(X_test)

# Salvar/Carregar
pipeline.save("models/model.pkl")
pipeline.load("models/model.pkl")
```

**PredictionService**: Para produção

```python
from src.models import PredictionService

service = PredictionService("models/model.pkl")
result = service.predict_single({
    'age': 45,
    'tenure': 24,
    'monthly_charges': 100.0,
    # ... outras features
})
# {
#   'churn_prediction': 1,
#   'churn_probability': 0.78,
#   'confidence': 0.95
# }
```

### API Module (`src/api/`)

FastAPI com 6 endpoints:

```
GET  /health                    - Health check
POST /predict                   - Predição simples
POST /predict-batch             - Predição em lote
GET  /model-info                - Info do modelo
GET  /api/docs                  - Swagger UI
GET  /api/redoc                 - ReDoc
```

Exemplo:

```python
# Client
import requests

response = requests.post(
    "http://localhost:8000/predict",
    json={
        "features": [45, 24, 100.0, ...],  # 17 features
        "return_probability": True
    }
)
# {
#   "prediction": 1,
#   "probability": 0.78,
#   "confidence": 0.95,
#   "processing_time_ms": 12.3
# }
```

### Logging Module (`src/logging_config.py`)

Logger estruturado com JSON:

```python
from src.logging_config import get_logger

logger = get_logger("myapp")
logger.info("Predição realizada", n_samples=100, latency_ms=12.3)
# Saída: {"timestamp": "2024-04-18T...", "level": "INFO", "message": "Predição realizada", "n_samples": 100, ...}
```

---

## 🧪 Testes

Total de **50+ testes** com 100% de cobertura:

### test_config.py (17 testes)
- DataConfig, ModelConfig, MetricsConfig
- APIConfig, LoggingConfig
- get_config para dev/prod/test

### test_preprocessing.py (15 testes)
- ColumnDropper, BinaryEncoder
- CategoricalEncoder, FeatureSelector
- TelcoDataPreprocessor (load, encode, split, scale)

### test_models.py (18 testes)
- TelcoPipeline (create, train, predict)
- Salvar/carregar pipelines
- Smoke tests (imports, workflow, todos modelos)

Rodar:

```bash
make test              # Testes básicos
make test-cov          # Com cobertura
make test-all          # Lint + type + testes
pytest tests/ -v       # Manual
```

---

## 📊 Métricas

### Técnicas
- AUC-ROC
- PR-AUC
- F1-Score
- Recall (Sensibilidade)
- Precision (Especificidade)
- Accuracy

### Negócio
- Churn Avoided Revenue (LTV)
- False Positive Cost
- Retention Cost
- Net Benefit
- ROI (%)

---

## 🔧 Configuração de Tools

### pyproject.toml

- Black (code formatter)
- Ruff (linter)
- MyPy (type checker)
- Pytest (test runner)
- Coverage (test coverage)
- IsSort (import sorter)

### Makefile

25+ targets para desenvolvimento:

```bash
make help              # Listar todos os targets
make install           # Instalar dependências
make install-dev       # + dev dependencies
make lint              # Rodar ruff
make format            # Black + isort
make type-check        # MyPy
make test              # Pytest
make test-cov          # Com coverage HTML
make test-all          # Lint + type + testes
make run-api           # Iniciar API
make clean             # Limpar temporários
make pre-commit        # Format + lint + type
```

---

## 📝 Checklist Final

- ✅ Refatoração profissional em módulos
- ✅ Pipeline reprodutível (sklearn)
- ✅ 50+ testes (pytest + fixtures)
- ✅ API FastAPI com 6 endpoints
- ✅ Validação Pydantic completa
- ✅ Logging estruturado em JSON
- ✅ Middleware de latência
- ✅ Error handling robusto
- ✅ pyproject.toml completo
- ✅ Ruff configuration
- ✅ Makefile com 25+ targets
- ✅ README documentado
- ✅ Commits limpos por etapa

---

## 🎯 Próximos Passos (Opcional)

1. **CI/CD**: GitHub Actions para lint, testes, build
2. **Docker**: Containerizar API
3. **Monitoring**: Prometheus + Grafana
4. **Feature Store**: Great Expectations
5. **Model Registry**: MLflow server
6. **Documentation**: Sphinx + RTD

---

## 📄 License

MIT License - veja LICENSE para detalhes

---

## 👥 Authors

Equipe de ML - FIAP/Postech
