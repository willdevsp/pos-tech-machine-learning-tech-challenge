# PLANO ETAPA 1: Clean Code + Estrutura Inicial

## TL;DR
Setup repositório profissional com estrutura modular, design patterns (Factory + Strategy), type hints completos, e linting passando. Base sólida para as próximas etapas.

## Steps

### 1.1 Preparar Repositório GitHub
- Criar repo: `rocket-tail-recommendation`
- Clonar localmente
- Criar branches: `main`, `develop`
- Configurar `.gitignore` (Python + IDE: `__pycache__`, `.venv`, `.env`, `*.egg-info`)
- Configurar `.env.example` (variáveis de exemplo sem valores)

### 1.2 Estrutura Monorepo por Objetivo

**Padrão**: Monorepo com componentes isolados, cada um com seus testes e CI/CD separado.

```
rocket-tail-recommendation/

# 1. COMPONENTE: TREINAMENTO
training/
├── pyproject.toml        # Deps: torch, sklearn, mlflow, dvc
├── src/
│   └── rocket_tail_training/
│       ├── __init__.py
│       ├── config.py     # Config específico (epochs, batch_size)
│       ├── preprocess.py # Data loading + cleanup
│       ├── features.py   # Feature engineering
│       ├── train.py      # Training loop
│       ├── evaluate.py   # Baselines + metrics
│       └── utils.py      # Helpers
├── tests/
│   ├── conftest.py
│   ├── test_preprocess.py
│   ├── test_features.py
│   ├── test_train.py
│   └── test_evaluate.py
├── dvc.yaml              # Pipeline stages
├── scripts/
│   ├── run_pipeline.sh
│   └── push_models.sh
├── .github/workflows/
│   └── train.yml         # Trigger: training/**
└── README.md

# 2. COMPONENTE: API REST
api/
├── pyproject.toml        # Deps: fastapi, uvicorn, pydantic, torch
├── src/
│   └── rocket_tail_api/
│       ├── __init__.py
│       ├── config.py     # API config (port, workers)
│       ├── app.py        # FastAPI app + endpoints
│       ├── models.py     # Request/response models (Pydantic)
│       ├── service.py    # Lógica de recomendação
│       └── utils.py      # Helpers
├── tests/
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_service.py
│   └── test_models.py
├── Dockerfile            # Multi-stage
├── docker-compose.yml    # Local dev
├── .github/workflows/
│   └── api.yml           # Trigger: api/**, shared/**
└── README.md

# 3. COMPONENTE: MLFLOW SERVER
mlflow-server/
├── Dockerfile            # Custom MLflow image
├── docker-compose.yml    # MLflow + S3 local (MinIO)
├── configs/
│   ├── mlflow.conf
│   └── nginx.conf        # (opcional, reverse proxy)
├── scripts/
│   ├── init_server.sh
│   └── backup_artifacts.sh
├── .github/workflows/
│   └── mlflow.yml        # Trigger: mlflow-server/**
└── README.md

# 4. COMPONENTE: CÓDIGO COMPARTILHADO
shared/
├── pyproject.toml        # Package: rocket_tail_shared
├── src/
│   └── rocket_tail_shared/
│       ├── __init__.py
│       ├── models/       # PyTorch model classes (HybridNN, EmbeddingLayer)
│       ├── config/       # Pydantic Settings
│       ├── utils/        # Logging, helpers (usados por training + api)
│       ├── ml/
│       │   ├── factory.py        # ModelFactory
│       │   ├── baselines.py      # Sklearn baselines
│       │   └── metrics.py        # NDCG, Precision@K, etc
│       └── data/         # Common data structures
├── tests/
│   ├── conftest.py
│   └── test_factory.py
├── .github/workflows/
│   └── shared.yml        # Trigger: shared/**
└── README.md

# 5. COMPONENTE: INFRASTRUCTURE
terraform/
├── main.tf               # Provider, backend
├── variables.tf
├── outputs.tf
├── ecr.tf                # ECR repository
├── s3.tf                 # S3 buckets
├── iam.tf                # IAM roles + policies
├── lambda.tf             # Lambda + API Gateway
├── versions.tf
├── terraform.tfvars.example
├── .github/workflows/
│   └── terraform.yml     # Trigger: terraform/**
├── .terraform.lock.hcl
└── README.md

# 6. ROOT LEVEL
├── .github/
│   ├── workflows/
│   │   ├── train.yml           # Testa training/
│   │   ├── api.yml             # Testa api/ + shared/
│   │   ├── mlflow.yml          # Valida mlflow-server/
│   │   ├── shared.yml          # Testa shared/
│   │   └── terraform.yml       # Plan terraform/
│   └── pull_request_template.md
├── docs/
│   ├── ARCHITECTURE.md   # Visão geral monorepo
│   ├── CONTRIBUTING.md
│   └── WORKFLOWS.md      # GitHub Actions explícito
├── data/                 # (gitignored, local only)
│   ├── raw/
│   ├── processed/
│   └── features/
├── .gitignore            # Completo
├── .env.example
├── README.md             # Root: como clonar + rodar cada componente
├── renovate.json         # Dependências automáticas (optional)
└── Makefile              # Shortcuts (optional)
```

