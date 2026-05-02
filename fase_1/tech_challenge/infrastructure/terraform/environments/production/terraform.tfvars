# ====================================================================
# PRODUCTION ENVIRONMENT VARIABLES
# ====================================================================

aws_region  = "us-east-1"
environment = "production"

# VPC Configuration
vpc_cidr           = "10.0.0.0/16"
enable_nat_gateway = true

# RDS Configuration
# ⚠️  IMPORTANTE: Usar AWS Secrets Manager para senha em produção
# Provisoriamente, pode usar uma variável de ambiente:
# export TF_VAR_rds_password="sua-senha-segura"
# rds_password = "MUDE-PARA-SECRETS-MANAGER"

# MLflow Image (será preenchido por CI/CD)
# Formato: 123456789.dkr.ecr.us-east-1.amazonaws.com/telco-churn-mlflow:latest
# mlflow_image_uri = "SERÁ-PREENCHIDO-POR-CI-CD"

# Route53 & Domain
parent_domain = "asgardprint.com.br"

# ACM Certificate
# Deve ser criado manualmente em AWS console ou via Terraform
# acm_certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/..."

# ====================================================================
# TAGS
# ====================================================================

tags = {
  Environment = "production"
  CostCenter  = "engineering"
  Owner       = "telco-team"
}
