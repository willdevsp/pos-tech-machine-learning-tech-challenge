# ECS Module - To be implemented in FASE 4

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_id" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}

variable "private_subnet_ids" {
  type = list(string)
}

variable "mlflow_image_uri" {
  type = string
}

variable "mlflow_port" {
  type    = number
  default = 5000
}

variable "rds_endpoint" {
  type = string
}

variable "rds_port" {
  type = number
}

variable "rds_database" {
  type = string
}

variable "s3_artifacts_bucket" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar ECS Cluster, Task Definition, Service, ALB

output "alb_dns_name" {
  value = "mlflow-alb-placeholder.elb.us-east-1.amazonaws.com"
}

output "ecs_cluster_name" {
  value = "telco-churn-cluster"
}
