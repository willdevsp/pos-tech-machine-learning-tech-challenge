#!/bin/bash

# ====================================================================
# FASE 0: BOOTSTRAP AWS - SETUP CRÍTICO PARA TERRAFORM + CI/CD
# ====================================================================
# Este script executa os comandos críticos para preparar AWS para:
# 1. Terraform backend (S3 + DynamoDB)
# 2. IAM Role para GitHub Actions (OIDC)
# ====================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 FASE 0: AWS Bootstrap${NC}"
echo "==========================================="
echo ""

# ====================================================================
# STEP 1: Verificar se AWS CLI está configurado
# ====================================================================
echo -e "${YELLOW}Step 1/5: Verificando AWS CLI...${NC}"

if ! command -v aws &> /dev/null; then
  echo -e "${RED}❌ AWS CLI não encontrado. Instale: https://aws.amazon.com/cli/${NC}"
  exit 1
fi

# Verificar credenciais
if ! aws sts get-caller-identity &> /dev/null; then
  echo -e "${RED}❌ AWS credenciais não configuradas. Execute: aws configure${NC}"
  exit 1
fi

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION=${AWS_REGION:-us-east-1}

echo -e "${GREEN}✅ AWS CLI configurado${NC}"
echo "   Account ID: $ACCOUNT_ID"
echo "   Region: $AWS_REGION"
echo ""

# ====================================================================
# STEP 2: Criar S3 bucket para Terraform state
# ====================================================================
echo -e "${YELLOW}Step 2/5: Criando S3 bucket (terraform state)...${NC}"

BUCKET_NAME="telco-tf-state-${ACCOUNT_ID}"

# Verificar se bucket já existe
if aws s3 ls "s3://${BUCKET_NAME}" 2>/dev/null; then
  echo -e "${YELLOW}⚠️  Bucket ${BUCKET_NAME} já existe. Pulando criação.${NC}"
else
  aws s3api create-bucket \
    --bucket "$BUCKET_NAME" \
    --region "$AWS_REGION" \
    $([ "$AWS_REGION" != "us-east-1" ] && echo "--create-bucket-configuration LocationConstraint=$AWS_REGION")
  
  echo -e "${GREEN}✅ Bucket criado: $BUCKET_NAME${NC}"
fi

# Ativar versionamento
aws s3api put-bucket-versioning \
  --bucket "$BUCKET_NAME" \
  --versioning-configuration Status=Enabled

echo -e "${GREEN}✅ Versionamento habilitado${NC}"

# Aplicar encriptação AES256
aws s3api put-bucket-encryption \
  --bucket "$BUCKET_NAME" \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'

echo -e "${GREEN}✅ Encriptação AES256 habilitada${NC}"

# Bloquear acesso público
aws s3api put-public-access-block \
  --bucket "$BUCKET_NAME" \
  --public-access-block-configuration \
    BlockPublicAcls=true,IgnorePublicAcls=true,BlockPublicPolicy=true,RestrictPublicBuckets=true

echo -e "${GREEN}✅ Bloqueio de acesso público aplicado${NC}"
echo ""

# ====================================================================
# STEP 3: Criar DynamoDB table para Terraform locking
# ====================================================================
echo -e "${YELLOW}Step 3/5: Criando DynamoDB table (terraform locks)...${NC}"

LOCK_TABLE="telco-tf-locks"

# Verificar se tabela já existe
if aws dynamodb describe-table --table-name "$LOCK_TABLE" &>/dev/null; then
  echo -e "${YELLOW}⚠️  DynamoDB table ${LOCK_TABLE} já existe. Pulando criação.${NC}"
else
  aws dynamodb create-table \
    --table-name "$LOCK_TABLE" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST \
    --region "$AWS_REGION"
  
  echo -e "${GREEN}✅ DynamoDB table criada: $LOCK_TABLE${NC}"
  
  # Aguardar tabela estar disponível
  echo "   Aguardando tabela ficar ativa..."
  aws dynamodb wait table-exists --table-name "$LOCK_TABLE" --region "$AWS_REGION"
  echo -e "${GREEN}✅ Tabela ativa${NC}"
fi
echo ""

# ====================================================================
# STEP 4: Aplicar IAM Policy ao role existente
# ====================================================================
echo -e "${YELLOW}Step 4/5: Aplicando IAM Policy ao role...${NC}"

ROLE_NAME="github-action-tech-challenge"
POLICY_FILE="./iam-policy.json"

if [ ! -f "$POLICY_FILE" ]; then
  echo -e "${RED}❌ Arquivo $POLICY_FILE não encontrado.${NC}"
  echo "   Certifique-se que o arquivo está no diretório atual."
  exit 1
fi

# Verificar se role existe
if ! aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
  echo -e "${RED}❌ IAM Role ${ROLE_NAME} não encontrada.${NC}"
  echo "   Certifique-se que a role foi criada em AWS console."
  exit 1
fi

# Aplicar policy
aws iam put-role-policy \
  --role-name "$ROLE_NAME" \
  --policy-name TechChallengeTerraformPolicy \
  --policy-document "file://$POLICY_FILE"

echo -e "${GREEN}✅ IAM Policy aplicada ao role: $ROLE_NAME${NC}"
echo ""

# ====================================================================
# STEP 5: Exibir configurações finais
# ====================================================================
echo -e "${YELLOW}Step 5/5: Validações finais...${NC}"

# Validar S3 bucket
echo "   Verificando S3 bucket..."
if aws s3api get-bucket-versioning --bucket "$BUCKET_NAME" | grep -q "Enabled"; then
  echo -e "${GREEN}   ✅ S3 versioning: OK${NC}"
fi

# Validar DynamoDB
echo "   Verificando DynamoDB..."
if aws dynamodb describe-table --table-name "$LOCK_TABLE" --query 'Table.TableStatus' | grep -q "ACTIVE"; then
  echo -e "${GREEN}   ✅ DynamoDB: OK${NC}"
fi

# Validar IAM Role
echo "   Verificando IAM Role..."
if aws iam get-role --role-name "$ROLE_NAME" &>/dev/null; then
  ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text)
  echo -e "${GREEN}   ✅ IAM Role: OK${NC}"
  echo "   ARN: $ROLE_ARN"
fi

echo ""
echo -e "${GREEN}✅ FASE 0 CONCLUÍDO COM SUCESSO!${NC}"
echo ""
echo "=========================================="
echo "📋 PRÓXIMAS AÇÕES:"
echo "=========================================="
echo ""
echo "1️⃣  Configurar GitHub Secrets (no repositório):"
echo "   - AWS_ROLE_ARN = $ROLE_ARN"
echo "   - AWS_REGION = $AWS_REGION"
echo ""
echo "2️⃣  Configurar Route53 zona pai (asgardprint.com.br):"
echo "   - Certifique-se que está criada em AWS console"
echo ""
echo "3️⃣  Preparar código para Terraform:"
echo "   - Criar infrastructure/terraform/main.tf"
echo "   - Configurar backend.tf (Phases 1-9)"
echo ""
echo "4️⃣  Começar FASE 1 (VPC + Segurança):"
echo "   - Executar: cd infrastructure/terraform && terraform init"
echo "   - Executar: terraform plan -var-file=environments/production/terraform.tfvars"
echo ""
echo "=========================================="
