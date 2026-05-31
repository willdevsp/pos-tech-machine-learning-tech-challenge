# PLANO ETAPA 2: Ambiente + Dependências + Tracking

## TL;DR
Setup reproduzível com Poetry, Pydantic Settings, Docker multi-stage, MLflow local, DVC init com remote S3. Resultado: `poetry install` em ambiente novo tem tudo funcionando.

## Steps

### 2.1 Configurar Poetry (pyproject.toml)

No padrão Monorepo, cada componente gerencia de forma independente suas dependências e ambiente virtual (`poetry` em cada subpasta). O pacote `shared` é instalado como link local de desenvolvimento.

#### A) Módulo Compartilhado (`shared/pyproject.toml`)
```toml
[tool.poetry]
name = "rocket-tail-shared"
version = "1.0.0"
description = "Classes comuns, Pydantic settings, baselines e métricas"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
torch = "^2.0"
scikit-learn = "^1.3"
pandas = "^2.0"
numpy = "^1.24"
pydantic = "^2.0"
pydantic-settings = "^2.0"
loguru = "^0.7"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

#### B) Módulo de Treinamento (`training/pyproject.toml`)
```toml
[tool.poetry]
name = "rocket-tail-training"
version = "1.0.0"
description = "Pipeline DVC e scripts de treinamento"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
rocket-tail-shared = { path = "../shared", develop = true }
mlflow = "^2.8"
duckdb = "^0.9"
click = "^8.1"
python-dotenv = "^1.0"
pyyaml = "^6.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-cov = "^4.1"
ruff = "^0.1"
dvc = "^3.0"
dvc-s3 = "^3.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

#### C) Módulo da API REST (`api/pyproject.toml`)
```toml
[tool.poetry]
name = "rocket-tail-api"
version = "1.0.0"
description = "FastAPI endpoints e Lambda handler"
authors = ["Your Name <you@example.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.10"
rocket-tail-shared = { path = "../shared", develop = true }
fastapi = "^0.104"
uvicorn = { extras = ["standard"], version = "^0.24" }
mlflow = "^2.8"
aws-lambda-powertools = "^2.24"
python-dotenv = "^1.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.4"
pytest-cov = "^4.1"
pytest-asyncio = "^0.21"
ruff = "^0.1"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"
```

**Instalação**:
Em cada diretório (`shared/`, `training/`, `api/`), execute `poetry install` para gerar seus respectivos `poetry.lock`.

### 2.2 Environment Variables (.env + Pydantic Settings)
**Arquivo**: `.env.example`

```env
# Environment
ENVIRONMENT=local
LOG_LEVEL=INFO

# Paths
DATA_DIR=./data
MODELS_DIR=./models
CONFIG_DIR=./configs

# MLflow
MLFLOW_TRACKING_URI=http://localhost:5000
MLFLOW_EXPERIMENT_NAME=rocket-tail-experiments

# DVC & Data
DVC_REMOTE=s3://rocket-tail-data
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789

# API
API_HOST=0.0.0.0
API_PORT=8000

# Database
DUCKDB_PATH=./data/rocket_tail.db

# Model config
MODEL_TYPE=hybrid
EMBEDDING_DIM=32
BATCH_SIZE=32
EPOCHS=100
```

**Arquivo**: `shared/src/rocket_tail_shared/config/settings.py`

```python
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    environment: str = "local"
    log_level: str = "INFO"
    
    # Paths (relativos à raiz do monorepo, ajustável via .env)
    data_dir: Path = Path("../data")
    models_dir: Path = Path("../models")
    config_dir: Path = Path("../configs")
    
    mlflow_tracking_uri: str = "http://localhost:5000"
    mlflow_experiment_name: str = "rocket-tail-experiments"
    
    dvc_remote: str = "s3://rocket-tail-data"
    aws_region: str = "us-east-1"
    
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    duckdb_path: Path = Path("../data/rocket_tail.db")
    
    model_type: str = "hybrid"
    embedding_dim: int = 32
    batch_size: int = 32
    epochs: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    def validate_paths(self):
        """Cria diretórios se não existirem."""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.config_dir.mkdir(parents=True, exist_ok=True)

# Global settings instance
settings = Settings()
settings.validate_paths()
```

**Uso**:
```python
from rocket_tail_shared.config.settings import settings
print(settings.mlflow_tracking_uri)
```

### 2.3 Docker Multi-Stage Base
**Arquivo**: `api/Dockerfile`

Como a API é um componente independente no monorepo, seu `Dockerfile` está contido dentro da pasta `api/` e realiza o build copiando o módulo `shared/` para satisfazer as dependências locais.

