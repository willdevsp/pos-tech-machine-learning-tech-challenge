# ✅ CHECKLIST PRÉ-DEPLOYMENT AWS MLFLOW

**Data da Avaliação**: 2026-05-02  
**Status**: ✅ VIÁVEL PARA PRODUÇÃO  
**Custo Estimado**: $128-214/mês  
**Tempo Implementação**: 11-14 horas

---

## 🔴 FASE 0: SETUP CRÍTICO (30 minutos)

### Pré-requisitos Antes de Qualquer Ação

- [x] **AWS Account** criada e configurada
  - [x] Billing alerts configurados
  - [x] Root account com MFA
  
- [x] **GitHub OIDC Provider** já criado em AWS
  - [x] Federated identity configurada
  - [x] OIDC URL: https://token.actions.githubusercontent.com
  
- [x] **IAM Role** `github-action-tech-challenge` já criada
  - [x] OIDC trust relationship configurada
  - [x] Policy JSON aplicada (veja `PLANO_AWS_MLFLOW.md`)
  
- [ ] **Zona pai Route53** (asgardprint.com.br)
  - [ ] Já criada e operacional em AWS
  - [ ] Será delegada para subzone tech-challenge
  
- [ ] **GitHub Repository** criado
  - [ ] Código pushed para main branch
  - [ ] Workflows directory `.github/workflows/` criado

### Bootstrap: Executar Commands AWS CLI

```bash
# 1️⃣ Criar S3 bucket para Terraform state
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
BUCKET_NAME="telco-tf-state-${ACCOUNT_ID}"

aws s3api create-bucket \
  --bucket $BUCKET_NAME \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket $BUCKET_NAME \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket $BUCKET_NAME \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

aws s3api put-public-access-block \
  --bucket $BUCKET_NAME \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

# 2️⃣ Atach IAM Policy à role existente
aws iam put-role-policy \
  --role-name github-action-tech-challenge \
  --policy-name TechChallengeTerraformPolicy \
  --policy-document file://policy.json

echo "✅ Bootstrap Phase 0 concluído!"
echo "S3 Bucket: $BUCKET_NAME"
echo "IAM Role: github-action-tech-challenge (OIDC já configurado)"
echo "Próximo passo: Configurar GitHub Secrets com AWS_ROLE_ARN"
```

### ⚠️ Validação Pós-Bootstrap

- [ ] Verificar IAM Role: `aws iam get-role --role-name github-action-tech-challenge`
- [ ] Verificar S3 bucket: `aws s3 ls | grep telco-tf-state`
- [ ] Verificar versionamento: `aws s3api get-bucket-versioning --bucket telco-tf-state-{account-id}`

### ✅ GitHub Secrets Necessários

Com OIDC, apenas um secret é necessário:
- [ ] `AWS_ROLE_ARN` = `arn:aws:iam::204524745296:role/github-action-tech-challenge`
- [ ] `AWS_REGION` = us-east-1 (ou sua região)

---

## 🟦 FASE 1: VPC + SEGURANÇA (1 hora)

- [ ] VPC criada (CIDR 10.0.0.0/16)
- [ ] Subnets privadas criadas (2x az)
- [ ] Subnets públicas criadas (2x az) - se houver NAT
- [ ] Internet Gateway anexado
- [ ] NAT Gateway criado (OPCIONAL: pode economizar $30-45/mês sem)
- [ ] Security Groups:
  - [ ] ALB security group (port 80/443)
  - [ ] ECS security group (port 5000)
  - [ ] RDS security group (port 5432)
  - [ ] Lambda security group (egress only)

---

## 🟦 FASE 2: BANCO DE DADOS (30 minutos)

- [ ] Aurora Serverless v2 criado
- [ ] Database `telco_churn` criada
- [ ] User `mlflow` criado
- [ ] Conexão testada via Security Group

---

## 🟦 FASE 3: ECR + DOCKER (1 hora)

- [ ] ECR repositories criados:
  - [ ] `telco-churn-mlflow`
  - [ ] `telco-churn-api`
  - [ ] `telco-churn-training`
- [ ] Docker images built localmente
- [ ] Images pushed para ECR
- [ ] Image URIs anotadas para próximas fases

---

## 🟦 FASE 4: ECS FARGATE (MLFLOW) (1 hora)

- [ ] CloudWatch Log Group criado
- [ ] ECS Task Execution Role criado (IAM)
- [ ] ECS Task Role criado (S3 + RDS acesso)
- [ ] Task Definition criada
  - [ ] Image: `{account}.dkr.ecr.us-east-1.amazonaws.com/telco-churn-mlflow:latest`
  - [ ] Port: 5000
  - [ ] Environment vars: RDS_HOST, MLFLOW_BACKEND_STORE_URI, etc
