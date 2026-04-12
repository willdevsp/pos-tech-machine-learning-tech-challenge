# 📞 Previsão de Churn - Rede Neural com PyTorch

**Projeto de ML End-to-End**: Sistema de alerta precoce para identificar clientes com alto risco de cancelamento em uma operadora de telecomunicações.

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-red.svg)](https://pytorch.org/)
[![MLflow](https://img.shields.io/badge/MLflow-2.10+-green.svg)](https://mlflow.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Tabela de Conteúdos

- [Visão Geral](#visão-geral)
- [Quick Start](#quick-start)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Dados](#dados)
- [Modelagem](#modelagem)
- [API](#api)
- [Monitoramento](#monitoramento)
- [Contribuição](#contribuição)

---

## 🎯 Visão Geral

### Proposta de Valor
Implementar um **sistema de alerta precoce** que identifique clientes com alta propensão ao cancelamento, permitindo ações de retenção personalizadas antes do encerramento do contrato.

### Métricas de Sucesso

| Métrica | Target | Status |
|---------|--------|--------|
| **F1-Score** | > 0.70 | 🚀 Em Desenvolvimento |
| **AUC-ROC** | > 0.85 | 🚀 Em Desenvolvimento |
| **Recall** | ≥ 0.80 | 🚀 Em Desenvolvimento |
| **Latência API** | < 200ms | 🚀 Em Desenvolvimento |

### Padrões Críticos Identificados (EDA)

```
🔴 ALTO CHURN:
  • Contratos mês-a-mês: 42.71%
  • Fibra Óptica: 41.89%
  • Electronic Check Payment: 45.29%

🟢 BAIXO CHURN:
  • Contratos 2 anos: 2.83%
  • Sem Internet: 7.40%
  • Pagamento automático: ~16%
```

---

## 🚀 Quick Start

### 1. Pré-requisitos
- Python ≥ 3.10
- pip ou conda
- Git

### 2. Clone o Repositório
```bash
git clone https://github.com/seu-user/telco-churn-prediction.git
cd telco-churn-prediction
```

### 3. Setup do Ambiente
```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências
pip install -e ".[dev]"
```

### 4. Download dos Dados
```bash
# Os dados já devem estar em: data/raw/Telco_customer_churn.xlsx
# Se não estiverem, download em: https://www.kaggle.com/blastchar/telco-customer-churn
```

### 5. Executar EDA
```bash
cd notebooks
jupyter notebook 01_eda_and_ml_canvas.ipynb

# Ou rodar script Python
cd ..
python 01_eda_analysis.py
```

---

## 📂 Estrutura do Projeto

```
telco-churn-prediction/
├── 📄 README.md                        # Este arquivo
├── 📄 pyproject.toml                   # Dependências e config
├── 📄 .gitignore                       # Arquivos ignorados
├── 📄 Telco_customer_churn.xlsx        # Dataset original
│
├── 📁 data/
│   ├── raw/                            # Dados brutos (não versionados)
│   │   └── .gitkeep
│   └── processed/                      # Dados processados
│       └── telco_churn_processed.csv   # ✅ Dataset limpo
│
├── 📁 notebooks/
│   ├── 01_eda_and_ml_canvas.ipynb      # ✅ EDA + ML Canvas
│   ├── 02_baseline_models.ipynb        # 🚀 Baselines
│   └── 03_neural_network.ipynb         # 🚀 MLP + PyTorch
│
├── 📁 src/
│   ├── __init__.py
│   ├── data/
│   │   ├── loader.py                   # Carregamento de dados
│   │   └── preprocessing.py            # Pipeline de prep
│   ├── models/
│   │   ├── baseline.py                 # Modelos baseline
│   │   └── neural_network.py           # MLP com PyTorch
│   ├── evaluation/
│   │   ├── metrics.py                  # Métricas customizadas
│   │   └── fairness.py                 # Análise de viés
│   └── api/
│       ├── main.py                     # FastAPI app
│       └── schemas.py                  # Pydantic models
│
├── 📁 tests/
│   ├── test_data.py                    # Testes de dados
│   ├── test_models.py                  # Testes de modelos
│   └── test_api.py                     # Testes da API
│
├── 📁 docs/
│   ├── ml_canvas.md                    # ✅ ML Canvas
│   ├── RELATORIO_EDA.md                # ✅ Relatório EDA
│   ├── MODEL_CARD.md                   # 🚀 Model Card
│   └── DEPLOYMENT.md                   # 🚀 Guia deploy
│
├── 📁 models/
│   ├── baseline_model.pkl              # 🚀 Baseline treinado
│   ├── neural_network.pth              # 🚀 MLP treinado
│   └── .gitkeep
│
└── 📁 .github/
    └── workflows/
        └── ml_pipeline.yml             # 🚀 CI/CD GitHub Actions
```

---

## 📊 Dados

### Dataset: IBM Telco Customer Churn

| Propriedade | Valor |
|-------------|-------|
| **Registros** | 7,043 clientes |
| **Variáveis** | 33 features |
| **Target** | Churn (Yes/No) |
| **Desbalanceamento** | 73.5% No / 26.5% Yes (razão 1:2.77) |
| **Período** | Dados históricos |

### variáveis Principais

**Numéricas**:
- `Tenure Months` (0-72): Meses como cliente
- `Monthly Charges` ($18-$119): Fatura mensal
- `Total Charges` ($0-$8685): Total gasto

**Categóricas Críticas**:
- `Contract`: Month-to-month / One year / Two year
- `Internet Service`: DSL / Fiber optic / No
- `Payment Method`: Electronic check / Bank transfer / Credit card / Mailed check
- `Senior Citizen`: Yes / No
- Outros: Phone Service, Tech Support, Online Security, etc.

### Data Quality

✅ **Limpeza Realizada**:
- Conversão de `Total Charges` (string → float)
- Tratamento de 11 NaNs em clientes novos
- Validação de tipos de dados
- Verificação de integridade referencial

---

## 🤖 Modelagem

### Etapas Planejadas

#### ✅ Etapa 1: Entendimento (COMPLETO)
- [x] ML Canvas
- [x] EDA exploratória
- [x] Análise de qualidade de dados
- [x] Identificação de padrões

#### 🚀 Etapa 2: Modelagem
- [ ] Baselines (DummyClassifier, LogReg)
- [ ] Rede Neural MLP (3 camadas)
- [ ] Early Stopping + LR Scheduler
- [ ] Comparação de modelos
- [ ] MLflow tracking

#### 🚀 Etapa 3: API e Engenharia
- [ ] Refatoração modular
- [ ] Pipeline sklearn
- [ ] Testes automatizados
- [ ] API FastAPI
- [ ] Docker container

#### 🚀 Etapa 4: Documentação
- [ ] Model Card
- [ ] Análise de Fairness
- [ ] Plano de monitoramento
- [ ] Apresentação STAR (video)

### Modelos Planejados

```python
# Baselines
1. DummyClassifier (strategy='stratified')
2. LogisticRegression (sklearn)

# Tree-based
3. RandomForest (sklearn)
4. XGBoost (xgboost)

# Neural Network (Principal)
5. MLP 3-layer (PyTorch)
   - Input → Dense(128) → ReLU → Dropout(0.3)
            → Dense(64) → ReLU → Dropout(0.3)
            → Dense(32) → ReLU → Dropout(0.3)
            → Dense(1) → Sigmoid
   - Loss: BCEWithLogitsLoss (com class weights)
   - Optimizer: Adam (LR=0.001)
   - Early Stopping: validation loss (patience=20)
```

---

## 🌐 API

### Endpoints Planejados (Etapa 3)

```bash
# GET - Health check
curl http://localhost:8000/health

# POST - Prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "tenure_months": 12,
    "monthly_charges": 65.50,
    "contract": "Month-to-month",
    "internet_service": "Fiber optic",
    "payment_method": "Electronic check"
  }'

# Response
{
  "customer_id": "XXXX-YYYY",
  "churn_probability": 0.78,
  "churn_prediction": "Yes",
  "confidence": 0.85,
  "risk_level": "HIGH",
  "recommended_actions": [
    "Oferecer upgrade para contrato 2 anos",
    "Investigar satisfação com Fibra",
    "Converter para pagamento automático"
  ],
  "inference_time_ms": 45.2
}
```

---

## 📈 Monitoramento

### Métricas Rastreadas (MLflow)

```
Experiments:
  ├── Baseline
  │   ├── DummyClassifier
  │   └── LogisticRegression
  ├── Tree Models
  │   ├── RandomForest
  │   └── XGBoost
  └── Neural Networks
      ├── MLP_v1 (64-32-16)
      ├── MLP_v2 (128-64-32) ← Melhor
      └── MLP_v3 (256-128-64)

Métricas:
  • F1-Score
  • AUC-ROC
  • Recall
  • Precision
  • Accuracy
  • Tempo de treino
```

### Análise de Fairness (Planejada)

```python
Grupos Sensíveis:
  • Senior Citizen (Yes/No)
  • Gender (M/F)
  • Region (State)

Métricas Fairness:
  • Taxa de Seleção (Selection Rate Difference)
  • Disparidade de Falso Negativo
```

---

## 🔧 Desenvolvimento

### Ambiente de Dev

```bash
# Instalar dependências de desenvolvimento
pip install -e ".[dev]"

# Linting com ruff
ruff check src/ tests/
ruff format src/ tests/

# Type checking com mypy
mypy src/

# Testes com pytest
pytest tests/ -v --cov=src

# Executar notebook
jupyter notebook notebooks/
```

### Git Workflow

```bash
# Feature branch
git checkout -b feature/seu-feature

# Commit com mensagens claras
git commit -m "feat: adiciona preprocessing module"

# Push e PR
git push origin feature/seu-feature
```

---

## 📝 Documentação

- [ML Canvas](docs/ml_canvas.md) - Definição de negócio
- [Relatório EDA](docs/RELATORIO_EDA.md) - Análise exploratória ✅
- [Model Card](docs/MODEL_CARD.md) - Características do modelo 🚀
- [Deployment Guide](docs/DEPLOYMENT.md) - Deploy em produção 🚀

---

## 📚 Referências

- [IBM Telco Dataset](https://www.kaggle.com/blastchar/telco-customer-churn)
- [PyTorch Docs](https://pytorch.org/docs/stable/index.html)
- [MLflow Guide](https://mlflow.org/docs/latest/index.html)

---

## 📝 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes

---

## 👥 Contribuidores

| Nome | Role | Status |
|------|------|--------|
| Equipe de ML | Lead | ✅ Ativo |
| Data Engineer | Suporte | ✅ Ativo |

---

## 📞 Contato & Suporte

- **Issues**: GitHub Issues
- **Discussões**: GitHub Discussions
- **Email**: ml@telecom.com
- **Slack**: #ml-churn-prediction

---

**Last Updated**: Abril 2026  
**Status**: 🟢 Etapas 1 & 2 Completas - Pronto para Etapa 2
