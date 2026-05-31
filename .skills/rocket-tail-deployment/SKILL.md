---
name: rocket-tail-deployment
description: >-
  Deploys the recommendation model using FastAPI, containerization (Docker/docker-compose),
  and AWS infrastructure (Lambda, ECR, S3, IAM) provisioned via Terraform IaC.
---

# rocket-tail-deployment

Esta skill orienta a exposição do modelo de recomendação via API RESTful com FastAPI, sua containerização para Docker, testes locais via docker-compose e deploy de infraestrutura serverless e de armazenamento seguro na AWS usando Terraform.

## Ações e Responsabilidades

### 1. API FastAPI
* Criar a aplicação FastAPI expondo os endpoints principais:
  * `/health`: Diagnóstico de saúde e checagem de modelo carregado.
  * `/recommend`: Endpoint do tipo POST aceitando `user_id` e `top_k` e retornando a lista de itens.
  * `/info`: Metadados do modelo operacional.
* Garantir tratamento de erros e logs estruturados em todas as chamadas.

### 2. Containerização Docker e docker-compose
* Elaborar um `Dockerfile` multi-stage otimizado (builder que gera o `requirements.txt` a partir do Poetry + runtime limpo para produção).
* Criar o arquivo `docker-compose.yml` local que acopla o serviço da API e o MLflow server para validação integrada em ambiente local antes do deploy na nuvem.

### 3. AWS Lambda Handler
* Implementar o wrapper `lambda_handler` para o AWS Lambda (por exemplo, usando a biblioteca `aws-lambda-powertools`).
* Garantir que o modelo seja baixado e carregado a partir do bucket S3 durante a inicialização (startup/warm start) do Lambda para economizar overhead e contornar os limites de tamanho de código do Lambda.

### 4. Infraestrutura como Código (Terraform IaC)
Estruturar o Terraform de forma limpa em arquivos separados:
* `main.tf`: Configuração de provedores (AWS) e backend remoto persistente para o Terraform state (S3 + DynamoDB lock).
* `variables.tf` / `outputs.tf`: Parametrizar a infraestrutura e expor endpoints.
* `ecr.tf`: Repositório ECR de imagens Docker da API.
* `s3.tf`: Bucket para persistência dos artefatos de modelos treinados (`.pt`).
* `iam.tf`: Regras de políticas IAM (acesso do Lambda ao S3 e permissão para escrita de logs no CloudWatch).
* `lambda.tf`: Definição da função Lambda (baseada na imagem do ECR) e roteamento de requisições públicas através do API Gateway HTTP V2.

### 5. Documentação do Modelo (Model Card)
* Escrever o `MODEL_CARD.md` detalhando as métricas de performance do modelo comparadas com os baselines, a arquitetura, as restrições operacionais (ex: cold start) e possíveis vieses éticos.

### 6. Pipeline de Transição de Modelos (CI/CD GitHub Actions)
* Implementar o arquivo `.github/workflows/model_registry.yml` para transição do estágio do modelo no MLflow.
* Definir gatilhos manuais (`workflow_dispatch`) recebendo o ID da run (`run_id`) e nome do modelo.
* Associar os jobs de transição a **GitHub Environments** para exigir aprovação manual antes da promoção de estágio:
  - Aprovação 1 (Ambiente `staging-approval`) → Transição para `Staging`.
  - Aprovação 2 (Ambiente `production-approval`) → Transição para `Production` (aplicada em um segundo momento).

