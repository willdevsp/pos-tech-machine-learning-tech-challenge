# S3 Module - To be implemented

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "aws_region" {
  type = string
}

variable "bucket_names" {
  type = map(string)
  default = {}
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar S3 buckets com versioning, encryption, lifecycle policies

output "terraform_state_bucket" {
  value = ""
}

output "mlflow_artifacts_bucket_id" {
  value = ""
}

output "processed_data_bucket" {
  value = ""
}
