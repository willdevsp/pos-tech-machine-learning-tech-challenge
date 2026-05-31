# PLANO ETAPA 4: Modelo Neural + API + Deploy (com Terraform)

## TL;DR
Treinar modelo PyTorch híbrido (Collaborative + Content-Based), expor via FastAPI, containerizar, e fazer deploy serverless na AWS (Lambda + ECR) usando Terraform como Infrastructure as Code. Rodar local com docker-compose, escalar com `terraform apply`.

## Steps

### 4.1 PyTorch Neural Network Model
**Arquivo**: `shared/src/rocket_tail_shared/models/neural_models.py`

#### Camadas (MLP Profundo - 3-4 camadas)
```
Entrada: user_embedding + item_embedding + features (categoria, preço, etc)
  ↓
Dense(256) + ReLU + Dropout(0.3)
  ↓
Dense(128) + ReLU + Dropout(0.2)
  ↓
Dense(64) + ReLU + Dropout(0.1)
  ↓
Dense(1) + Sigmoid
  ↓
Saída: Probabilidade de interação (0-1)
```

**Componentes**:
- Classe `EmbeddingLayer`: user embedding (dim=32), item embedding (dim=32)
- Classe `ContentBasedNN`: rede apenas com item features (categoria, preço)
- Classe `CollaborativeNN`: rede com user/item embeddings
- Classe `HybridNN`: concatena ambas + MLP final (a usar)

**Regularização**:
- L2 weight decay: 1e-5
- Dropout nas 3 camadas ocultas
- Batch normalization (opcional, sem over-eng)
- Early stopping (monitor val_loss)

### 4.2 Treinamento com PyTorch puro (ou PyTorch Lightning)
**Arquivo**: `training/src/rocket_tail_training/train.py`

**Fluxo**:
1. Carregar features do DVC (output da Etapa 3)
2. Criar DataLoader (batch_size=32)
3. Instanciar HybridNN com config
4. Loop de epochs (50-100):
   - Forward pass
   - Compute loss (BinaryCrossentropy)
   - Backward + optimizer step
   - Log métricas no MLflow
5. Validação a cada epoch
6. Early stopping se val_loss não melhora (10 epochs)
7. Salvar melhor modelo em `models/best_model.pt`

**Função**: `train_model(config_path, output_dir)`
- Lê config YAML
- Retorna: trained model, history, best_metrics

### 4.3 Baselines para Comparação
**Arquivo**: `shared/src/rocket_tail_shared/ml/baselines.py`

#### Baseline 1: Item-Item Similarity (Cosine)
- Calcular matriz de similaridade entre itens (category + preço + popularity)
- Para um user novo, recomendar itens similares aos que viu

#### Baseline 2: User-User Similarity (KNN)
- Usar ScikitLearn KNeighborsRegressor
- Features: histórico de compra do user
- Recomendar top-N itens dos users vizinhos

#### Baseline 3: Popularity Ranking
- Simples: itens mais vistos / comprados

**Função**: `evaluate_baselines(features_df, test_df) → dict`

### 4.4 Métricas de Avaliação
**Arquivo**: `shared/src/rocket_tail_shared/utils/metrics.py`

Implementar:
- **NDCG@K** (Normalized Discounted Cumulative Gain)
- **Precision@K** (% de recs relevantes)
- **Recall@K** (% de itens relevantes encontrados)
- **MRR** (Mean Reciprocal Rank)
- **Coverage** (% de itens recomendados vs total)
- **Diversity** (variância de categorias recomendadas)

**Função**: `compute_metrics(y_true, y_pred_ranked, k=10) → dict`

### 4.5 MLflow Model Registry
**Arquivo**: `training/src/rocket_tail_training/register_model.py`

**Fluxo Automatizado/Manual**:
1. Comparar metrics: HybridNN vs Baselines. Se melhor, registrar o modelo no Registry.
2. A transição de estágio do modelo registrado será controlada via pipeline do GitHub Actions usando **GitHub Environments** para aprovações manuais:
   - **Staging Approval**: Gatilho para transicionar para o stage `Staging`. Requer aprovação manual de um revisor no GitHub.
   - **Production Approval**: Gatilho secundário para transicionar o modelo mais recente de `Staging` para `Production`. Requer aprovação manual adicional.

