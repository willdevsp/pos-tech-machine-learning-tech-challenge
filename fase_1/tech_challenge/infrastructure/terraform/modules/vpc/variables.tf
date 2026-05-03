# ====================================================================
# VPC MODULE - VARIABLES
# ====================================================================

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
}

variable "environment" {
  description = "Environment (staging/production)"
  type        = string
  validation {
    condition     = contains(["staging", "production"], var.environment)
    error_message = "Environment deve ser 'staging' ou 'production'."
  }
}

variable "vpc_cidr" {
  description = "CIDR block for VPC"
  type        = string
  validation {
    condition     = can(cidrhost(var.vpc_cidr, 0))
    error_message = "vpc_cidr must be a valid CIDR block."
  }
}

variable "enable_nat" {
  description = "Enable NAT Gateway for private subnets (costs ~$30-45/month)"
  type        = bool
  default     = true
}

variable "availability_zones" {
  description = "List of availability zones"
  type        = list(string)
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  
  # Limitar subnets ao número de AZs (máximo 3 por melhor prática)
  subnet_count = min(3, length(var.availability_zones))
  
  # Subnet CIDR calculations (usando /3 para aceitar até 8 subnets: 4 públicas + 4 privadas)
  public_subnet_cidrs  = [for i in range(local.subnet_count) : cidrsubnet(var.vpc_cidr, 3, i)]
  private_subnet_cidrs = [for i in range(local.subnet_count) : cidrsubnet(var.vpc_cidr, 3, i + local.subnet_count)]
}
