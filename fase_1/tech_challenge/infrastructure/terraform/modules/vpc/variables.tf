# VPC Module - To be implemented in FASE 1

variable "project_name" {
  type = string
}

variable "environment" {
  type = string
}

variable "vpc_cidr" {
  type = string
}

variable "enable_nat" {
  type = bool
  default = true
}

variable "availability_zones" {
  type = list(string)
}

variable "tags" {
  type = map(string)
  default = {}
}

# TODO: Implementar VPC, Subnets, IGW, NAT, Security Groups

output "vpc_id" {
  value = "vpc-placeholder"
}

output "public_subnet_ids" {
  value = []
}

output "private_subnet_ids" {
  value = []
}
