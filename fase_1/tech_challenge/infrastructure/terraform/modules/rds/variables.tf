# ====================================================================
# RDS MODULE - VARIABLES
# ====================================================================

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (staging/production)"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID where RDS will be deployed"
  type        = string
}

variable "private_subnet_ids" {
  description = "List of private subnet IDs for RDS cluster"
  type        = list(string)
}

variable "availability_zones" {
  description = "List of availability zones for multi-AZ deployment"
  type        = list(string)
}

variable "rds_security_group_id" {
  description = "Security group ID for RDS database"
  type        = string
}

variable "db_name" {
  description = "Initial database name"
  type        = string
  default     = "telco_churn"
}

variable "db_username" {
  description = "Master database username"
  type        = string
  default     = "mlflow"
}

variable "db_password" {
  description = "Master database password (should be stored in AWS Secrets Manager)"
  type        = string
  sensitive   = true
}

variable "tags" {
  description = "Tags to apply to RDS resources"
  type        = map(string)
  default     = {}
}
