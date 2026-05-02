# Infrastructure as Code - Tech Challenge MLflow

Terraform + AWS para deploy de MLflow com arquitetura serverless-first.

## 📁 Estrutura

```
infrastructure/
├── terraform/              # Código Terraform principal
│   ├── main.tf             # Arquivo principal (orquestra módulos)
│   ├── modules/            # Módulos reutilizáveis
│   │   ├── vpc/            # VPC, Subnets, Security Groups
│   │   ├── rds/            # Aurora Serverless v2
│   │   ├── ecs/            # ECS Fargate (MLflow)
│   │   ├── ecr/            # ECR repositories
│   │   ├── s3/             # S3 buckets
│   │   ├── route53/        # Route53 subdomain
│   │   ├── cloudfront/     # CloudFront distribution
│   │   ├── lambda/         # Lambda (API predictions)
│   │   ├── batch/          # AWS Batch (training)
│   │   ├── cloudwatch/     # Monitoring
│   │   └── iam/            # IAM roles
│   ├── environments/       # Variáveis por ambiente
│   │   ├── staging/        # Staging tfvars + backend
│   │   └── production/     # Production tfvars + backend
│   └── outputs.tf          # Outputs globais
├── scripts/                # Scripts auxiliares
│   ├── fase0-bootstrap.sh  # Setup crítico (S3, DynamoDB, IAM)
│   └── iam-policy.json     # Policy para GitHub Actions
└── README.md               # Este arquivo
```

## 🚀 Como Começar

### Pré-requisitos (FASE 0)

```bash
# 1. Configurar AWS CLI
aws configure

# 2. Executar bootstrap
cd scripts
bash fase0-bootstrap.sh

# 3. Verificar outputs
echo "✅ Bootstrap concluído!"
```

### Inicializar Terraform (FASE 1)

```bash
cd terraform

# Staging
terraform init -backend-config=environments/staging/backend.tf
terraform plan -var-file=environments/staging/terraform.tfvars

# Production
terraform init -backend-config=environments/production/backend.tf
terraform plan -var-file=environments/production/terraform.tfvars
```

## 📋 Fases Implementação

| Fase | Descrição | Status | Tempo |
|------|-----------|--------|-------|
| 0 | Bootstrap (S3, DynamoDB, IAM) | ⏳ Próximo | 30 min |
| 1 | VPC + Segurança | 📋 TODO | 1h |
| 2 | RDS Aurora Serverless | 📋 TODO | 30 min |
| 3 | ECR Repositories | 📋 TODO | 30 min |
| 4 | ECS Fargate MLflow | 📋 TODO | 1h |
| 5 | Route53 + CloudFront | 📋 TODO | 1.5h |
| 6 | Lambda API | 📋 TODO | 1h |
| 7 | AWS Batch Training | 📋 TODO | 1h |
| 8 | EventBridge Scheduler | 📋 TODO | 30 min |
| 9 | Monitoring + Alarms | 📋 TODO | 30 min |

## 🔐 Segurança

- ✅ S3 terraform state com versionamento + encriptação
- ✅ DynamoDB table para locking (evita race conditions)
- ✅ IAM Role para GitHub Actions (OIDC, sem secrets em repo)
- ✅ RDS em subnet privada
- ✅ ALB privado (CloudFront → ALB)
- ✅ Security Groups restrictivos

## 💰 Custo Estimado

- **VPC + NAT**: $30-45/mês
- **RDS Aurora Serverless v2**: $20-35/mês
- **ECS Fargate MLflow**: $50-80/mês
- **S3**: $6-14/mês
- **CloudFront**: $0.085/GB + requisições
- **Lambda/Batch**: $10-20/mês
- **Misc (Route53, CloudWatch, ACM)**: $5-10/mês

**Total: $121-204/mês** (vs $500+ com EC2 dedicado)

## 📝 Variáveis Importantes

Criar arquivo `.tfvars.local` para valores sensíveis:

```hcl
# .tfvars.local (não commitar)
rds_password          = "sua-senha-super-segura"
mlflow_image_uri      = "123456.dkr.ecr.us-east-1.amazonaws.com/telco-churn-mlflow:latest"
acm_certificate_arn   = "arn:aws:acm:us-east-1:123456:certificate/..."
```

## 🔄 CI/CD

GitHub Actions workflows em `.github/workflows/`:
- `terraform-plan.yml` - Plan em PRs
- `terraform-apply.yml` - Apply em merges (main branch)
- `docker-build-push.yml` - Build images + push ECR
- `deploy-stack.yml` - Orquestra tudo

Todos usam OIDC (sem secrets em GitHub).

## 🛠️ Troubleshooting

### Backend S3 não encontrado
```bash
# Verificar bucket
aws s3 ls | grep telco-tf-state

# Verificar ACCOUNT_ID em backend.tf
aws sts get-caller-identity
```

### DynamoDB lock timeout
```bash
# Liberar lock stuck
aws dynamodb scan --table-name telco-tf-locks
aws dynamodb delete-item --table-name telco-tf-locks --key '{"LockID":{"S":"..."}}'
```

### RDS acesso negado
```bash
# Verificar security group
aws ec2 describe-security-groups --filters "Name=tag:Name,Values=rds-*"

# Verificar subnet
aws rds describe-db-instances --db-instance-identifier telco-churn
```

## 📚 Documentação

- `plano_ci_cd/PLANO_AWS_MLFLOW.md` - Arquitetura completa
- `plano_ci_cd/CHECKLIST_PRE_DEPLOYMENT.md` - Step-by-step detalhado
- `plano_ci_cd/RESUMO_EXECUTIVO.md` - Executive summary

## 💡 Dicas

- Use `terraform fmt` para formatar código
- Sempre faça `terraform plan` antes de `apply`
- Mantenha `.tfstate` em S3 (nunca em Git)
- Backup RDS automático ativo (35 dias retenção)
- CloudFront TTL=0 para `/api/*` (sempre fresh)
