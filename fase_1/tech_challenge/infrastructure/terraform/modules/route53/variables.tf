# Route53 Module - To be implemented in FASE 5

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "parent_domain" {
  type = string
}

variable "subdomain" {
  type = string
  default = "tech-challenge"
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar Route53 Hosted Zone + delegação

output "zone_id" {
  value = ""
}

output "zone_nameservers" {
  value = []
}

output "subdomain_fqdn" {
  value = ""
}
