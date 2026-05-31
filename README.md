# RocketTail Recommendation System

Este repositório contém a solução do sistema de recomendação **RocketTail**, estruturado como um monorepo modular.

## Estrutura do Monorepo

O repositório é composto pelos seguintes diretórios:

- `shared/` — Pacote contendo código comum (modelos PyTorch, baseline, pré-processamento, utilitários).
- `training/` — Pipelines de treinamento de modelos baseados em DVC e MLflow.
- `api/` — API REST utilizando FastAPI pronta para deploy no AWS Lambda.
- `mlflow-server/` — Configuração para o servidor local do MLflow Tracking.
- `terraform/` — Declaração da infraestrutura como código (IaC) para deploy na AWS.

## Setup Local

### Pré-requisitos
- Python 3.10+ (ou Python 3.12 disponível no ambiente)
- Gerenciador de dependências e ambientes virtuais de preferência.

### Setup de Linting e Formatação
Este repositório utiliza o **Ruff** para linting e formatação rápida de código.
Você pode configurar o pre-commit hooks executando:
```bash
pip install pre-commit
pre-commit install
```

Para verificar o código manualmente:
```bash
ruff check .
```