**Função**: `register_and_transition(model_name, stage)`
- Função no pipeline Python que efetua a chamada à API do MLflow Client (`client.transition_model_version_stage`) passando a versão e o estágio alvo.


### 4.6 FastAPI REST API (Componente api/)
**Arquivo**: `api/src/rocket_tail_api/app.py`

```python
import os
import mlflow
from fastapi import FastAPI
from rocket_tail_shared.config.settings import settings

app = FastAPI(title="RocketTail REST API", version="1.0")

model = None

@app.on_event("startup")
async def load_model():
    global model
    mlflow.set_tracking_uri(settings.mlflow_tracking_uri)
    model_name = os.getenv("MLFLOW_MODEL_NAME", "rocket-tail-hybrid")
    model_uri = f"models:/{model_name}/Production"
    model = mlflow.pytorch.load_model(model_uri)

@app.get("/health")
def health():
    return {"status": "ok", "model_loaded": model is not None}

@app.post("/recommend")
def recommend(user_id: int, top_k: int = 10):
    """
    Retorna top-K produtos recomendados para um usuário.
    """
    if model is None:
        return {"error": "Model not loaded"}
    
    recommendations = model.predict(user_id, top_k)
    return {
        "user_id": user_id,
        "recommendations": recommendations,
        "count": len(recommendations)
    }

@app.get("/info")
def info():
    return {
        "model": "HybridNN",
        "version": "1.0",
        "last_updated": "2026-05-31"
    }
```

**Funcionalidades**:
- Load model na startup
- Health check (`/health`)
- Endpoint `/recommend` (POST, user_id, top_k)
- Endpoint `/info` (modelo metadata)
- Logging de requisições
- Error handling

### 4.7 Docker para API REST
**Arquivo**: `api/Dockerfile`

Refira-se ao arquivo `api/Dockerfile` configurado na Etapa 2. Para rodar em produção localmente ou construir a imagem para o ECR, o build é executado a partir do contexto da raiz do monorepo.

**Para AWS Lambda**:
- Imagem base: `public.ecr.aws/lambda/python:3.10`
- Entrypoint: `src.rocket_tail.api.handler` (wrapper para Lambda)

### 4.8 Docker Compose (Local Development)
**Arquivo**: `docker-compose.yml`

```yaml
version: '3.9'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
    environment:
      - ENVIRONMENT=local
      - LOG_LEVEL=INFO
  
  mlflow:
    image: ghcr.io/mlflow/mlflow:latest
    ports:
      - "5000:5000"
    volumes:
      - mlflow_data:/mlflow
    command: mlflow server --host 0.0.0.0 --backend-store-uri file:///mlflow
    
volumes:
  mlflow_data:
```

**Como usar**:
- `docker-compose up` → rodar localmente
- Acessar: http://localhost:8000/docs (Swagger)

### 4.9 Terraform IaC para AWS (Minimal)
**Estrutura**: `terraform/` com 6 arquivos

#### 4.9.1 `terraform/main.tf`
```terraform
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  backend "s3" {
    bucket         = "rocket-tail-tf-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "rocket-tail-locks"
  }
}

provider "aws" {
  region = var.aws_region
}
```

#### 4.9.2 `terraform/variables.tf`
```terraform
variable "aws_region" {
  default = "us-east-1"
}

variable "project_name" {
  default = "rocket-tail"
}

variable "environment" {
  default = "prod"
}

variable "lambda_memory_mb" {
  default = 512
}

variable "lambda_timeout_sec" {
  default = 60
}
```

#### 4.9.3 `terraform/ecr.tf`
```terraform
resource "aws_ecr_repository" "rocket_tail" {
  name                 = "${var.project_name}-api"
  image_tag_mutability = "MUTABLE"
  
  image_scanning_configuration {
    scan_on_push = true
  }
}

output "ecr_repository_url" {
  value = aws_ecr_repository.rocket_tail.repository_url
}
```

