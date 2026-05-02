# Plano: Migração Telco Churn ML para AWS com Custo Mínimo

## TL;DR
Estratégia de AWS serverless-first com componentes gerenciados para minimizar custos operacionais:
- **MLflow + Artefatos**: RDS PostgreSQL + S3 em um container ECS Fargate (sempre ativo, ~$50-80/mês)
- **Predições**: Lambda + API Gateway (paga-se apenas por requisição, microsegundos ociosos)
- **Treinamento em batch**: AWS Batch + Spot Instances ou ECS Task agendada com EventBridge (~$10-20/mês)
- **Dados**: S3 com lifecycle policies para CSV de processado
- **Custo total estimado**: $100-165/mês (vs $500+ com instâncias EC2 dedicadas)

---

## Decisões Finais Confirmadas

- ✅ **Q1: RDS** → Aurora Serverless v2
- ✅ **Q2: Training** → AWS Batch (Spot instances)
- ✅ **Q3: CI/CD** → Terraform + GitHub Actions (pipeline completa: build, push, deploy)
- ✅ **MLflow Acesso** → Backend privado + CloudFront distribution

---

## 🏗️ Arquitetura: CloudFront + ALB Privado (Detalhada)

### **Fluxo de Tráfego**

```
┌─────────────────────────────────────────────────────────────────┐
│ Internet Público                                                │
└────────────────────────┬────────────────────────────────────────┘
                         │
                ┌────────▼────────┐
                │  Route53 (DNS)  │
                │mlflow.ejemplo.com
                └────────┬────────┘
                         │
        ┌────────────────▼────────────────┐
        │    CloudFront Distribution      │ (Cache + DDoS protection)
        │  - Cache Behavior: /api/* → ALB │
        │  - TTL: 300s (5 min)            │
        │  - Security: AWS WAF (opcional) │
        │  - HTTPS only (certificado ACM)│
        └────────────────┬────────────────┘
                         │
        ┌────────────────▼────────────────────┐
        │   AWS VPC (Privada)                 │
        │  ┌──────────────────────────────┐   │
        │  │  Application Load Balancer   │   │
        │  │  (Privado - sem IP público)  │   │
        │  │  - Listener: port 80 (HTTP)  │   │
        │  │  - Target: ECS service       │   │
        │  └────────────┬─────────────────┘   │
        │               │                     │
        │  ┌────────────▼──────────────────┐  │
        │  │  ECS Task (MLflow Container)  │  │
        │  │  - Port 5000 interno          │  │
        │  │  - Conecta ao RDS + S3        │  │
        │  └───────────────────────────────┘  │
        │                                      │
        └──────────────────────────────────────┘
```

### **Componentes Específicos do CloudFront**

1. **ACM Certificate** (Amazon Certificate Manager)
   - Domínio: `mlflow.exemplo.com` (wildcard opcional)
   - Validação: DNS ou Email
   - Auto-renewal: Automático (AWS gerencia)
   - Custo: **Grátis**

2. **CloudFront Distribution**
   - Origem: ALB privado (não IP público direto, via DNS)
   - Protocol: HTTPS → HTTP (CloudFront → ALB)
   - Cache Behavior:
     - Default: `/` → TTL 300s
     - Custom: `/api/*` → TTL 0 (sem cache, real-time)
   - Compression: Habilitado (gzip, brotli)
   - Custom Headers: Adicionar `X-Origin-Verify: token` (segurança)
   - Security:
     - SSL/TLS: TLS 1.2+
     - Origin Policy (restricts access ao ALB apenas de CloudFront)
   - Custo: $0.085/GB transferido + $0.01/10k requisições

3. **Route53**
   - Record: `mlflow.exemplo.com` → CloudFront distribution
   - Tipo: CNAME ou ALIAS (preferir ALIAS para apex domain)
   - Custo: **Grátis** (included em Route53)

4. **Security Group Restriction**
   - ALB: Inbound port 80/443 apenas de **CloudFront IP ranges**
   - CloudFront publica subnets/IPs, aplicar como origem permitida
   - Terraform: Usar data source `aws_cloudfront_distribution` para automatizar

### **Vantagens dessa Arquitetura**

✅ **Segurança**: ALB privado, não exposto na internet
✅ **Cache**: Reduz carga no MLflow, melhora latência
✅ **DDoS**: CloudFront absorve ataques
✅ **SSL/TLS**: Gerenciado automaticamente (ACM)
✅ **Custom Domain**: Profissional, não amazonaws.com
✅ **Escalabilidade**: CloudFront distribui globalmente (edge locations)

