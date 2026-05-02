# ====================================================================
# TERRAFORM BACKEND CONFIGURATION - Staging
# ====================================================================
# Estado será armazenado em S3 + DynamoDB para locking
# Criado em FASE 0 (bootstrap)

terraform {
  backend "s3" {
    # Nome do bucket: telco-tf-state-{ACCOUNT_ID}
    # ⚠️  Substituir {ACCOUNT_ID} com seu Account ID
    bucket         = "telco-tf-state-204524745296"  # MUDE PARA SEU ACCOUNT ID
    key            = "staging/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "telco-tf-locks"
  }
}
