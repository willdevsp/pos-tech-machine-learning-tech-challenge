# IAM Module - Roles and Policies

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

# TODO: Implementar IAM roles para ECS, Lambda, Batch

output "ecs_task_execution_role_arn" {
  value = ""
}

output "ecs_task_role_arn" {
  value = ""
}
