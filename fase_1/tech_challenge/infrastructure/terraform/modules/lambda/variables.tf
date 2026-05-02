# Lambda Module - To be implemented in FASE 6

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

# TODO: Implementar Lambda para API predictions

output "lambda_function_arn" {
  value = ""
}

output "api_gateway_url" {
  value = ""
}
