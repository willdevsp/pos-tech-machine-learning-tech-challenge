#!/bin/bash

# ====================================================================
# Git Setup Script - Configure local repository for push
# ====================================================================
# Executa configuração básica de git antes do push
# ====================================================================

set -e

echo "🔧 Git Setup & Push Preparation"
echo "=================================="
echo ""

# 1. Verificar se está em um repositório git
if [ ! -d .git ]; then
  echo "❌ Não está em um repositório git"
  echo "   Execute: git init"
  exit 1
fi

# 2. Configurar git (se necessário)
GIT_USER=$(git config user.name)
GIT_EMAIL=$(git config user.email)

if [ -z "$GIT_USER" ]; then
  echo "⚠️  Configure seu nome de usuário git:"
  read -p "Nome: " GIT_USER
  git config user.name "$GIT_USER"
fi

if [ -z "$GIT_EMAIL" ]; then
  echo "⚠️  Configure seu email git:"
  read -p "Email: " GIT_EMAIL
  git config user.email "$GIT_EMAIL"
fi

echo "✅ Git configurado:"
echo "   User: $GIT_USER"
echo "   Email: $GIT_EMAIL"
echo ""

# 3. Verificar alterações
echo "📋 Alterações a fazer commit:"
git status --short
echo ""

# 4. Confirmação antes de push
read -p "Deseja fazer commit e push? (s/N): " CONFIRM

if [ "$CONFIRM" != "s" ] && [ "$CONFIRM" != "S" ]; then
  echo "❌ Operação cancelada"
  exit 0
fi

# 5. Fazer commit
echo "📝 Fazendo commit..."
git add .
git commit -m "feat: Add GitHub Actions CI/CD workflows for automated deployment

- FASE 0: Bootstrap workflow (S3, DynamoDB, IAM Policy)
- Terraform Plan workflow (PR trigger)
- Terraform Apply workflow (main branch)
- Docker Build & Push workflow (ECR)
- Full Stack Deploy workflow (orchestration)

All infrastructure setup now automated via GitHub Actions OIDC.
Account ID: 204524745296"

echo "✅ Commit criado"
echo ""

# 6. Fazer push
echo "🚀 Fazendo push para main..."
git push origin main

echo ""
echo "✅ Push concluído com sucesso!"
echo ""
echo "📊 Próximos passos:"
echo "  1. GitHub Actions vai disparar automaticamente"
echo "  2. Vá para GitHub Repo → Actions para acompanhar"
echo "  3. Primeiro workflow (FASE 0) vai demorar 2-3 minutos"
echo "  4. Monitorar logs em tempo real"
echo ""
echo "🔐 Não esqueça de configurar GitHub Secrets:"
echo "  - Settings → Secrets and variables → Actions"
echo "  - Adicionar: RDS_PASSWORD, ACM_CERTIFICATE_ARN"
echo ""
echo "🎉 Deployment automático iniciado!"
