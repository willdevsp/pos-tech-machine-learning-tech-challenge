# ====================================================================
# RDS MODULE - AURORA SERVERLESS V2
# ====================================================================

locals {
  name_prefix = "${var.project_name}-${var.environment}"
  db_engine   = "aurora-postgresql"
  db_version  = "15.2"  # PostgreSQL 15
}

# ====================================================================
# DB SUBNET GROUP
# ====================================================================

resource "aws_db_subnet_group" "main" {
  name_prefix     = "${local.name_prefix}-db-subnet-"
  subnet_ids      = var.private_subnet_ids
  
  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-db-subnet-group"
    }
  )
}

# ====================================================================
# RDS AURORA CLUSTER (Serverless v2)
# ====================================================================

resource "aws_rds_cluster" "main" {
  cluster_identifier              = "${local.name_prefix}-aurora-cluster"
  engine                          = local.db_engine
  engine_version                  = local.db_version
  database_name                   = var.db_name
  master_username                 = var.db_username
  master_password                 = var.db_password
  
  # Database port
  port                            = 5432
  
  # Subnet and Security Group configuration
  db_subnet_group_name            = aws_db_subnet_group.main.name
  vpc_security_group_ids          = [var.rds_security_group_id]
  
  # Serverless v2 configuration
  engine_mode                     = "provisioned"  # Requires provisioned mode
  
  # Backup configuration
  backup_retention_period         = 7
  preferred_backup_window         = "03:00-04:00"
  storage_encrypted               = true
  kms_key_id                      = aws_kms_key.rds.arn
  
  # Availability zones for multi-AZ
  db_cluster_parameter_group_name = aws_rds_cluster_parameter_group.main.name
  availability_zones              = var.availability_zones
  
  # Other configurations
  skip_final_snapshot             = false
  final_snapshot_identifier       = "${local.name_prefix}-snap-${formatdate("YYYYMMDDhhmm", timeadd(timestamp(), "0s"))}"
  copy_tags_to_snapshot           = true
  
  # Enhanced monitoring (optional but recommended)
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  # Performance Insights (optional)
  performance_insights_enabled    = true
  performance_insights_retention_period = 7
  
  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-aurora-cluster"
    }
  )

  depends_on = [aws_db_subnet_group.main]
}

# ====================================================================
# RDS AURORA INSTANCE (Serverless v2)
# ====================================================================

resource "aws_rds_cluster_instance" "main" {
  count              = 2  # 2 instances for high availability
  cluster_identifier = aws_rds_cluster.main.id
  instance_class     = "db.serverless"
  engine             = local.db_engine
  engine_version     = local.db_version
  
  # Serverless v2 scaling
  # Min ACU: 0.5 (cost-effective)
  # Max ACU: 2 (adjustable based on needs)
  
  publicly_accessible = false
  
  # Monitoring
  monitoring_interval             = 60
  monitoring_role_arn            = aws_iam_role.rds_monitoring.arn
  performance_insights_enabled   = true
  
  # Auto minor version upgrade
  auto_minor_version_upgrade = true
  
  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-aurora-instance-${count.index + 1}"
    }
  )

  depends_on = [aws_rds_cluster.main, aws_iam_role_policy.rds_monitoring]
}

# ====================================================================
# KMS KEY FOR RDS ENCRYPTION
# ====================================================================

resource "aws_kms_key" "rds" {
  description             = "KMS key for RDS Aurora encryption"
  deletion_window_in_days = 10
  enable_key_rotation     = true

  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-rds-key"
    }
  )
}

resource "aws_kms_alias" "rds" {
  name          = "alias/${local.name_prefix}-rds"
  target_key_id = aws_kms_key.rds.key_id
}

# ====================================================================
# IAM ROLE FOR RDS MONITORING
# ====================================================================

resource "aws_iam_role" "rds_monitoring" {
  name_prefix = "${local.name_prefix}-rds-mon-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "monitoring.rds.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })

  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-rds-monitoring-role"
    }
  )
}

resource "aws_iam_role_policy_attachment" "rds_monitoring" {
  role       = aws_iam_role.rds_monitoring.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}

resource "aws_iam_role_policy" "rds_monitoring" {
  name_prefix = "${local.name_prefix}-rds-monitoring-"
  role        = aws_iam_role.rds_monitoring.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:PutLogEvents",
          "logs:CreateLogStream",
          "logs:CreateLogGroup"
        ]
        Resource = "arn:aws:logs:*:*:*"
      }
    ]
  })
}

# ====================================================================
# RDS PARAMETER GROUP (Aurora PostgreSQL)
# ====================================================================

resource "aws_rds_cluster_parameter_group" "main" {
  name_prefix = "${local.name_prefix}-aurora-pg-"
  family      = "aurora-postgresql15"
  
  # Enable logical replication (optional, for CDC/replication) - STATIC parameter (requires reboot)
  parameter {
    name           = "rds.logical_replication"
    value          = "1"
    apply_method   = "pending-reboot"
  }
  
  # Connection pooling - STATIC parameter (requires reboot)
  parameter {
    name           = "shared_preload_libraries"
    value          = "pgaudit,pg_stat_statements"
    apply_method   = "pending-reboot"
  }
  
  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-aurora-pg-params"
    }
  )
}

# ====================================================================
# RDS ENHANCED MONITORING LOG GROUP
# ====================================================================

resource "aws_cloudwatch_log_group" "rds" {
  name              = "/aws/rds/cluster/${local.name_prefix}-aurora"
  retention_in_days = 7

  tags = merge(
    var.tags,
    {
      Name = "${local.name_prefix}-rds-logs"
    }
  )
}

# ====================================================================
# AURORA AUTOSCALING (Serverless v2)
# Note: Aurora Serverless v2 handles auto-scaling automatically
# The ACU scaling (0.5-2) is managed by AWS at the cluster level
# No additional AppAutoScaling configuration needed
# ====================================================================
