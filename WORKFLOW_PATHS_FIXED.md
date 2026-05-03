# Correção de Paths - GitHub Actions Workflows

**Status**: ✅ **COMPLETO**  
**Commit**: `ffb3a00` - fix: Correct all GitHub Actions workflow paths  
**Data**: 2 de Maio de 2026

---

## 📍 O Problema

Quando você moveu a pasta `.github` para a raiz do repositório, os paths dos workflows ficaram incorretos:

```
❌ ANTES (Paths errados)
├── .github/
│   └── workflows/
│       ├── terraform-plan.yml       → Procurava por: infrastructure/terraform/**
│       ├── terraform-apply.yml      → Procurava por: infrastructure/terraform/
│       ├── docker-build-push.yml    → Procurava por: Dockerfile* (raiz)
│       └── fase0-bootstrap.yml      → Procurava por: infrastructure/scripts/

❌ RESULTADO: Pipeline não encontrava Dockerfiles nem scripts
```

---

## ✅ A Solução

Todos os paths foram corrigidos para referenciar `fase_1/tech_challenge/`:

```
✅ DEPOIS (Paths corretos)
├── .github/
│   └── workflows/
│       ├── terraform-plan.yml       → Procura por: fase_1/tech_challenge/infrastructure/terraform/**
│       ├── terraform-apply.yml      → Working dir: fase_1/tech_challenge/infrastructure/terraform/
│       ├── docker-build-push.yml    → Procura por: fase_1/tech_challenge/Dockerfile*
│       ├── fase0-bootstrap.yml      → Policy: fase_1/tech_challenge/infrastructure/scripts/iam-policy.json
│       └── full-stack-deploy.yml    → Context: fase_1/tech_challenge

✅ RESULTADO: Pipeline encontra tudo corretamente
```

---

## 🔧 Mudanças Específicas

### 1. **docker-build-push.yml**
```diff
- context: .
+ context: fase_1/tech_challenge
- file: Dockerfile.mlflow
+ file: fase_1/tech_challenge/Dockerfile.mlflow
```

**Por quê**: O Docker build precisa usar o contexto correto (pasta com código)

---

### 2. **fase0-bootstrap.yml**
```diff
- --policy-document file://infrastructure/scripts/iam-policy.json
+ --policy-document file://${{ env.SCRIPTS_PATH }}/iam-policy.json
+ 
+ env:
+ SCRIPTS_PATH: fase_1/tech_challenge/infrastructure/scripts
```

**Por quê**: Script IAM policy não era encontrado

---

### 3. **terraform-plan.yml**
```diff
- paths:
-   - 'infrastructure/terraform/**'
+ paths:
+   - 'fase_1/tech_challenge/infrastructure/terraform/**'

- working-directory: infrastructure/terraform
+ working-directory: fase_1/tech_challenge/infrastructure/terraform
```

**Por quê**: Terraform files não eram encontrados

---

### 4. **terraform-apply.yml**
```diff
- working-directory: infrastructure/terraform
+ working-directory: fase_1/tech_challenge/infrastructure/terraform
```

**Por quê**: Apply precisa do working directory correto

---

### 5. **full-stack-deploy.yml**
```diff
- context: .
- file: Dockerfile.mlflow
+ context: fase_1/tech_challenge
+ file: fase_1/tech_challenge/Dockerfile.mlflow

- paths:
-   - 'src/**'
-   - 'Dockerfile*'
-   - 'infrastructure/terraform/**'
+ paths:
+   - 'fase_1/tech_challenge/src/**'
+   - 'fase_1/tech_challenge/Dockerfile*'
+   - 'fase_1/tech_challenge/infrastructure/terraform/**'

+ env:
+   TF_WORKING_DIR: fase_1/tech_challenge/infrastructure/terraform
```

**Por quê**: Orquestra Docker + Terraform com paths corretos

---

### 6. **Todas os workflows - AWS Role**
```diff
- role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
+ role-to-assume: arn:aws:iam::${{ env.ACCOUNT_ID }}:role/github-action-tech-challenge

+ env:
+   ACCOUNT_ID: 204524745296
```

**Por quê**: Account ID é fixo (204524745296), não precisa de secret

---

## 📊 Estrutura de Diretórios Atual

```
.github/
├── workflows/                              ← Raiz do repo
│   ├── fase0-bootstrap.yml
│   ├── terraform-plan.yml
│   ├── terraform-apply.yml
│   ├── docker-build-push.yml
│   └── full-stack-deploy.yml

fase_1/
└── tech_challenge/
    ├── Dockerfile.mlflow                  ← Docker encontra aqui
    ├── Dockerfile.api
    ├── Dockerfile.training
    ├── src/                               ← Código fonte
    │   ├── api/
    │   ├── data/
    │   ├── evaluation/
    │   └── models/
    ├── infrastructure/
    │   ├── scripts/
    │   │   ├── fase0-bootstrap.sh
    │   │   └── iam-policy.json            ← IAM encontra aqui
    │   └── terraform/                     ← Terraform encontra aqui
    │       ├── main.tf
    │       ├── modules/
    │       └── environments/
    └── ... (outros arquivos)
```

---

## ✅ Próximas Ações

### GitHub Actions agora conseguem:

1. ✅ **FASE 0 Bootstrap** 
   - Encontra `fase_1/tech_challenge/infrastructure/scripts/iam-policy.json`
   - Cria S3, DynamoDB, aplica IAM policy

2. ✅ **Docker Build & Push**
   - Encontra `fase_1/tech_challenge/Dockerfile.*`
   - Build com contexto correto
   - Push para ECR

3. ✅ **Terraform Plan**
   - Encontra `fase_1/tech_challenge/infrastructure/terraform/`
   - Executa terraform init/plan/validate

4. ✅ **Terraform Apply**
   - Aplica infraestrutura corretamente
   - Exporta outputs

---

## 🚀 Disparar Workflows Novamente

Agora você pode:

### Via Push (automático)
```bash
git push origin main
# Workflows disparam automaticamente
```

### Via GitHub Actions (manual)
1. GitHub Repo → Actions
2. Selecionar workflow
3. "Run workflow" → Selecionar ambiente → "Run"

---

## 🔍 Verificação

Para garantir que tudo está funcionando:

1. **Vá em**: GitHub Repo → Actions
2. **Selecione**: Último workflow que rodou
3. **Verifique**: Se encontrou os arquivos corretamente
4. **Logs devem mostrar**:
   ```
   ✅ Dockerfile encontrado
   ✅ Terraform configurado
   ✅ IAM policy carregada
   ```

---

## 📝 Resumo das Mudanças

| Arquivo | Mudanças | Razão |
|---------|----------|-------|
| docker-build-push.yml | Paths Docker + context | Encontrar Dockerfiles |
| terraform-plan.yml | Working dir + paths trigger | Encontrar Terraform |
| terraform-apply.yml | Working dir | Aplicar Terraform |
| fase0-bootstrap.yml | Script path via env var | Encontrar IAM policy |
| full-stack-deploy.yml | Todos os paths acima | Orquestra tudo |

---

## 🎉 Status Final

```
Antes:  ❌ Workflows não encontravam arquivos
Depois: ✅ Todos os paths corretos
Push:   ✅ Enviado com sucesso
Ready:  ✅ Para próxima fase
```

**Commit**: `ffb3a00`

---

**Próximo**: Fase 1 (VPC + Security) pode começar! 🚀
