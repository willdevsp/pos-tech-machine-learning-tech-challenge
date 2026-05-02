# CloudWatch Module - To be implemented in FASE 9

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

# TODO: Implementar CloudWatch Logs + Dashboards + Alarms

output "log_group_name" {
  value = ""
}
