# ====================================================================
# RDS MODULE - OUTPUTS
# ====================================================================

# Aurora Cluster Outputs
output "cluster_id" {
  description = "Aurora cluster ID"
  value       = aws_rds_cluster.main.id
}

output "cluster_arn" {
  description = "Aurora cluster ARN"
  value       = aws_rds_cluster.main.arn
}

output "endpoint" {
  description = "Aurora cluster write endpoint (for connections)"
  value       = aws_rds_cluster.main.endpoint
}

output "reader_endpoint" {
  description = "Aurora cluster read endpoint (for read replicas)"
  value       = aws_rds_cluster.main.reader_endpoint
}

output "port" {
  description = "Database port"
  value       = aws_rds_cluster.main.port
}

output "database_name" {
  description = "Database name"
  value       = aws_rds_cluster.main.database_name
}

output "master_username" {
  description = "Master username"
  value       = aws_rds_cluster.main.master_username
  sensitive   = true
}

output "db_subnet_group_name" {
  description = "DB subnet group name"
  value       = aws_db_subnet_group.main.name
}

# Serverless v2 specific outputs
output "serverless_min_acu" {
  description = "Minimum Aurora Capacity Units (ACU) for Serverless v2"
  value       = 0.5
}

output "serverless_max_acu" {
  description = "Maximum Aurora Capacity Units (ACU) for Serverless v2"
  value       = 2
}

output "instance_count" {
  description = "Number of Aurora instances in the cluster"
  value       = length(aws_rds_cluster_instance.main)
}

# Connection string outputs (for reference)
output "connection_string" {
  description = "JDBC-style connection string"
  value       = "jdbc:postgresql://${aws_rds_cluster.main.endpoint}:${aws_rds_cluster.main.port}/${aws_rds_cluster.main.database_name}"
  sensitive   = true
}

output "psql_connection_command" {
  description = "psql command to connect to the database"
  value       = "psql -h ${aws_rds_cluster.main.endpoint} -U ${aws_rds_cluster.main.master_username} -d ${aws_rds_cluster.main.database_name}"
  sensitive   = true
}

# Security & Monitoring
output "kms_key_id" {
  description = "KMS key ID for RDS encryption"
  value       = aws_kms_key.rds.id
}

output "monitoring_role_arn" {
  description = "IAM role ARN for RDS monitoring"
  value       = aws_iam_role.rds_monitoring.arn
}

output "cloudwatch_log_group" {
  description = "CloudWatch log group for RDS"
  value       = aws_cloudwatch_log_group.rds.name
}

# Autoscaling outputs
output "autoscaling_target_id" {
  description = "Application Auto Scaling target ID"
  value       = aws_appautoscaling_target.rds_target.id
}

output "cpu_scaling_policy_name" {
  description = "CPU-based auto scaling policy name"
  value       = aws_appautoscaling_policy.rds_cpu.name
}

output "connections_scaling_policy_name" {
  description = "Connections-based auto scaling policy name"
  value       = aws_appautoscaling_policy.rds_connections.name
}
