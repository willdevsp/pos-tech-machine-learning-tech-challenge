# 🚀 FASE 0 - AÇÃO IMEDIATA

**Status**: ✅ Arquivos estrutura Terraform preparados  
**Próximos passos**: Configurar AWS + executar bootstrap  
**Tempo restante**: ~45 minutos

---

## 📋 Checklist - O QUE FAZER AGORA

### 1. ✅ VERIFICAR PRÉ-REQUISITOS

- [x] Domínio registrado (asgardprint.com.br)
- [x] AWS Account criada
- [x] Billing alerts configurados
- [x] GitHub OIDC Provider já criado em AWS
- [x] IAM Role `github-action-tech-challenge` já criada
- [ ] **AÇÃO**: Verificar que tudo acima está realmente OK

### 2. 🔴 CONFIGURAR AWS CLI (ESSENCIAL)

Seu AWS CLI **NÃO está configurado** no terminal.

```bash
# OPÇÃO A: Usar credenciais de Access Key (rápido, menos seguro)
aws configure

# Será pedido:
# AWS Access Key ID: [colar seu access key]
# AWS Secret Access Key: [colar seu secret key]
# Default region name: us-east-1
# Default output format: json

# OPÇÃO B: Usar AWS SSO/IAM Identity Center (recomendado, mais seguro)
aws configure sso
# Seguir prompts para selecionar sua organização/account
```

**Testar se funcionou:**
```bash
aws sts get-caller-identity
# Deve retornar: Account ID, UserId, ARN
```

### 3. 📝 PREPARAR ACCOUNT ID

Copie seu Account ID (será necessário em vários arquivos):

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "Seu Account ID: $ACCOUNT_ID"
```

**⚠️ IMPORTANTE**: Você vai precisar substituir `204524745296` pelos arquivos:
- `infrastructure/terraform/environments/production/backend.tf` (linha do bucket)
- `infrastructure/terraform/environments/staging/backend.tf` (linha do bucket)

### 4. 🏃 EXECUTAR BOOTSTRAP (FASE 0 OFICIAL)

```bash
cd fase_1/tech_challenge/infrastructure/scripts

# Tornar script executável
chmod +x fase0-bootstrap.sh

# Executar
bash fase0-bootstrap.sh
```

**O que esse script vai fazer:**
1. ✅ Criar S3 bucket `telco-tf-state-{ACCOUNT_ID}`
2. ✅ Ativar versionamento no bucket
3. ✅ Ativar encriptação AES256
4. ✅ Bloquear acesso público
5. ✅ Criar DynamoDB table `telco-tf-locks`
6. ✅ Aplicar IAM Policy ao role `github-action-tech-challenge`

**Duração**: ~2-3 minutos

### 5. ✅ VALIDAR BOOTSTRAP

Depois que o script terminar, ele vai exibir:

```
✅ FASE 0 CONCLUÍDO COM SUCESSO!

📋 PRÓXIMAS AÇÕES:

1️⃣  Configurar GitHub Secrets (no repositório)...
2️⃣  Configurar Route53 zona pai...
3️⃣  Preparar código para Terraform...
4️⃣  Começar FASE 1...
```

---

## 🔐 CONFIGURAR GITHUB SECRETS (APÓS BOOTSTRAP)

Depois que bootstrap terminar com sucesso:

1. **Abrir GitHub repositório**
2. **Ir para Settings → Secrets and variables → Actions**
3. **Criar 2 secrets:**

| Nome | Valor | Exemplo |
|------|-------|---------|
| `AWS_ROLE_ARN` | ARN do role github-action (será exibido no terminal) | `arn:aws:iam::204524745296:role/github-action-tech-challenge` |
| `AWS_REGION` | us-east-1 | `us-east-1` |

---

## 📝 SUBSTITUIR ACCOUNT ID

**Antes de usar Terraform**, substituir Account ID nos arquivos:

```bash
# Copiar seu Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Editar arquivo production
# Mudar "telco-tf-state-204524745296" para "telco-tf-state-$ACCOUNT_ID"
# Arquivo: infrastructure/terraform/environments/production/backend.tf

# Editar arquivo staging
# Arquivo: infrastructure/terraform/environments/staging/backend.tf
```

---

## 🔄 PRÓXIMAS FASES (DEPOIS DE FASE 0)

Depois que bootstrap funcionar:

### ✅ FASE 1: VPC + Segurança (1h)
```bash
cd infrastructure/terraform
terraform init -backend-config=environments/staging/backend.tf
terraform plan -var-file=environments/staging/terraform.tfvars

# Será necessário fornecer:
# - rds_password
# - mlflow_image_uri (deixar em branco por agora)
# - acm_certificate_arn (deixar em branco por agora)
```

### ⏳ FASE 2-9: Implementar módulos Terraform conforme plano

---

## ❌ TROUBLESHOOTING

### Erro: "Unable to locate credentials"
```bash
# Solução: Configurar AWS CLI
aws configure
# ou
aws configure sso
```

### Erro: "S3 bucket already exists"
- Esperado se bootstrap rodou antes
- Script verifica e pula se já existe

### Erro: "NoCredentialProviders" no Terraform
```bash
# Verificar que AWS CLI está configurado
aws sts get-caller-identity

# Se não funcionar, usar variáveis de ambiente
export AWS_ACCESS_KEY_ID="sua-key"
export AWS_SECRET_ACCESS_KEY="sua-secret"
```

### Erro: "DynamoDB table already exists"
- Esperado se bootstrap rodou antes
- Script pula automaticamente

### Erro: "IAM Role not found"
- **Ação**: Criar role em AWS console antes
  - Nome: `github-action-tech-challenge`
  - Trusted entity: OIDC (token.actions.githubusercontent.com)

---

## 📊 RESUMO TIMELINE

```
🔴 AGORA (5 min)      → Configurar AWS CLI
🟡 Próximo (30 min)   → Executar fase0-bootstrap.sh
🟢 Depois (15 min)    → Configurar GitHub Secrets
🔵 Então (1h)         → Começar FASE 1 (Terraform)
```

**Total FASE 0**: ~50 minutos

---

## 🎯 PRÓXIMO COMANDO A EXECUTAR

```bash
# 1. Configurar AWS
aws configure

# 2. Verificar
aws sts get-caller-identity

# 3. Executar bootstrap
cd fase_1/tech_challenge/infrastructure/scripts
bash fase0-bootstrap.sh

# 4. Guardar output (AWS_ROLE_ARN, AWS_REGION)
```

---

## 📞 PRECISA DE AJUDA?

Verificar:
1. `plano_ci_cd/CHECKLIST_PRE_DEPLOYMENT.md` - Step-by-step oficial
2. `infrastructure/README.md` - Documentação Terraform
3. `infrastructure/scripts/fase0-bootstrap.sh` - Script comentado

---

**Status Final FASE 0 Prep**: ✅ COMPLETO  
**Aguardando**: Você executar comandos acima