**Vantagens desta estrutura**:
- ✅ **Isolamento**: Cada componente (`api/`, `training/`, `shared/`) tem suas dependências isoladas em seu próprio `pyproject.toml`.
- ✅ **CI/CD eficiente**: Workflows rodam no GitHub Actions apenas se o respectivo componente ou o pacote `shared/` for modificado.
- ✅ **Imagens Otimizadas**: A API REST (`api/`) não carrega dependências de treinamento pesadas (como DVC), diminuindo drasticamente o tamanho do container Docker e mitigando cold starts no AWS Lambda.
- ✅ **Reutilização de Código**: Todo o código comum de modelos, baselines e métricas fica centralizado em `shared/` e é importado localmente.


### 1.3 Design Patterns

#### Pattern 1: Factory Pattern (para criar modelos)
**Arquivo**: `shared/src/rocket_tail_shared/ml/model_factory.py`

- Classe `ModelFactory` com método estático `create_model(model_type, config)`
- Suporta: `"mlp_collaborative"`, `"mlp_content_based"`, `"hybrid"`
- Cada tipo retorna modelo configurado (será usado na Etapa 4)
- Permite fácil extensão sem modificar código existente

#### Pattern 2: Strategy Pattern (para preprocessadores)
**Arquivo**: `shared/src/rocket_tail_shared/data/preprocessing.py`

- Interface `PreprocessingStrategy` (ABC)
- Implementações: `NormalizationStrategy`, `DropMissingStrategy`, `EncodingStrategy`
- Contexto `DataPreprocessor` que aplica strategies sequencialmente
- Config define qual strategy usar via YAML

### 1.3.5 Shared Package Setup
**Arquivo**: `shared/pyproject.toml`

```toml
[project]
name = "rocket-tail-shared"
version = "1.0.0"
dependencies = [
    "torch>=2.0",
    "scikit-learn>=1.3",
    "pydantic>=2.0",
    "loguru>=0.7"
]
```

