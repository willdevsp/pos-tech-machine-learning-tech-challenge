---
name: rocket-tail-recom-setup
description: >-
  Sets up the monorepo structure, clean code practices (Ruff, pre-commit),
  design patterns (Factory and Strategy), and basic CI/CD GitHub Actions workflows with path triggers.
---

# rocket-tail-recom-setup

Esta skill orienta a configuração inicial da estrutura do repositório monorepo do projeto RocketTail, aplicando boas práticas de clean code, padrões de projeto (Factory e Strategy), linters/formatters e workflows do GitHub Actions com gatilhos de caminho (path triggers).

## Ações e Responsabilidades

### 1. Estruturação do Monorepo
Organizar a raiz do projeto de forma a manter os componentes isolados e modulares:
* **`training/`**: Scripts de treinamento e pipelines DVC.
* **`api/`**: Servidor FastAPI para servir as recomendações.
* **`mlflow-server/`**: Configurações para o servidor MLflow local.
* **`shared/`**: Biblioteca compartilhada (`rocket-tail-shared`) importada por `training` e `api` para reutilização de modelos, configurações e utilitários.
* **`terraform/`**: Arquivos de Infraestrutura como Código (IaC) para deploy na AWS.

### 2. Padrões de Projeto (Design Patterns)
* **Factory Pattern (ModelFactory)**: Criar uma fábrica de modelos para instanciar diferentes variantes de redes neurais (ex: MLP, Collaborative, Content-Based, Hybrid) dinamicamente.
* **Strategy Pattern (PreprocessingStrategy)**: Estruturar as etapas de limpeza de dados em estratégias modulares e intercambiáveis (ex: preenchimento de nulos, normalização, codificação).

### 3. Qualidade de Código e Estilo
* Configurar o **Ruff** no arquivo `pyproject.toml` para gerenciar a lintagem e ordenação de imports.
* Adicionar regras de pré-commit (`.pre-commit-config.yaml`) para sanitizar espaços em branco, verificar finais de arquivo e rodar Ruff automaticamente a cada commit.
* Garantir type hints e docstrings no estilo do Google para todas as funções públicas.

### 4. Workflows CI/CD com Path Triggers
Criar workflows independentes no diretório `.github/workflows/` para evitar execuções desnecessárias:
* `train.yml` (disparado por alterações sob `training/` ou `shared/`)
* `api.yml` (disparado por alterações sob `api/` ou `shared/`)
* `shared.yml` (disparado por alterações sob `shared/`)
* `terraform.yml` (disparado por alterações sob `terraform/`)
