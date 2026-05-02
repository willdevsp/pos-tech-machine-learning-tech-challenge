# ECR Module - To be implemented in FASE 3

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "repositories" {
  type = map(any)
  default = {}
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar ECR repositories

output "repository_uris" {
  value = {}
}
