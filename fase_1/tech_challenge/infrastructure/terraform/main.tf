# ====================================================================
# MAIN TERRAFORM FILE - Tech Challenge MLflow on AWS
# ====================================================================
# Arquivo principal que orquestra todos os módulos
# Organização:
# - Terraform version e providers
# - Backend (S3 + DynamoDB)
# - Variáveis globais
# - Módulos (VPC, RDS, ECS, ECR, etc)
# ====================================================================

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  
  # Backend será configurado por ambiente (staging/production)
  # Veja: environments/{env}/backend.tf
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "telco-churn-mlflow"
      ManagedBy   = "Terraform"
      CreatedAt   = timestamp()
    }
  }
}

# ====================================================================
# DATA SOURCES
# ====================================================================

data "aws_caller_identity" "current" {}

data "aws_availability_zones" "available" {
  state = "available"
}

# ====================================================================
# VARIÁVEIS GLOBAIS
# ====================================================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment (staging/production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment deve ser 'staging' ou 'production'."
  }
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "telco-churn-mlflow"
}

variable "vpc_cidr" {
  description = "CIDR block para VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "enable_nat_gateway" {
  description = "Habilitar NAT Gateway (custa ~$30-45/mês)"
  type        = bool
  default     = true
}

# ====================================================================
# OUTPUTS GLOBAIS
# ====================================================================

output "aws_region" {
  description = "AWS region sendo utilizada"
  value       = var.aws_region
}

output "environment" {
  description = "Ambiente (staging/production)"
  value       = var.environment
}

output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

# ====================================================================
# MÓDULOS - Fase 1-9
# ====================================================================

# FASE 1: VPC + Segurança
module "vpc" {
  source = "./modules/vpc"

  project_name    = var.project_name
  environment     = var.environment
  vpc_cidr        = var.vpc_cidr
  enable_nat      = var.enable_nat_gateway
  availability_zones = data.aws_availability_zones.available.names

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# FASE 2: RDS (Aurora Serverless v2)
module "rds" {
  source = "./modules/rds"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnet_ids
  
  db_name     = "telco_churn"
  db_username = "mlflow"
  db_password = var.rds_password  # Usar secrets manager
  
  tags = {
    Name = "${var.project_name}-db"
  }

  depends_on = [module.vpc]
}

# FASE 3: ECR Repositories
module "ecr" {
  source = "./modules/ecr"

  project_name = var.project_name
  environment  = var.environment
  
  repositories = {
    mlflow   = { name = "telco-churn-mlflow" }
    api      = { name = "telco-churn-api" }
    training = { name = "telco-churn-training" }
  }

  tags = {
    Name = "${var.project_name}-ecr"
  }
}

# FASE 4: ECS + MLflow
module "ecs" {
  source = "./modules/ecs"

  project_name       = var.project_name
  environment        = var.environment
  vpc_id             = module.vpc.vpc_id
  public_subnet_ids  = module.vpc.public_subnet_ids
  private_subnet_ids = module.vpc.private_subnet_ids
  
  mlflow_image_uri = var.mlflow_image_uri
  mlflow_port      = 5000
  
  rds_endpoint = module.rds.endpoint
  rds_port     = module.rds.port
  rds_database = module.rds.database_name
  
  s3_artifacts_bucket = module.s3.mlflow_artifacts_bucket_id

  depends_on = [module.vpc, module.rds, module.ecr]
}

# FASE 5: Route53 + CloudFront
module "route53" {
  source = "./modules/route53"

  project_name     = var.project_name
  environment      = var.environment
  parent_domain    = var.parent_domain
  subdomain        = "tech-challenge"
  
  tags = {
    Name = "${var.project_name}-route53"
  }
}

module "cloudfront" {
  source = "./modules/cloudfront"

  project_name = var.project_name
  environment  = var.environment
  
  alb_dns_name          = module.ecs.alb_dns_name
  route53_zone_id       = module.route53.zone_id
  domain_name           = module.route53.subdomain_fqdn
  
  acm_certificate_arn = var.acm_certificate_arn

  tags = {
    Name = "${var.project_name}-cloudfront"
  }

  depends_on = [module.route53, module.ecs]
}

# FASE 6: Lambda API
# TODO: Implementar quando chegarmos a essa fase

# FASE 7: AWS Batch
# TODO: Implementar quando chegarmos a essa fase

# FASE 8: EventBridge
# TODO: Implementar quando chegarmos a essa fase

# FASE 9: Monitoring + Alarms
# TODO: Implementar quando chegarmos a essa fase

# ====================================================================
# S3 BUCKETS
# ====================================================================

module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  environment  = var.environment
  aws_region   = var.aws_region

  bucket_names = {
    terraform_state = "telco-tf-state"
    mlflow_artifacts = "telco-mlflow-artifacts"
    processed_data = "telco-processed-data"
    training_datasets = "telco-training-datasets"
    logs = "telco-logs"
    rds_backups = "telco-rds-backups"
  }

  tags = {
    Name = "${var.project_name}-s3"
  }
}

# ====================================================================
# VARIÁVEIS QUE PRECISAM SER DEFINIDAS POR AMBIENTE
# ====================================================================

variable "rds_password" {
  description = "RDS master password (use AWS Secrets Manager em produção)"
  type        = string
  sensitive   = true
}

variable "mlflow_image_uri" {
  description = "URI da imagem Docker MLflow no ECR"
  type        = string
}

variable "parent_domain" {
  description = "Domínio pai para delegação (ex: asgardprint.com.br)"
  type        = string
}

variable "acm_certificate_arn" {
  description = "ARN do certificado ACM para HTTPS"
  type        = string
}
