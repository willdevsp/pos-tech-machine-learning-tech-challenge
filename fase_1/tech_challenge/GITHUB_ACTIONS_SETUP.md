# GitHub Actions Setup - Complete Automation

## 📋 Workflows Criados

Todos os workflows estão em `.github/workflows/`:

| Workflow | Arquivo | Trigger | Ação |
|----------|---------|---------|------|
| FASE 0 Bootstrap | `fase0-bootstrap.yml` | Manual ou push | Cria S3, DynamoDB, aplica IAM Policy |
| Terraform Plan | `terraform-plan.yml` | Pull Request | Faz `terraform plan` |
| Terraform Apply | `terraform-apply.yml` | Push main | Faz `terraform apply` |
| Docker Build | `docker-build-push.yml` | Push main | Build e push images ECR |
| Full Stack | `full-stack-deploy.yml` | Push main | Orquestra tudo: Docker + Terraform |

---

## 🚀 PRÓXIMAS AÇÕES (Essencial)

### 1️⃣ Configure GitHub Secrets (Obrigatório)

**Ir em**: GitHub Repo → Settings → Secrets and Variables → Actions

**Criar secrets:**

| Nome | Valor | Exemplo |
|------|-------|---------|
| `RDS_PASSWORD` | Senha forte para RDS master | `SuperSenha@123#` |
| `ACM_CERTIFICATE_ARN` | ARN do certificado ACM (opcional por agora) | `arn:aws:acm:us-east-1:204524745296:certificate/...` |
| `MLFLOW_IMAGE_URI` | URI da imagem (será preenchido automaticamente) | (auto-gerado) |

**⚠️ IMPORTANTE**: Sem `RDS_PASSWORD`, terraform plan vai falhar!

### 2️⃣ Verificar Pré-requisitos

```bash
# ✅ GitHub OIDC Provider já criado em AWS
# ✅ IAM Role 'github-action-tech-challenge' já criada
# ✅ Trust relationship configurado para OIDC
```

### 3️⃣ Fazer Push do Código

```bash
# No seu terminal
git add .
git commit -m "feat: Add GitHub Actions workflows for automated deployment

- FASE 0: Bootstrap (S3, DynamoDB, IAM)
- Terraform Plan/Apply workflows
- Docker Build & Push to ECR
- Full Stack orchestration

All infrastructure setup now automated via GitHub Actions."

git push origin main
```

---

## 📊 Sequência de Execução Automática

Quando você fazer `git push origin main`:

### **Primeira execução (FASE 0 - Uma única vez)**

1. ⏳ GitHub Actions dispara workflows
2. 📦 `fase0-bootstrap.yml` executa (pode levar 2-3 min)
   - Cria S3 bucket: `telco-tf-state-204524745296`
   - Cria DynamoDB table: `telco-tf-locks`
   - Aplica IAM Policy ao role
3. ✅ Workflow completa
4. 🔒 Resources criados no AWS

### **Execuções subsequentes (FASE 1+)**

1. ⏳ `full-stack-deploy.yml` dispara automaticamente
2. 🐳 Build Docker images (MLflow, API, Training)
3. 📤 Push images para ECR
4. 📋 Terraform plan
5. 🚀 Terraform apply
6. ✅ Infrastructure atualizada

---

## 🎯 Disparar Workflows Manualmente

### FASE 0 Bootstrap (Se precisar re-rodar)

```
GitHub Repo → Actions → FASE 0 Bootstrap
→ "Run workflow" → Select environment → "Run workflow"
```

### Terraform Plan Only

```
GitHub Repo → Actions → Terraform Plan
→ "Run workflow" → Select environment → "Run workflow"
```

### Terraform Apply Only

```
GitHub Repo → Actions → Terraform Apply
→ "Run workflow" → Select environment + auto_approve=true → "Run workflow"
```

### Full Stack Deploy

```
GitHub Repo → Actions → Full Stack Deploy
→ "Run workflow" → Select environment → "Run workflow"
```

---

## 📝 Environment Configuration

Dois ambientes estão configurados:

