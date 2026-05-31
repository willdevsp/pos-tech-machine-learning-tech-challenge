terraform {
  required_version = ">= 1.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = var.app_name
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}

# Example placeholder resources to establish dependency configurations
resource "aws_s3_bucket" "model_artifacts" {
  bucket = "${var.app_name}-${var.environment}-model-artifacts"
}