#### 4.9.4 `terraform/s3.tf`
```terraform
resource "aws_s3_bucket" "models" {
  bucket = "${var.project_name}-models-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_bucket_versioning" "models" {
  bucket = aws_s3_bucket.models.id
  versioning_configuration {
    status = "Enabled"
  }
}

output "s3_models_bucket" {
  value = aws_s3_bucket.models.id
}
```

#### 4.9.5 `terraform/iam.tf`
```terraform
resource "aws_iam_role" "lambda_role" {
  name = "${var.project_name}-lambda-role"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy" "lambda_s3" {
  name = "${var.project_name}-lambda-s3"
  role = aws_iam_role.lambda_role.id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.models.arn,
          "${aws_s3_bucket.models.arn}/*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

output "lambda_role_arn" {
  value = aws_iam_role.lambda_role.arn
}
```

#### 4.9.6 `terraform/lambda.tf`
```terraform
resource "aws_lambda_function" "rocket_tail" {
  function_name = "${var.project_name}-recommender"
  role          = aws_iam_role.lambda_role.arn
  
  package_type = "Image"
  image_uri    = "${aws_ecr_repository.rocket_tail.repository_url}:latest"
  
  memory_size = var.lambda_memory_mb
  timeout     = var.lambda_timeout_sec
  
  environment {
    variables = {
      ENVIRONMENT         = var.environment
      MLFLOW_TRACKING_URI = var.mlflow_tracking_uri
      MLFLOW_MODEL_NAME   = var.mlflow_model_name
    }
  }
}

resource "aws_apigatewayv2_api" "rocket_tail" {
  name          = "${var.project_name}-api"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "lambda" {
  api_id             = aws_apigatewayv2_api.rocket_tail.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  target             = "arn:aws:apigatewayv2:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.rocket_tail.arn}/invocations"
}

resource "aws_apigatewayv2_route" "recommend" {
  api_id    = aws_apigatewayv2_api.rocket_tail.id
  route_key = "POST /recommend"
  target    = "integrations/${aws_apigatewayv2_integration.lambda.id}"
}

resource "aws_apigatewayv2_stage" "prod" {
  api_id      = aws_apigatewayv2_api.rocket_tail.id
  name        = "prod"
  auto_deploy = true
}

output "api_endpoint" {
  value = aws_apigatewayv2_stage.prod.invoke_url
}
```

#### 4.9.7 `terraform/outputs.tf`
```terraform
output "ecr_repository_url" {
  description = "URL do repositório ECR"
  value       = aws_ecr_repository.rocket_tail.repository_url
}

output "s3_models_bucket" {
  description = "S3 bucket para modelos"
  value       = aws_s3_bucket.models.id
}

output "lambda_role_arn" {
  description = "ARN da role do Lambda"
  value       = aws_iam_role.lambda_role.arn
}

output "api_endpoint" {
  description = "Endpoint da API no API Gateway"
  value       = aws_apigatewayv2_stage.prod.invoke_url
}
```

### 4.10 Lambda Handler (para AWS)
**Arquivo**: `api/src/rocket_tail_api/handler.py`

```python
import json
import os
import mlflow
from aws_lambda_powertools import Logger

logger = Logger()
model = None

def load_model():
    global model
    model_name = os.getenv("MLFLOW_MODEL_NAME", "rocket-tail-hybrid")
    tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
    
    # Define tracking server URI
    mlflow.set_tracking_uri(tracking_uri)
    
    # Carrega o modelo do estágio 'Production' diretamente pelo MLflow Registry
    logger.info(f"Loading model '{model_name}' (Production stage) from MLflow...")
    model_uri = f"models:/{model_name}/Production"
    model = mlflow.pytorch.load_model(model_uri)
    logger.info("Model loaded successfully")

def lambda_handler(event, context):
    if model is None:
        load_model()
    
    try:
        body = event.get("body", "{}")
        if isinstance(body, str):
            body = json.loads(body)
            
        user_id = body.get("user_id")
        top_k = body.get("top_k", 10)
        
        # Realiza recomendação
        recommendations = model.predict(user_id, top_k)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "user_id": user_id,
                "recommendations": recommendations,
                "count": len(recommendations)
            })
        }
    except Exception as e:
        logger.exception("Failed to run recommendations")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
```