### **Staging** (Padrão)
- VPC CIDR: `10.1.0.0/16`
- NAT Gateway: ❌ Desabilitado (economizar)
- Uso: Desenvolvimento e testes

### **Production**
- VPC CIDR: `10.0.0.0/16`
- NAT Gateway: ✅ Habilitado
- Uso: Deploy final

Para mudar entre ambientes, use o workflow dispatch.

---

## 🔍 Monitorar Execução

### Ver logs do workflow

1. GitHub Repo → Actions
2. Clicar no workflow em execução
3. Clicar no job (ex: `bootstrap`)
4. Ver output em tempo real

### Verificar recursos criados no AWS

```bash
# Depois que workflow termina, verificar:

# S3 bucket
aws s3 ls | grep telco-tf-state

# DynamoDB table
aws dynamodb list-tables | grep telco-tf-locks

# ECR repositories (após Docker build)
aws ecr describe-repositories

# Terraform state
aws s3 ls s3://telco-tf-state-204524745296/
```

---

## ⚙️ Variáveis Terraform por Ambiente

Já pré-configuradas em:
- `infrastructure/terraform/environments/staging/terraform.tfvars`
- `infrastructure/terraform/environments/production/terraform.tfvars`

Modificar conforme necessário antes de fazer push.

---

## 🔐 Segurança

- ✅ OIDC usado (sem secrets armazenados em GitHub)
- ✅ Tokens de curta vida (1 hora)
- ✅ Auditoria automática em CloudTrail
- ✅ Role com permissões mínimas necessárias
- ✅ Estado Terraform encriptado em S3

---

## 🚨 Troubleshooting

### ❌ Erro: "Role not found"
```
Status: Workflow falha antes de fazer nada
Causa: IAM Role 'github-action-tech-challenge' não existe
Solução: Criar em AWS console com OIDC trust relationship
```

### ❌ Erro: "RDS_PASSWORD not set"
```
Status: Terraform plan falha
Causa: Secret RDS_PASSWORD não configurado no GitHub
Solução: Adicionar em GitHub Settings → Secrets
```

### ❌ Erro: "Permission denied" no S3
```
Status: Terraform init falha
Causa: IAM Policy incompleta
Solução: Verificar que policy foi aplicada ao role
```

### ❌ Erro: "Bucket already exists"
```
Status: Bootstrap falha
Causa: Bucket já foi criado em execução anterior
Solução: Esperado - script pula automaticamente
```

---

## 📚 Próximas Fases

Após bootstrap (FASE 0) completar com sucesso:

- [ ] FASE 1: VPC + Security Groups (automático via Terraform)
- [ ] FASE 2: RDS Aurora Serverless (automático via Terraform)
- [ ] FASE 3: ECR Repositories (automático via Terraform + Docker)
- [ ] FASE 4: ECS Fargate MLflow (automático via Terraform)
- [ ] FASE 5: Route53 + CloudFront (automático via Terraform)
- [ ] FASE 6-9: Lambda, Batch, Monitoring (TODO - implementar módulos)

Cada fase será implementada de forma modular no Terraform.

---

## ✅ Checklist Final

Antes de fazer push:

- [x] Todos os workflows criados em `.github/workflows/`
- [x] Account ID verificado: `204524745296`
- [ ] GitHub Secrets configurados (RDS_PASSWORD, ACM_CERTIFICATE_ARN)
- [ ] IAM Role `github-action-tech-challenge` existe em AWS
- [ ] OIDC Provider configurado em AWS
- [ ] Ready to: `git push origin main`

---

## 🎉 Resumo

**Antes (Manual)**:
- Configure AWS CLI localmente
- Execute scripts bash manualmente
- Deploy manualmente

**Agora (Automático)**:
- Apenas: `git push origin main`
- GitHub Actions faz tudo
- Logs visíveis em tempo real
- Rollback via Git revert

---

**Próximo comando**:
```bash
git add .
git commit -m "feat: Add GitHub Actions CI/CD workflows"
git push origin main
```

Depois, GitHub Actions vai executar tudo automaticamente! 🚀