- [ ] Application Load Balancer (privado) criado
  - [ ] Listener: port 80 (HTTP interno)
  - [ ] Target group: ECS service
  - [ ] Health check: `/`
- [ ] ECS Service criado
  - [ ] Min: 1, Max: 3 tasks
  - [ ] Rolling deployment
- [ ] Teste MLflow internamente

---

## 🟦 FASE 5: ROUTE53 SUBZONE + CLOUDFRONT + DOMAIN (1.5 horas)

### Route53 Subzone Delegation
- [ ] Route53 Hosted Zone criada
  - [ ] Zone name: `tech-challenge.asgardprint.com.br`
  - [ ] Type: Public hosted zone
- [ ] Nameservers copiados do terraform output:
  ```
  output "sub_zone_nameservers" {
    value = aws_route53_zone.tech_challenge_subzone.name_servers
  }
  ```
- [ ] NS records adicionados na zona pai (asgardprint.com.br)
  - [ ] Adicionar 4 NS records no console da zona pai
  - [ ] Aguardar propagação DNS (~5-15 minutos)
- [ ] Validação: `dig tech-challenge.asgardprint.com.br NS`

### ACM + CloudFront
- [ ] ACM Certificate criado/validado
  - [ ] Domain: `mlflow.tech-challenge.asgardprint.com.br`
  - [ ] Wildcard: `*.tech-challenge.asgardprint.com.br` (opcional)
  - [ ] Validação: DNS automática via Route53 (sem ação manual)
- [ ] CloudFront Distribution criada
  - [ ] Origin: ALB privado (custom origin)
  - [ ] Behavior 1: Default `/` → TTL 300s
  - [ ] Behavior 2: `/api/*` → TTL 0s (sem cache)
  - [ ] SSL/TLS: TLS 1.2+
  - [ ] HTTPS only

### Route53 Records na Subzone
- [ ] ALIAS record para MLflow
  - [ ] Name: `mlflow.tech-challenge.asgardprint.com.br`
  - [ ] Type: A (ALIAS)
  - [ ] Target: CloudFront distribution
- [ ] ALIAS record para API Gateway (opcional)
  - [ ] Name: `api.tech-challenge.asgardprint.com.br`
  - [ ] Type: A (ALIAS)
  - [ ] Target: API Gateway custom domain
- [ ] Teste acesso: `https://mlflow.tech-challenge.asgardprint.com.br`

---

---

## 🟦 FASE 6: LAMBDA + API GATEWAY (1 hora)

- [ ] Lambda IAM Role criado
  - [ ] Permissões: S3 leitura, RDS acesso, CloudWatch logs
- [ ] Lambda Layer criado (dependências Python)
  - [ ] Upload: `python/lib/python3.11/site-packages/` com numpy, pandas, scikit-learn, etc
- [ ] Lambda Functions criadas:
  - [ ] `telco-predict` (inference)
  - [ ] `telco-batch-trigger` (treinamento)
- [ ] API Gateway criado
  - [ ] REST API
  - [ ] Resource: `/predict`
  - [ ] Method: POST
  - [ ] Integration: Lambda `telco-predict`
  - [ ] Authorization: API Key ou Cognito (OPCIONAL)
- [ ] Deploy API Gateway
- [ ] Teste endpoint: `POST https://api.seu-dominio.com/predict`

---

## 🟦 FASE 7: AWS BATCH (1 hora)

- [ ] IAM Role para Batch Job criado
  - [ ] Permissões: S3, RDS, ECR, CloudWatch
- [ ] Batch Compute Environment criado
  - [ ] Type: MANAGED (recomendado)
  - [ ] Compute type: SPOT (70-90% savings)
  - [ ] Min vCPU: 0 (scale down)
  - [ ] Max vCPU: 4
- [ ] Batch Job Queue criado
  - [ ] Prioridade: 1
  - [ ] Compute Environment: associado acima
- [ ] Batch Job Definition criada
  - [ ] Image: `{account}.dkr.ecr.us-east-1.amazonaws.com/telco-churn-training:latest`
  - [ ] vCPU: 2
  - [ ] Memory: 4096 MB
  - [ ] Environment vars: RDS_HOST, MLFLOW_TRACKING_URI, S3_BUCKET
  - [ ] Retry strategy: 2 attempts
  - [ ] Timeout: 3600s (1h)
- [ ] EventBridge Scheduler criado
  - [ ] Schedule: `cron(0 2 ? * SUN *)` (domingos 2AM UTC)
  - [ ] Target: Batch Submit Job
  - [ ] Job Queue: telco-batch-queue
  - [ ] Job Definition: telco-churn-training