```dockerfile
# Stage 1: Builder
FROM python:3.10-slim as builder

WORKDIR /build
RUN pip install poetry

# Copia configurações dos componentes
COPY shared/ /build/shared/
COPY api/ /build/api/

WORKDIR /build/api
RUN poetry export -f requirements.txt --without-hashes > requirements.txt

# Stage 2: Runtime
FROM python:3.10-slim

WORKDIR /app
COPY --from=builder /build/api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia códigos fontes
COPY shared/ /app/shared/
COPY api/ /app/api/

# Instala pacotes locais
RUN pip install -e /app/shared -e /app/api

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

CMD ["uvicorn", "rocket_tail_api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Build local (executar a partir da raiz do repositório)**:
```bash
docker build -t rocket-tail-api:dev -f api/Dockerfile .
docker run --rm -p 8000:8000 rocket-tail-api:dev
```

### 2.4 MLflow Setup (Local)
**Arquivo**: `scripts/setup_mlflow.sh`

```bash
#!/bin/bash
set -e

echo "Initializing MLflow..."

# Criar diretório para artifacts
mkdir -p mlflow_artifacts

# Criar diretório para backend (SQLite)
mkdir -p mlflow_backend

# Comando para rodar MLflow
echo "To start MLflow server, run:"
echo "  mlflow server --host 0.0.0.0 --port 5000 \\"
echo "    --backend-store-uri sqlite:///mlflow_backend/mlflow.db \\"
echo "    --default-artifact-root ./mlflow_artifacts"
```

**Arquivo**: `docker-compose.yml`

```yaml
version: '3.9'

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - mlflow_backend:/mlflow_backend
      - mlflow_artifacts:/mlflow_artifacts
    command: >
      mlflow server 
      --host 0.0.0.0 
      --port 5000
      --backend-store-uri sqlite:////mlflow_backend/mlflow.db
      --default-artifact-root /mlflow_artifacts
    environment:
      - MLFLOW_TRACKING_URI=http://localhost:5000

volumes:
  mlflow_backend:
  mlflow_artifacts:
```

**Setup MLflow client**:

**Arquivo**: `shared/src/rocket_tail_shared/ml/mlflow_utils.py`

```python
import mlflow
from rocket_tail_shared.config.settings import settings

def setup_mlflow():
    """Inicializa MLflow com tracking URI."""
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    mlflow.set_experiment(settings.mlflow_experiment_name)

def log_parameters(params: dict):
    """Log parameters para run atual."""
    mlflow.log_params(params)

def log_metrics(metrics: dict):
    """Log metrics para run atual."""
    mlflow.log_metrics(metrics)

def log_model(model, artifact_path: str = "model"):
    """Salva modelo como artifact."""
    mlflow.pytorch.log_model(model, artifact_path)
```

### 2.5 DVC Initialization
**Arquivo**: `scripts/setup_dvc.sh`

```bash
#!/bin/bash
set -e

echo "Initializing DVC..."

# Inicializa DVC (cria .dvc/, .dvcignore)
dvc init --no-scm

# Configura remote S3
DVC_REMOTE="s3://rocket-tail-data/$(date +%Y%m%d)"
dvc remote add -d s3remote ${DVC_REMOTE}
dvc remote modify s3remote profile default  # Usa AWS default profile

echo "DVC initialized with remote: ${DVC_REMOTE}"
echo "Next: Run 'dvc add data/raw/events.csv' to track dataset"
```

**Arquivo**: `.dvc/config` (após setup)

```ini
[core]
    analytics = false
    autostage = true
['remote "s3remote"']
    url = s3://rocket-tail-data
    profile = default
    ssl_verify = true
```

**Arquivo**: `.dvcignore`

```
# Ignora cache
.dvc
*.dvc

# Ignora processed data durante tracking
*.pyc
__pycache__
.env

# IDE
.vscode
.idea
```

### 2.6 Environment Validation Script
**Arquivo**: `scripts/validate_env.py`

```python
#!/usr/bin/env python3
"""Valida setup de ambiente do Monorepo."""

import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Python 3.10+."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        print("✅ Python version OK:", f"{version.major}.{version.minor}")
        return True
    print("❌ Python 3.10+ required")
    return False

def check_poetry():
    """Poetry instalado."""
    try:
        subprocess.run(["poetry", "--version"], capture_output=True, check=True)
        print("✅ Poetry installed")
        return True
    except:
        print("❌ Poetry not installed. Run: pip install poetry")
        return False

def check_directories():
    """Diretórios do Monorepo existem."""
    dirs = ["shared", "training", "api", "mlflow-server", "terraform"]
    all_exist = all(Path(d).exists() for d in dirs)
    
    if all_exist:
        print("✅ Monorepo directory structure OK")
        return True
    else:
        print("❌ Missing monorepo directories. Check your repo structure.")
        return False

def check_env_file():
    """.env existe."""
    if Path(".env").exists():
        print("✅ .env file exists")
        return True
    else:
        print("⚠️  .env not found. Using defaults from .env.example")
        return True  # Não bloqueia