### 4.11 Scripts de Deployment
**Arquivo**: `scripts/deploy.sh`

```bash
#!/bin/bash
set -e

REGION="us-east-1"
PROJECT="rocket-tail"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${REGION}.amazonaws.com/${PROJECT}-api"

# 1. Build image
echo "Building Docker image..."
docker build -t ${PROJECT}:latest .

# 2. Tag para ECR
echo "Tagging image for ECR..."
docker tag ${PROJECT}:latest ${ECR_URI}:latest

# 3. Push para ECR
echo "Pushing to ECR..."
aws ecr get-login-password --region ${REGION} | docker login --username AWS --password-stdin ${ECR_URI}
docker push ${ECR_URI}:latest

# 4. Deploy com Terraform
echo "Deploying with Terraform..."
cd terraform
terraform init
terraform plan -out=tfplan
terraform apply tfplan
echo "Deployment complete!"
echo "API Endpoint:"
terraform output api_endpoint
```

### 4.12 Model Card
**Arquivo**: `MODEL_CARD.md`

Seções:
1. **Model Overview**: Nome, versão, tipo (Hybrid)
2. **Performance**: Tabela comparando HybridNN vs Baselines
3. **Intended Use**: Para que serve, não serve
4. **Training Data**: Dataset RetailRocket, períodos
5. **Limitations**: Coldfstart users, itens novos, viés de categoria
6. **Ethical Considerations**: Possível discriminação por categoria?
7. **Version History**: v1.0 inicial, métricas, data

### 4.13 Testes Unitários + Integração
**Arquivos**: `shared/tests/test_models.py`, `api/tests/test_api.py`

```python
# shared/tests/test_models.py
from rocket_tail_shared.models.neural_models import HybridNN
import torch

def test_hybrid_model_output_shape():
    model = HybridNN(embedding_dim=32)
    output = model(user_ids=torch.tensor([1, 2]), item_ids=torch.tensor([10, 20]))
    assert output.shape == (2, 1)

# api/tests/test_api.py
from fastapi.testclient import TestClient
from rocket_tail_api.app import app

def test_api_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200

def test_api_recommend():
    client = TestClient(app)
    response = client.post("/recommend", json={"user_id": 1, "top_k": 5})
    assert response.status_code == 200
    assert len(response.json()["recommendations"]) <= 5
```

### 4.14 CI/CD GitHub Actions (Opcional, não essencial)
**Arquivo**: `.github/workflows/deploy.yml`

```yaml
name: Deploy to AWS
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: pytest tests/ -v

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy
        env:
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
        run: bash scripts/deploy.sh
```

**Arquivo**: `.github/workflows/model_registry.yml`
*(Gerencia a transição de modelos do MLflow com aprovações manuais)*

