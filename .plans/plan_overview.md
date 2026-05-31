# RocketTail Recommendation System - Visão Geral do Plano

## Decisões Definidas
- **Tipo de Recomendação**: Híbrido (Collaborative Filtering + Content-Based)
- **Arquitetura Local**: Python + PyTorch + DuckDB + FastAPI + Docker
- **Arquitetura AWS**: Lambda + S3 + ECR (serverless)
- **Timeline**: 1 pessoa, 2-3 semanas
- **Complexidade do Modelo**: MLP profundo (3-4 camadas com regularização)

## Estrutura dos 4 Planos

### Etapa 1: Clean Code + Estrutura Inicial (Monorepo)
**Arquivo**: `PLANO_ETAPA_1_CLEAN_CODE.md`
- Setup repositório GitHub
- Estrutura monorepo com pastas por objetivo:
  - `training/` — Scripts de treinamento + pipeline DVC
  - `api/` — FastAPI + testes unitários
  - `mlflow-server/` — MLflow tracking server
  - `shared/` — Código compartilhado (models, utils, config)
  - `terraform/` — IaC AWS
- Design patterns: Factory + Strategy
- Configuração de linting (Ruff, pre-commit)
- Type hints + docstrings
- GitHub Actions com path triggers
**Duração Estimada**: 4-5 horas | **Dependência**: Nenhuma

### Etapa 2: Ambiente + Dependências + Tracking
**Arquivo**: `PLANO_ETAPA_2_AMBIENTE.md`
- pyproject.toml com Poetry (deps prod/dev separadas)
- Pydantic Settings + .env
- Docker multi-stage base
- MLflow server setup (local)
- DVC init + remote S3
- Script de validação de ambiente
**Duração Estimada**: 3-4 horas | **Dependência**: Etapa 1

### Etapa 3: Pipeline de Dados + Preparação
**Arquivo**: `PLANO_ETAPA_3_PIPELINE_DADOS.md`
- Dataset download (Kaggle)
- DVC pipeline com 3+ stages: download → preprocess → feature_engineering
- EDA e análise de comportamento
- Split train/val/test
- Logging de artefatos no MLflow
- Testes unitários para cada stage
**Duração Estimada**: 5-6 horas | **Dependência**: Etapa 2

### Etapa 4: Modelo Neural + API + Deploy (com Terraform)
**Arquivo**: `PLANO_ETAPA_4_MODELO_DEPLOY.md`
- PyTorch MLP (3-4 camadas) com embedding
- Baselines: ScikitLearn para comparação
- Métricas: NDCG, Precision@K, Recall@K, MRR
- MLflow Model Registry (Staging → Production)
- FastAPI endpoint (/recommend)
- Docker prod image + docker-compose (local)
- Model Card + documentação
- **Terraform IaC**: Lambda + S3 + ECR + IAM roles + CloudWatch
- Deploy serverless via Terraform apply
**Duração Estimada**: 8-9 horas | **Dependência**: Etapa 3

## Abordagem: Sem Over-Engineering
- ✅ Não adicionar autoscaling complexo (SQS, etc)
- ✅ DuckDB em arquivo (não cluster)
- ✅ FastAPI mínimo (1 endpoint de recomendação + 1 health)
- ✅ Lambda como container (sem funções pequenas, trigger via API Gateway)
- ✅ Batch predictions em S3 (se necessário)
- ✅ Terraform minimal: 5-7 arquivos (.tf) para ECR + Lambda + S3 + IAM (com permissões para o Lambda consultar o MLflow Tracking Server e baixar artefatos do S3)
- ❌ Não usar: Kubernetes, SageMaker, Real-time Spark, Airflow completo, RDS (usar S3 gerenciado pelo MLflow para model artifacts)

## Skills a Criar
1. **rocket-tail-recom-setup** - Estrutura Clean Code + Design Patterns
2. **rocket-tail-dependencies** - Poetry + DVC + MLflow setup
3. **rocket-tail-pipeline** - DVC pipeline + EDA
4. **rocket-tail-pytorch-model** - PyTorch neural network + training
5. **rocket-tail-deployment** - FastAPI + Docker + Terraform + Lambda

## Arquitetura Monorepo + GitHub Actions + AWS

```
rocket-tail-recommendation/
├── training/                 # Componente: Treinamento
│   ├── pyproject.toml
│   ├── src/
│   ├── tests/
│   ├── dvc.yaml
│   └── .github/workflows/train.yml  # Trigger: alterações em training/**
├── api/                      # Componente: API REST
│   ├── pyproject.toml
│   ├── src/
│   ├── tests/
│   ├── Dockerfile
│   └── .github/workflows/api.yml    # Trigger: alterações em api/**
├── mlflow-server/            # Componente: MLflow Server
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── .github/workflows/mlflow.yml # Trigger: alterações em mlflow-server/**
├── shared/                   # Código compartilhado
│   ├── rocket_tail_shared/   # Package importado por training + api
│   ├── pyproject.toml
│   └── .github/workflows/shared.yml # Trigger: alterações em shared/**
├── terraform/                # IaC AWS
│   ├── *.tf
│   └── .github/workflows/terraform.yml # Trigger: alterações em terraform/**
├── .github/workflows/
│   ├── train.yml            # Testa + publica training image
│   ├── api.yml              # Testa + publica API image
│   ├── mlflow.yml           # Testa MLflow config
│   ├── shared.yml           # Testa shared package
│   └── terraform.yml        # Plan + apply Terraform
├── .gitignore
└── README.md
```

**GitHub Actions Path Triggers**:
- **train.yml**: `training/**` → pytest + DVC repro test
- **api.yml**: `api/**`, `shared/**` → pytest + build ECR image
- **terraform.yml**: `terraform/**` → terraform plan + apply (manual confirm)
- **shared.yml**: `shared/**` → pytest + publish to PyPI (futuro)

## Próximos Passos
1. ✅ Finalizar 4 planos em arquivos separados (Revisados e unificados no padrão Monorepo)
2. ✅ Criar 5 skills específicas
3. ✅ Usuário revisa e aprova os planos (Aprovado com direcionamento para Monorepo e MLflow Registry no Lambda)
4. Passar para implementação da Etapa 1