**Instalação em training/ e api/**:
```toml
# Em training/pyproject.toml e api/pyproject.toml
dependencies = [
    "rocket-tail-shared @ file://../shared"
]
```

Permitir importações como:
```python
from rocket_tail_shared.models import HybridNN
from rocket_tail_shared.ml.factory import ModelFactory
from rocket_tail_shared.config import settings
```

### 1.4 GitHub Actions com Path Triggers

**Arquivo**: `.github/workflows/train.yml`

```yaml
name: Training Pipeline
on:
  push:
    branches: [main, develop]
    paths:
      - 'training/**'
      - 'shared/**'
      - '.github/workflows/train.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'training/**'
      - 'shared/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: cd training && poetry install
      - name: Lint with Ruff
        run: cd training && poetry run ruff check src/ tests/
      - name: Run pytest
        run: cd training && poetry run pytest tests/ -v --cov=src
      - name: Test DVC pipeline
        run: cd training && poetry run dvc dag --check
```

**Arquivo**: `.github/workflows/api.yml`

```yaml
name: API Build & Push
on:
  push:
    branches: [main, develop]
    paths:
      - 'api/**'
      - 'shared/**'
      - '.github/workflows/api.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'api/**'
      - 'shared/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: cd api && poetry install
      - name: Lint with Ruff
        run: cd api && poetry run ruff check src/ tests/
      - name: Run pytest
        run: cd api && poetry run pytest tests/ -v --cov=src

  build-and-push-ecr:
    needs: test
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Login to ECR
        run: |
          aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com
      - name: Build and push image
        run: |
          docker build -t rocket-tail-api:${{ github.sha }} api/
          docker tag rocket-tail-api:${{ github.sha }} ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/rocket-tail-api:latest
          docker push ${{ secrets.AWS_ACCOUNT_ID }}.dkr.ecr.us-east-1.amazonaws.com/rocket-tail-api:latest
```

**Arquivo**: `.github/workflows/terraform.yml`

```yaml
name: Terraform Plan & Apply
on:
  push:
    branches: [main, develop]
    paths:
      - 'terraform/**'
      - '.github/workflows/terraform.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'terraform/**'

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Terraform Init
        run: cd terraform && terraform init
      - name: Terraform Plan
        run: cd terraform && terraform plan -out=tfplan
      - name: Upload plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: terraform/tfplan

  apply:
    needs: plan
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production  # Requer aprovação manual
    steps:
      - uses: actions/checkout@v3
      - uses: hashicorp/setup-terraform@v2
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      - name: Download plan
        uses: actions/download-artifact@v3
        with:
          name: tfplan
          path: terraform/
      - name: Terraform Apply
        run: cd terraform && terraform apply tfplan
```

**Arquivo**: `.github/workflows/shared.yml`

```yaml
name: Shared Package Tests
on:
  push:
    branches: [main, develop]
    paths:
      - 'shared/**'
      - '.github/workflows/shared.yml'
  pull_request:
    branches: [main, develop]
    paths:
      - 'shared/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install Poetry
        run: pip install poetry
      - name: Install dependencies
        run: cd shared && poetry install
      - name: Lint with Ruff
        run: cd shared && poetry run ruff check src/ tests/
      - name: Run pytest
        run: cd shared && poetry run pytest tests/ -v --cov=src
```

**Como funciona**:
- GitHub Actions monitora mudanças em pastas específicas via `paths`
- Quando `api/**` muda → rodar `api.yml` automaticamente
- Quando `terraform/**` muda → rodar `terraform.yml` (manual apply)
- Paralelo: Se `api/` e `training/` mudam juntos → ambos rodam em paralelo
- Economia: `mlflow-server/` não dispara se só `training/` foi alterado

### 1.5 Type Hints + Docstrings

- **Todas as funções públicas** nos pacotes do Monorepo (`shared/src/rocket_tail_shared/`, `training/src/rocket_tail_training/`, `api/src/rocket_tail_api/`) recebem type hints
- Docstrings Google style: descrição, Args, Returns, Raises
- Use `typing.Optional`, `List`, `Dict`, `Union` conforme necessário
- Exemplos:
  ```python
  def load_events(path: str, nrows: Optional[int] = None) -> pd.DataFrame:
      """Carrega dataset de eventos.
      
      Args:
          path: Caminho para arquivo CSV
          nrows: Número máximo de linhas (None = todas)
      
      Returns:
          DataFrame com colunas: timestamp, visitorid, event, itemid, transactionid
      
      Raises:
          FileNotFoundError: Se arquivo não existir
      """
  ```

### 1.6 Configuração de Linting + Code Quality
**Arquivo**: `pyproject.toml` na raiz do projeto (para configurações globais de ferramentas)

```toml
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "N", "UP", "C90"]  # Errors, Flake8, Import sort, Naming, Upgrade, McCabe
ignore = ["E501"]  # Linha longa (já tem line-length)

[tool.ruff.lint.isort]
known-first-party = ["rocket_tail_shared", "rocket_tail_training", "rocket_tail_api"]
```

- Executar: `poetry run ruff check .` na raiz
- Pre-commit hook: Ruff roda antes de commit a nível global
- **Entregável**: Zero erros do Ruff em todos os pacotes

### 1.7 Arquivo: pre-commit Configuration
**Arquivo**: `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.0
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
```

- Instalar: `pre-commit install`
- Roda automaticamente antes de commits

### 1.8 README Inicial
**Arquivo**: `README.md`

Seções:
1. **O Projeto**: 1 parágrafo sobre RocketTail
2. **Estrutura**: árvore resumida
3. **Setup Local**: `poetry install`, `pre-commit install`
4. **Próximas Etapas**: Link para PLANO_ETAPA_2
5. **Contribuindo**: Naming conventions, commit semântico

### 1.9 Testes Unitários Base
**Arquivo**: `tests/__init__.py`, `tests/conftest.py`

- Setup pytest com fixtures básicas
- Mock dados pequenos para testes
- Teste que import dos módulos funciona
- Exemplo test: verificar que Factory retorna modelo correto

**Comandos**: 
* Rodar testes de todos os módulos:
  `cd shared && poetry run pytest tests/ -v`
  `cd ../training && poetry run pytest tests/ -v`
  `cd ../api && poetry run pytest tests/ -v`

## Relevant files
- `shared/src/rocket_tail_shared/models/` — PyTorch models (HybridNN, EmbeddingLayer)
- `shared/src/rocket_tail_shared/ml/model_factory.py` — Factory pattern para modelos
- `shared/src/rocket_tail_shared/ml/baselines.py` — Strategy pattern para preprocessamento
- `training/src/rocket_tail_training/` — Scripts de treinamento e pipeline DVC
- `api/src/rocket_tail_api/` — FastAPI application
- `.github/workflows/train.yml`, `api.yml`, `shared.yml`, `terraform.yml` — CI/CD com path triggers
- `.pre-commit-config.yaml` — Hooks automáticos (root level)
- `shared/pyproject.toml`, `training/pyproject.toml`, `api/pyproject.toml` — Deps por componente

## Verification
1. **Estrutura monorepo** criada com 5 componentes: `training/`, `api/`, `mlflow-server/`, `shared/`, `terraform/`
2. **Cada componente** tem `pyproject.toml` independente com deps isoladas
3. **GitHub Actions workflows** criados com path triggers (alterações em `api/**` → roda `api.yml`)
4. **Ruff check** passa sem erros em cada componente
5. **Pre-commit funciona**: Faça commit teste, deve passar automaticamente
6. **Imports funcionam**: `from rocket_tail_shared.models import HybridNN` sem erro
7. **README claro**: Descreve estrutura monorepo e como setup cada componente

## Decisions
- **Monorepo pattern**: 1 repo com 5 componentes isolados (vs. 5 repos separados)
  - Vantagem: Fácil refatoração, histórico compartilhado
  - Desvantagem: Mais complexo, mas CI/CD com path filters resolve
- **Shared package local**: Via `file://` path no Poetry (vs. PyPI)
  - Simplicidade durante desenvolvimento
  - Será publicado no PyPI em futuro se necessário
- **GitHub Actions obrigatório nesta etapa**: Path triggers reduzem CI overhead drasticamente
- **Sem SageMaker, Kubernetes, etc**: Manter simples para 1 pessoa, 2-3 semanas

## Further Considerations
1. **GitHub Branch Protection**: Ativar após Etapa 1
   - Require status checks (CI/CD workflows)
   - Require reviews antes de merge em `main`
2. **Monorepo Tooling (futuro)**: Se crescer, usar Nx, Turborepo (agora é overhead)
3. **Naming**: `rocket_tail` vs `retailrocket`? Usar `rocket_tail` para brand do projeto, `retailrocket` para dataset

---

**Duração Estimada**: 4-5 horas (monorepo setup + workflows + design patterns)  
**Próxima Etapa**: PLANO_ETAPA_2_AMBIENTE.md
