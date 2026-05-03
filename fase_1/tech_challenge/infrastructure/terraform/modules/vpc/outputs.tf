# ====================================================================
# VPC MODULE - OUTPUTS
# ====================================================================

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = aws_vpc.main.cidr_block
}

output "public_subnet_ids" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}

output "private_subnet_ids" {
  description = "List of private subnet IDs"
  value       = aws_subnet.private[*].id
}

output "internet_gateway_id" {
  description = "Internet Gateway ID"
  value       = aws_internet_gateway.main.id
}

output "nat_gateway_ids" {
  description = "List of NAT Gateway IDs (empty if not enabled)"
  value       = aws_nat_gateway.main[*].id
}

output "nat_gateway_eips" {
  description = "List of Elastic IP addresses for NAT Gateways"
  value       = aws_eip.nat[*].public_ip
}

# Security Groups
output "alb_security_group_id" {
  description = "Security group ID for ALB"
  value       = aws_security_group.alb.id
}

output "ecs_security_group_id" {
  description = "Security group ID for ECS tasks"
  value       = aws_security_group.ecs.id
}

output "rds_security_group_id" {
  description = "Security group ID for RDS"
  value       = aws_security_group.rds.id
}

output "vpc_endpoints_security_group_id" {
  description = "Security group ID for VPC Endpoints"
  value       = aws_security_group.vpc_endpoints.id
}

# VPC Endpoints
output "s3_endpoint_id" {
  description = "S3 Gateway Endpoint ID"
  value       = aws_vpc_endpoint.s3.id
}

output "ecr_api_endpoint_id" {
  description = "ECR API Interface Endpoint ID"
  value       = aws_vpc_endpoint.ecr_api.id
}

output "ecr_dkr_endpoint_id" {
  description = "ECR DKR Interface Endpoint ID"
  value       = aws_vpc_endpoint.ecr_dkr.id
}

output "logs_endpoint_id" {
  description = "CloudWatch Logs Interface Endpoint ID"
  value       = aws_vpc_endpoint.logs.id
}

# Convenience outputs for other modules
output "availability_zones" {
  description = "List of availability zones"
  value       = var.availability_zones
}

output "public_subnet_count" {
  description = "Number of public subnets"
  value       = length(aws_subnet.public)
}

output "private_subnet_count" {
  description = "Number of private subnets"
  value       = length(aws_subnet.private)
}