### **Considerações**

⚠️ **Domain registrado**: Precisa domínio próprio (ex: exemplo.com)
⚠️ **ACM Certificate**: Validação DNS requer acesso ao registrador
⚠️ **TTL cuidado**: Cache pode servir dados desatualizados
⚠️ **Custo adicional**: ~$20-50/mês (dependendo do tráfego)

---

## Estrutura Terraform (IaC)

```
infrastructure/
├── terraform/
│   ├── main.tf                    # Main config, providers
│   ├── variables.tf               # Input variables
│   ├── outputs.tf                 # Outputs (ALB, Lambda ARN, etc)
│   ├── terraform.tfvars           # Values (AWS region, tags)
│   │
│   ├── modules/
│   │   ├── s3/                    # S3 bucket, lifecycle, versioning
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── rds/                   # Aurora Serverless v2
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── ecr/                   # ECR repositories
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── ecs/                   # ECS cluster + task def + service (MLflow)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── lambda/                # Lambda functions (predict + batch trigger)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── api-gateway/           # API Gateway + authorization
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── batch/                 # AWS Batch (compute env, queue, job def)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── eventbridge/           # EventBridge scheduler (cron)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── iam/                   # IAM roles + policies (reutilizável)
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── vpc/                   # VPC, subnets, security groups
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   ├── cloudwatch/            # CloudWatch logs, dashboards, alarms
│   │   │   ├── main.tf
│   │   │   ├── variables.tf
│   │   │   └── outputs.tf
│   │   │
│   │   └── cloudfront/            # CloudFront distribution (MLflow UI)
│   │       ├── main.tf
│   │       ├── variables.tf
│   │       └── outputs.tf
│   │
│   └── environments/
│       ├── staging/
│       │   ├── terraform.tfvars    # Values específicos staging
│       │   └── backend.tf          # S3 backend (state)
│       │
│       └── production/
│           ├── terraform.tfvars    # Values específicos prod
│           └── backend.tf          # S3 backend (state)
│
└── github/
    └── workflows/
        ├── terraform-plan.yml       # PR: plan de infra
        ├── terraform-apply.yml      # Merge/Manual: apply infra
        ├── docker-build-push.yml    # Build imagens, push ECR
        ├── deploy-stack.yml         # Orquestra tudo: terraform + docker
        └── destroy-stack.yml        # Cleanup (staging)
```

---

## GitHub Actions Pipeline (CI/CD)

### **Workflow: `deploy-stack.yml`** (Trigger: push main, manual dispatch)

```yaml
name: Deploy Full Stack

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - 'Dockerfile*'
      - 'infrastructure/terraform/**'
      - '.github/workflows/deploy-stack.yml'
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        options: [staging, production]

jobs:
  # Job 1: Build Docker images
  build-images:
    runs-on: ubuntu-latest
    outputs:
      mlflow-image: ${{ steps.image.outputs.mlflow-image }}
      api-image: ${{ steps.image.outputs.api-image }}
      training-image: ${{ steps.image.outputs.training-image }}
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Login to Amazon ECR
        run: aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com
      
      - name: Build & Push MLflow image
        run: |
          docker build -f Dockerfile.mlflow -t $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/telco-churn-mlflow:$GITHUB_SHA .
          docker push $ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/telco-churn-mlflow:$GITHUB_SHA
      
      # Repetir para Dockerfile.api e Dockerfile.training
      
      - name: Output image URIs
        id: image
        run: |
          echo "mlflow-image=$ACCOUNT_ID.dkr.ecr.us-east-1.amazonaws.com/telco-churn-mlflow:$GITHUB_SHA" >> $GITHUB_OUTPUT
          # ... outras imagens

  # Job 2: Plan Terraform
  terraform-plan:
    runs-on: ubuntu-latest
    needs: build-images
    steps:
      - uses: actions/checkout@v4
      
      - uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: 1.7.0
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Terraform Init
        run: cd infrastructure/terraform && terraform init -backend-config=environments/$ENVIRONMENT/backend.tf
      
      - name: Terraform Plan
        run: |
          cd infrastructure/terraform
          terraform plan \
            -var-file=environments/$ENVIRONMENT/terraform.tfvars \
            -var="mlflow_image=${{ needs.build-images.outputs.mlflow-image }}" \
            -out=tfplan
      
      - name: Upload plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: infrastructure/terraform/tfplan

  # Job 3: Apply Terraform (apenas em main/manual)
  terraform-apply:
    runs-on: ubuntu-latest
    needs: [build-images, terraform-plan]
    if: github.ref == 'refs/heads/main' || github.event_name == 'workflow_dispatch'
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v2
      
      - name: Download plan
        uses: actions/download-artifact@v3
        with:
          name: tfplan
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Terraform Apply
        run: |
          cd infrastructure/terraform
          terraform init -backend-config=environments/$ENVIRONMENT/backend.tf
          terraform apply -auto-approve tfplan
      
      - name: Output infrastructure details
        run: |
          cd infrastructure/terraform
          terraform output -json > infrastructure-output.json
      
      - name: Save outputs as artifacts
        uses: actions/upload-artifact@v3
        with:
          name: infrastructure-output
          path: infrastructure/terraform/infrastructure-output.json
```

