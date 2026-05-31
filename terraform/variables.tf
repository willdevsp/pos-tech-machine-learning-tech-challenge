variable "aws_region" {
  type        = string
  description = "AWS Target Region for deployment"
  default     = "us-east-1"
}

variable "app_name" {
  type        = string
  description = "Application naming prefix"
  default     = "rocket-tail"
}

variable "environment" {
  type        = string
  description = "Deployment environment name"
  default     = "production"
}