```yaml
name: MLflow Model Transition

on:
  workflow_dispatch:
    inputs:
      run_id:
        description: 'MLflow Run ID do modelo para registrar'
        required: true
        type: string
      model_name:
        description: 'Nome do modelo registrado'
        required: true
        default: 'rocket-tail-hybrid'
        type: string

jobs:
  transition-to-staging:
    name: Registrar e Transicionar para Staging
    runs-on: ubuntu-latest
    environment: staging-approval # Exige aprovação no GitHub
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install MLflow
        run: pip install mlflow
      - name: Register & Transition
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python -c "
          import mlflow
          from mlflow.tracking import MlflowClient
          client = MlflowClient()
          
          # Registrar modelo
          model_version = mlflow.register_model(
              model_uri=f'runs:/${{ github.event.inputs.run_id }}/model',
              name='${{ github.event.inputs.model_name }}'
          )
          
          # Transicionar para Staging
          client.transition_model_version_stage(
              name='${{ github.event.inputs.model_name }}',
              version=model_version.version,
              stage='Staging',
              archive_existing_versions=True
          )
          print(f'Modelo registrado e transicionado para Staging. Versão: {model_version.version}')
          "

  transition-to-production:
    name: Transicionar de Staging para Production
    needs: transition-to-staging
    runs-on: ubuntu-latest
    environment: production-approval # Exige uma segunda aprovação no GitHub
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install MLflow
        run: pip install mlflow
      - name: Transition to Production
        env:
          MLFLOW_TRACKING_URI: ${{ secrets.MLFLOW_TRACKING_URI }}
        run: |
          python -c "
          from mlflow.tracking import MlflowClient
          client = MlflowClient()
          
          # Buscar a versão mais recente em Staging
          latest_staging = client.get_latest_versions('${{ github.event.inputs.model_name }}', stages=['Staging'])
          if not latest_staging:
              raise ValueError('Nenhuma versão em Staging encontrada!')
          latest_version = latest_staging[0].version
          
          # Transicionar para Production
          client.transition_model_version_stage(
              name='${{ github.event.inputs.model_name }}',
              version=latest_version,
              stage='Production',
              archive_existing_versions=True
          )
          print(f'Modelo versão {latest_version} transicionado para Production.')
          "
```


## Relevant files
- `shared/src/rocket_tail_shared/models/neural_models.py` — HybridNN, EmbeddingLayer, baselines
- `training/src/rocket_tail_training/train.py` — Treinamento e registro no MLflow
- `api/src/rocket_tail_api/app.py` — FastAPI REST API
- `api/src/rocket_tail_api/handler.py` — Lambda wrapper que carrega via MLflow Registry
- `api/Dockerfile` — Multi-stage docker image
- `docker-compose.yml` — Local orchestrator
- `terraform/` — IaC com configurações atualizadas de variáveis
- `shared/tests/test_models.py`, `api/tests/test_api.py` — Testes unitários separados

## Verification
1. **Local**: `docker-compose up` → API responde em http://localhost:8000/docs
2. **Endpoints testados**: `/health`, `/recommend`, `/info` retornam 200
3. **Terraform plan sem erros**: `terraform plan` no diretório terraform/
4. **Imagem ECR criada**: `aws ecr describe-repositories --region us-east-1`
5. **Lambda + API Gateway ativo**: `curl https://<api_endpoint>/health` retorna 200
6. **Model performance logged**: MLflow shows comparison table (HybridNN vs 3 baselines)
7. **MODEL_CARD atualizado**: Documentação completa com métricas reais

## Decisions
- **Terraform backend**: S3 + DynamoDB (requer setup inicial: `scripts/setup_tf_backend.sh`)
- **Sem autoscaling**: Lambda tem concorrência ilimitada por padrão
- **Lambda timeout**: 60 segundos (ajustável via `lambda_timeout_sec`)
- **Sem caching**: API Gateway cache desativado (simplicidade)
- **Sem monitoramento avançado**: CloudWatch basic logs apenas
- **Sem VPC**: Função Lambda pública (para MVP)

## Further Considerations
1. **Terraform State Lock**: Setup S3 versioning + DynamoDB na primeira execução
   - Criar: `aws s3api create-bucket --bucket rocket-tail-tf-state-<account-id>`
   - Comando em `scripts/setup_tf_backend.sh`
2. **Secrets Management**: AWS Secrets Manager para credenciais (futuro)
3. **Modelo Artifacts**: Registrado no MLflow Model Registry, Lambda baixa o modelo usando a API do MLflow na inicialização (cold start +1-2s) aproveitando as credenciais do IAM para ler o bucket de artefatos do MLflow.

---

**Duração Estimada**: 8-9 horas (5h modelo + testes, 2h FastAPI + Docker, 1.5h Terraform)  
**Critério de Conclusão**: `terraform apply` bem-sucedido + API responde + Model Card escrito
