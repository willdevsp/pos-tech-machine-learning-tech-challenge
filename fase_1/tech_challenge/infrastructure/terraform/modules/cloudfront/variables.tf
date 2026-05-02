# CloudFront Module - To be implemented in FASE 5

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "alb_dns_name" {
  type = string
}

variable "route53_zone_id" {
  type = string
}

variable "domain_name" {
  type = string
}

variable "acm_certificate_arn" {
  type = string
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar CloudFront Distribution + ACM certificate

output "distribution_id" {
  value = ""
}

output "domain_name" {
  value = ""
}