---

## Pré-requisitos (Checklist)

✅ **Antes de começar implementação:**

1. **Domain name** registrado (ex: sua-empresa.com)
2. **Route53 hosted zone** criado para domínio
3. **GitHub Secrets** configurados:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`
4. **S3 bucket** para Terraform state (backend remoto)
5. **IAM User** com permissões: ACM, CloudFront, Route53, EC2, VPC, ECS, RDS, S3, Lambda, Batch, EventBridge

---

## Fases Refinadas com CloudFront

### **Fase 0: Setup Pré-Infraestrutura** (~30min)
- [ ] Domínio + Route53 zone criados
- [ ] GitHub Secrets configurados
- [ ] S3 backend criado

### **Fase 1: VPC + Segurança** (~1h)
- [ ] VPC + Subnets (privadas + público)
- [ ] Security Groups (ALB, ECS, RDS, Lambda)
- [ ] NAT Gateway (para egress interno)

### **Fase 2: Banco de Dados** (~30min)
- [ ] Aurora Serverless v2 (RDS)
- [ ] Database + user criados

### **Fase 3: ECR + Docker Images** (~1h)
- [ ] ECR repositories criados
- [ ] Imagens built e pushed

### **Fase 4: ECS Fargate (MLflow)** (~1h)
- [ ] Task definition criada
- [ ] ALB privado (security group restritivo)
- [ ] ECS service rodando

### **Fase 5: CloudFront + Domain** (~1h)
- [ ] ACM certificate criado e validado
- [ ] CloudFront distribution criada
- [ ] Route53 records adicionados
- [ ] Testar acesso via `https://mlflow.sua-empresa.com`

### **Fase 6: Lambda + API Gateway** (~1h)
- [ ] Lambda layers criadas
- [ ] Funções Lambda (predict, batch-trigger) criadas
- [ ] API Gateway deployada

### **Fase 7: AWS Batch + Treinamento** (~1h)
- [ ] Batch compute environment + job queue
- [ ] Job definition criada
- [ ] EventBridge scheduler configurado

### **Fase 8: GitHub Actions Completo** (~1h)
- [ ] Workflows criados (terraform, docker, deploy)
- [ ] Testar pipeline end-to-end
- [ ] Documentar secrets necessários

### **Fase 9: Monitoramento + Testes** (~1h)
- [ ] CloudWatch dashboards
- [ ] Testes de latência (CloudFront cache)
- [ ] Testes de segurança (acesso privado)

**Total: ~9h de implementação**

---

## Estimativa de Custo Mensal

| Componente | Custo/Mês | Notas |
|-----------|-----------|-------|
| **ECS Fargate (MLflow)** | $50-70 | 0.25 vCPU + 512MB |
| **RDS Serverless Aurora** | $40-50 | 0.5-1 ACU, auto-scaling |
| **S3 (artefatos + CSV)** | $2-5 | ~1-10GB |
| **Lambda (predições)** | $1-10 | 1M requisições free, depois $0.0002/req |
| **API Gateway** | $3-5 | 1-2M requisições |
| **AWS Batch (training)** | $5-15 | Spot instances, 1 job/semana |
| **CloudWatch Logs** | $3-5 | Retenção 30 dias |
| **CloudFront** | $20-50 | $0.085/GB + $0.01/10k requisições |
| **Route53** | $0.50 | Grátis para hosted zone |
| **TOTAL** | **$124-210/mês** | Com CloudFront e redundância |

*(Sem NAT Gateway. Com NAT: +$30-45/mês)*

---

## Próximas Ações

Estamos prontos para começar a implementação das **Fases 0-2** (setup básico + infraestrutura principal).
