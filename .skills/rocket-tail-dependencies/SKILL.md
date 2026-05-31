---
name: rocket-tail-dependencies
description: >-
  Configures environment and dependency management including Poetry (pyproject.toml),
  Pydantic Settings (.env integration), local MLflow tracking server setup, and DVC initialization.
---

# rocket-tail-dependencies

Esta skill gerencia o ambiente de desenvolvimento, controle de dependências, parametrização do sistema e configuração inicial das ferramentas de rastreamento de experimentos (MLflow) e dados (DVC).

## Ações e Responsabilidades

### 1. Gerenciamento de Dependências com Poetry
* Criar e manter o arquivo `pyproject.toml` dividindo as dependências de produção (ex: `torch`, `scikit-learn`, `fastapi`, `mlflow`, `duckdb`) e de desenvolvimento (ex: `pytest`, `ruff`, `pre-commit`, `dvc`).
* Gerar e commitar o arquivo `poetry.lock` para assegurar a reprodutibilidade exata em qualquer nova máquina.

### 2. Configurações por Variáveis de Ambiente
* Usar o template `.env.example` para documentar as chaves requeridas (caminhos, endpoints, chaves AWS).
* Implementar a classe `Settings` estendendo `BaseSettings` do `pydantic-settings` para expor parâmetros dinamicamente no Python, efetuando validação de tipos de dados e caminhos na inicialização.

### 3. MLflow Local
* Criar uma estrutura para persistir dados do MLflow usando SQLite local (`sqlite:///mlflow_backend/mlflow.db`) e um diretório específico para artefatos (`./mlflow_artifacts`).
* Configurar o arquivo `docker-compose.yml` para levantar a imagem oficial do MLflow e automatizar o servidor local na porta 5000.

### 4. Inicialização do DVC
* Inicializar o DVC com `dvc init --no-scm`.
* Configurar o armazenamento remoto (remote storage) com S3 da AWS (ou mock local se aplicável) definindo as configurações de perfil (`profile`) e verificação SSL no arquivo `.dvc/config`.

### 5. Script de Validação de Ambiente
* Disponibilizar o script `scripts/validate_env.py` para verificar a versão do Python (3.10+), presença do Poetry, integridade das pastas do projeto, existência do arquivo `.env` e instalação correta de todas as dependências críticas do PyTorch, FastAPI e MLflow.
