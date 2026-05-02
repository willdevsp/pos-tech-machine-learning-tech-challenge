# ====================================================================
# STAGING ENVIRONMENT VARIABLES
# ====================================================================

aws_region  = "us-east-1"
environment = "staging"

# VPC Configuration
vpc_cidr           = "10.1.0.0/16"
enable_nat_gateway = false  # Economizar em staging

# RDS Configuration
# rds_password = "MUDE-PARA-SECRETS-MANAGER"

# MLflow Image (será preenchido por CI/CD)
# mlflow_image_uri = "SERÁ-PREENCHIDO-POR-CI-CD"

# Route53 & Domain
parent_domain = "asgardprint.com.br"

# ACM Certificate
# acm_certificate_arn = "arn:aws:acm:us-east-1:123456789:certificate/..."

# ====================================================================
# TAGS
# ====================================================================

tags = {
  Environment = "staging"
  CostCenter  = "engineering"
  Owner       = "telco-team"
}
