# RDS Module - To be implemented in FASE 2

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "db_name" {
  type = string
}

variable "db_username" {
  type = string
}

variable "db_password" {
  type      = string
  sensitive = true
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar Aurora Serverless v2

output "endpoint" {
  value = "db-placeholder.c123456.us-east-1.rds.amazonaws.com"
}

output "port" {
  value = 5432
}

output "database_name" {
  value = var.db_name
}
