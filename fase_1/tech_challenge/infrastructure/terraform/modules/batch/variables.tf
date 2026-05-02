# Batch Module - To be implemented in FASE 7

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar AWS Batch para training

output "compute_environment_arn" {
  value = ""
}

output "job_queue_arn" {
  value = ""
}