def main():
    """Run all checks."""
    checks = [
        check_python_version,
        check_poetry,
        check_directories,
        check_env_file,
    ]
    
    results = [check() for check in checks]
    
    if all(results):
        print("\n✅ Environment validation passed!")
        return 0
    else:
        print("\n❌ Environment validation failed. Fix errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
```

**Usar**:
```bash
chmod +x scripts/validate_env.py
python scripts/validate_env.py
```

### 2.7 Setup Scripts
**Arquivo**: `scripts/setup_local.sh`

```bash
#!/bin/bash
set -e

echo "=== RocketTail Local Setup ==="

# 1. Instalar dependências em cada módulo
echo "1. Installing dependencies in monorepo modules..."
cd shared && poetry install
cd ../training && poetry install
cd ../api && poetry install
cd ..

# 2. Pre-commit hooks
echo "2. Setting up pre-commit hooks..."
poetry run pre-commit install

# 3. Validate environment
echo "3. Validating environment..."
python scripts/validate_env.py

echo "✅ Setup complete!"
echo "Next steps:"
echo "1. Start MLflow + API locally using: docker-compose up"
echo "2. Configure AWS credentials: aws configure"
echo "3. Run: bash training/scripts/setup_dvc.sh (Etapa 3)"
```

**Instalar tudo**:
```bash
bash scripts/setup_local.sh
```

### 2.8 .gitignore Completo
**Arquivo**: `.gitignore`

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
*.egg
*.egg-info/
dist/
build/
.Python

# Virtual environments
venv/
env/
ENV/
.venv

# Poetry
poetry.lock

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Data (raw, large files)
data/raw/
data/processed/
data/features/

# Models
models/*.pt
models/*.pkl
models/*.h5

# MLflow
mlflow_artifacts/
mlflow_backend/
.mlflow/

# DVC
.dvc/
*.dvc

# Jupyter
.ipynb_checkpoints/
notebooks/*.ipynb

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Terraform
terraform/.terraform/
terraform/*.tfstate*
terraform/*.tfvars.local
terraform/tfplan
```

### 2.9 Lock File (poetry.lock)
- Executar: `poetry lock` após setup
- **Commitar `poetry.lock` sempre no git** (reproduzibilidade)
- Nunca remover `poetry.lock` manually

### 2.10 Docker Compose Completo
**Arquivo**: `docker-compose.yml` (na raiz do projeto, orquestrando tudo)

```yaml
version: '3.9'

services:
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - mlflow_backend:/mlflow_backend
      - mlflow_artifacts:/mlflow_artifacts
    command: >
      mlflow server
      --host 0.0.0.0
      --port 5000
      --backend-store-uri sqlite:////mlflow_backend/mlflow.db
      --default-artifact-root /mlflow_artifacts
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/"]
      interval: 10s
      timeout: 5s
      retries: 3

  api:
    build:
      context: .
      dockerfile: api/Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app/api
      - ./shared:/app/shared
      - ./data:/app/data
      - ./models:/app/models
    environment:
      - ENVIRONMENT=local
      - MLFLOW_TRACKING_URI=http://mlflow:5000
      - DUCKDB_PATH=/app/data/rocket_tail.db
    depends_on:
      mlflow:
        condition: service_healthy
    command: >
      uvicorn rocket_tail_api.app:app
      --host 0.0.0.0
      --port 8000
      --reload

volumes:
  mlflow_backend:
  mlflow_artifacts:
```

**Usar**:
```bash
docker-compose up  # Rodar MLflow + API
```

## Relevant files
- `pyproject.toml` — Dependências Poetry com tudo
- `src/rocket_tail/config/settings.py` — Pydantic Settings
- `.env.example` — Template de variáveis
- `Dockerfile` — Multi-stage image
- `docker-compose.yml` — Local services (MLflow + API)
- `src/rocket_tail/ml/mlflow_utils.py` — MLflow client setup
- `scripts/setup_local.sh` — Automatiza tudo
- `scripts/validate_env.py` — Validação de ambiente
- `.gitignore` — Completo

## Verification
1. **Poetry lock criado**: `poetry lock --no-update` sem erro
2. **Fresh install funciona**: `rm -rf venv && poetry install && python scripts/validate_env.py`
3. **Docker build ok**: `docker build -t rocket-tail:dev . --no-cache`
4. **MLflow acessível**: `curl http://localhost:5000/` → 200
5. **Settings carregam**: `python -c "from rocket_tail.config import settings; print(settings.mlflow_tracking_uri)"`
6. **Pre-commit hooks ativo**: `pre-commit run -a` roda sem erro

## Decisions
- **Sem Anaconda**: Poetry é mais moderno e reproducível
- **Sem requirements.txt manual**: Poetry gera via `poetry export`
- **DVC backend S3**: Pronto para Etapa 3 (dataset tracking)
- **MLflow local (SQLite)**: Sem dependência de banco externo
- **Docker compose com volumes**: Para desenvolvimento local rápido

## Further Considerations
1. **AWS Credentials**: Precisam ser configuradas (`aws configure`) antes de DVC + S3
2. **Lock file como source of truth**: Usar `poetry lock --no-update` sempre (freeze versions)
3. **GitHub Secrets (futuro)**: Para CI/CD, adicionar AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

---

**Duração Estimada**: 3-4 horas (setup + testes de validação)  
**Próxima Etapa**: PLANO_ETAPA_3_PIPELINE_DADOS.md