---

## 🟦 FASE 8: GITHUB ACTIONS (1 hora)

- [ ] Workflows criadas:
  - [ ] `.github/workflows/terraform-plan.yml` (PR trigger)
  - [ ] `.github/workflows/terraform-apply.yml` (merge trigger)
  - [ ] `.github/workflows/docker-build-push.yml` (ECR)
  - [ ] `.github/workflows/deploy-full-stack.yml` (orquestra tudo)
- [ ] Secrets validados no GitHub
- [ ] Test push para feature branch
  - [ ] Plan deve ser criado
  - [ ] Validar output
- [ ] Test merge para main
  - [ ] Docker images devem ser built
  - [ ] Terraform apply deve ser executado
  - [ ] Infrastructure deve ser deployada

---

## 🟦 FASE 9: MONITORAMENTO + TESTES (1 hora)

- [ ] CloudWatch Log Groups criados para:
  - [ ] `/aws/ecs/telco-mlflow`
  - [ ] `/aws/lambda/telco-predict`
  - [ ] `/aws/lambda/telco-batch-trigger`
  - [ ] `/aws/batch/telco-training`
- [ ] CloudWatch Dashboard criado
  - [ ] Métricas: CPU, Memory, Latency
  - [ ] Logs Insights queries pré-configuradas
- [ ] CloudWatch Alarms criados:
  - [ ] ECS task failures
  - [ ] Lambda errors
  - [ ] RDS connections
  - [ ] S3 bucket size
- [ ] Testes executados:
  - [ ] **Test 1**: Acessar MLflow UI → `https://mlflow.seu-dominio.com`
  - [ ] **Test 2**: Fazer predição → `curl -X POST https://api.seu-dominio.com/predict -H "Content-Type: application/json" -d '{"input": [...]}'`
  - [ ] **Test 3**: Verificar logs → CloudWatch Logs Insights
  - [ ] **Test 4**: Trigger manual de treinamento → AWS Batch console
  - [ ] **Test 5**: Validar S3 buckets criados → S3 console

---

## 📊 S3 BUCKETS: VALIDAÇÃO

Após todas as fases, validar que os 6 buckets foram criados:

- [ ] `telco-tf-state-{account-id}` - Terraform state (versionado)
- [ ] `telco-mlflow-artifacts-{region}` - Artefatos MLflow
- [ ] `telco-processed-data-{region}` - Dados processados
- [ ] `telco-training-datasets-{region}` - Dados de treino
- [ ] `telco-logs-{region}` - Logs
- [ ] `telco-rds-backups-{region}` - Backups RDS

**Validar para cada bucket**:
- [ ] Versionamento habilitado
- [ ] Encryption (AES256) habilitada
- [ ] Lifecycle policies configuradas
- [ ] Block Public Access habilitado
- [ ] Tagging correto

---

## 🎯 RESUMO FINAL

| Fase | Tempo | Status |
|------|-------|--------|
| **Fase 0** (Setup + OIDC + Bootstrap) | 1h | ⬜ Não iniciado |
| **Fase 1** (VPC) | 1h | ⬜ Não iniciado |
| **Fase 2** (RDS) | 30min | ⬜ Não iniciado |
| **Fase 3** (ECR) | 1h | ⬜ Não iniciado |
| **Fase 4** (ECS) | 1h | ⬜ Não iniciado |
| **Fase 5** (Route53 Subzone + CloudFront) | 1.5h | ⬜ Não iniciado |
| **Fase 6** (Lambda) | 1h | ⬜ Não iniciado |
| **Fase 7** (Batch) | 1h | ⬜ Não iniciado |
| **Fase 8** (GitHub Actions) | 1h | ⬜ Não iniciado |
| **Fase 9** (Monitoramento) | 1h | ⬜ Não iniciado |
| **TOTAL** | **~10.5-11h** | ⏳ Pendente |

---

## 📞 SUPORTE

Se encontrar problemas:

1. **OIDC não funciona**: Validar `aws iam get-open-id-connect-provider-thumbprint` e trust relationship
2. **DNS não propaga**: Usar `dig tech-challenge.asgardprint.com.br NS` e validar NS records
3. **ACM validation falha**: Verificar Route53 records criados pelo terraform
4. **Security groups**: Logs no VPC Flow Logs
5. **IAM permissões**: CloudTrail logs
6. **RDS conectividade**: `aws rds describe-db-instances`
7. **ECS tasks**: `aws ecs describe-services`

---

**⚠️ IMPORTANTE**: Guarde os nomes dos buckets S3 e IDs dos recursos criados. Você vai precisar deles para Terraform variables!
