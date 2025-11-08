# ============================================================================
# Data source: Consume shared infrastructure from remote state
# ============================================================================
data "terraform_remote_state" "shared" {
  backend = "s3"
  config = {
    bucket = var.tf_backend_bucket
    key    = var.shared_state_key
    region = var.aws_region
  }
}

locals {
  name = "${var.project}-${var.environment}"
  
  # Recursos compartidos desde el remote state
  cluster_name       = data.terraform_remote_state.shared.outputs.cluster_name
  rabbitmq_url       = data.terraform_remote_state.shared.outputs.rabbitmq_amqp_url
  
  vpc_id             = data.terraform_remote_state.shared.outputs.vpc_id
  private_subnet_ids = data.terraform_remote_state.shared.outputs.private_subnet_ids
  oidc_provider_arn  = data.terraform_remote_state.shared.outputs.oidc_provider_arn
  
  # Get the node security group ID from EKS nodes
  node_security_group_id = try(tolist(data.aws_instance.eks_node_sample[0].vpc_security_group_ids)[0], null)
}

# Derivamos el CIDR de la VPC SIN tocar el shared
data "aws_vpc" "this" {
  id = local.vpc_id
}

# Data source: Get security group of EKS nodes
data "aws_instances" "eks_nodes" {
  filter {
    name   = "tag:kubernetes.io/cluster/${local.cluster_name}"
    values = ["owned"]
  }
  
  filter {
    name   = "instance-state-name"
    values = ["running"]
  }
}

# Get the first node instance to extract its security group
data "aws_instance" "eks_node_sample" {
  count       = length(data.aws_instances.eks_nodes.ids) > 0 ? 1 : 0
  instance_id = data.aws_instances.eks_nodes.ids[0]
}

# ============================================================================
# Recursos del micro: RDS + Secrets + IAM
# ============================================================================
# Use a fixed suffix to avoid recreating resources on every apply
# ============================================================================
locals {
  # Fixed suffix based on current resources (5c2c)
  # DO NOT CHANGE THIS - it will recreate all secrets
  resource_suffix = "5c2c"
}

resource "random_password" "db_password" {
  length  = 20
  special = true
  # Evitar caracteres que puedan causar problemas en URLs de conexión
  override_special = "!#$%&*()-_=+[]{}<>:?"
  
  lifecycle {
    ignore_changes = all
  }
}

# ----------------------------------------------------------------------------
# Secret principal de configuración de la aplicación
# ----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "app" {
  name        = "${local.name}/application-${local.resource_suffix}"
  description = "Application configuration for ${local.name}"
  
  tags = {
    Name        = "${local.name}-app-config"
    Service     = "connectivity"
    Environment = var.environment
  }
}

# ----------------------------------------------------------------------------
# Security Groups (limitados al CIDR de la VPC)
# ----------------------------------------------------------------------------
resource "aws_security_group" "rds" {
  name        = "${local.name}-rds-sg"
  description = "SG for RDS PostgreSQL (${local.name})"
  vpc_id      = local.vpc_id
  
  tags = {
    Name        = "${local.name}-rds-sg"
    Service     = "connectivity"
    Environment = var.environment
  }
}

# Allow traffic from entire VPC CIDR (fallback)
resource "aws_vpc_security_group_ingress_rule" "rds_ingress_cidr" {
  security_group_id = aws_security_group.rds.id
  cidr_ipv4         = data.aws_vpc.this.cidr_block
  ip_protocol       = "tcp"
  from_port         = 5432
  to_port           = 5432
  description       = "Allow PostgreSQL from VPC CIDR"
}

# Allow traffic from EKS node security group (more specific)
resource "aws_vpc_security_group_ingress_rule" "rds_ingress_from_nodes" {
  count                        = local.node_security_group_id != null ? 1 : 0
  security_group_id            = aws_security_group.rds.id
  referenced_security_group_id = local.node_security_group_id
  ip_protocol                  = "tcp"
  from_port                    = 5432
  to_port                      = 5432
  description                  = "Allow PostgreSQL from EKS nodes"
}

resource "aws_vpc_security_group_egress_rule" "rds_egress" {
  security_group_id = aws_security_group.rds.id
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
  description       = "Allow all outbound traffic"
}

# ----------------------------------------------------------------------------
# RDS PostgreSQL (barato dev)
# ----------------------------------------------------------------------------
resource "aws_db_subnet_group" "rds" {
  name       = "${local.name}-rds-subnets"
  subnet_ids = local.private_subnet_ids
  
  tags = {
    Name        = "${local.name}-rds-subnets"
    Service     = "connectivity"
    Environment = var.environment
  }
}

resource "aws_db_parameter_group" "rds" {
  name   = "${local.name}-rds-params"
  family = "postgres16"
  
  parameter {
    name  = "log_min_duration_statement"
    value = "2000"
  }
  
  parameter {
    name  = "log_connections"
    value = "1"
  }
  
  parameter {
    name  = "log_disconnections"
    value = "1"
  }
  
  tags = {
    Name        = "${local.name}-rds-params"
    Service     = "connectivity"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret" "rds_credentials" {
  name        = "${local.name}/rds/postgresql-${local.resource_suffix}"
  description = "RDS PostgreSQL credentials for ${local.name}"
  
  tags = {
    Name        = "${local.name}-rds-credentials"
    Service     = "connectivity"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "rds_credentials_initial" {
  secret_id     = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username = "appuser"
    password = random_password.db_password.result
    engine   = "postgres"
    host     = null
    port     = 5432
    dbname   = "connectivity_db"
  })
}

resource "aws_db_instance" "postgres" {
  identifier                 = "${local.name}-pg"
  engine                     = "postgres"
  engine_version             = "16.3"
  instance_class             = "db.t4g.micro"
  allocated_storage          = 20
  db_name                    = "connectivity_db"
  username                   = "appuser"
  password                   = random_password.db_password.result
  db_subnet_group_name       = aws_db_subnet_group.rds.name
  vpc_security_group_ids     = [aws_security_group.rds.id]
  parameter_group_name       = aws_db_parameter_group.rds.name
  storage_encrypted          = true
  backup_retention_period    = 1
  deletion_protection        = false
  auto_minor_version_upgrade = true
  multi_az                   = false
  publicly_accessible        = false
  skip_final_snapshot        = true
  apply_immediately          = false
  
  # Performance Insights (opcional, puede aumentar costo mínimamente)
  enabled_cloudwatch_logs_exports = ["postgresql", "upgrade"]
  
  tags = {
    Name        = "${local.name}-postgres"
    Service     = "connectivity"
    Environment = var.environment
  }
  
  lifecycle {
    ignore_changes = [
      password,  # Never change password after creation
    ]
  }
}

# Actualiza secret con el host al tener endpoint
resource "aws_secretsmanager_secret_version" "rds_credentials_with_host" {
  secret_id = aws_secretsmanager_secret.rds_credentials.id
  secret_string = jsonencode({
    username = "appuser"
    password = random_password.db_password.result
    engine   = "postgres"
    host     = aws_db_instance.postgres.address
    port     = 5432
    dbname   = "connectivity_db"
  })
  
  depends_on = [aws_db_instance.postgres]
}

# ----------------------------------------------------------------------------
# Secret con cadenas de conexión (para la app y/o External Secrets)
# ----------------------------------------------------------------------------
resource "aws_secretsmanager_secret" "app_connections" {
  name        = "${local.name}/connections-${local.resource_suffix}"
  description = "App connections for ${local.name}"
  
  tags = {
    Name        = "${local.name}-connections"
    Service     = "connectivity"
    Environment = var.environment
  }
}

resource "aws_secretsmanager_secret_version" "app_connections" {
  secret_id     = aws_secretsmanager_secret.app_connections.id
  secret_string = jsonencode({
    DATABASE_URL = "postgresql://appuser:${random_password.db_password.result}@${aws_db_instance.postgres.address}:5432/connectivity_db"
    RABBITMQ_URL = local.rabbitmq_url
  })
  
  depends_on = [aws_db_instance.postgres]
}

# ----------------------------------------------------------------------------
# IAM para el servicio (IRSA) - acceso a estos secretos
# ----------------------------------------------------------------------------
data "aws_iam_policy_document" "service_policy" {
  statement {
    sid = "AllowSecretsAccess"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      aws_secretsmanager_secret.app.arn,
      aws_secretsmanager_secret.rds_credentials.arn,
      aws_secretsmanager_secret.app_connections.arn
    ]
  }
  
  statement {
    sid = "AllowCloudWatchLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = [
      "${aws_cloudwatch_log_group.connectivity.arn}:*"
    ]
  }
}

resource "aws_iam_policy" "service" {
  name        = "${local.name}-service-policy"
  description = "IAM policy for ${local.name} service"
  policy      = data.aws_iam_policy_document.service_policy.json
  
  tags = {
    Name        = "${local.name}-service-policy"
    Service     = "connectivity"
    Environment = var.environment
  }
  
  lifecycle {
    create_before_destroy = false
  }
}

# IRSA for connectivity service
module "irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.39"

  role_name        = "${local.name}-service-irsa"
  role_description = "IRSA role for ${local.name} service"

  oidc_providers = {
    main = {
      provider_arn               = local.oidc_provider_arn
      namespace_service_accounts = ["connectivity:connectivity-sa"]
    }
  }

  role_policy_arns = {
    service = aws_iam_policy.service.arn
  }
  
  tags = {
    Name        = "${local.name}-service-irsa"
    Service     = "connectivity"
    Environment = var.environment
  }
}

# ----------------------------------------------------------------------------
# IAM Policy para External Secrets -> acceso a los secretos de este micro
# (se adjunta al rol compartido del ESO que viene del shared)
# ----------------------------------------------------------------------------
data "aws_iam_policy_document" "external_secrets" {
  statement {
    sid     = "AllowExternalSecretsAccess"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret"
    ]
    resources = [
      aws_secretsmanager_secret.app.arn,
      aws_secretsmanager_secret.rds_credentials.arn,
      aws_secretsmanager_secret.app_connections.arn
    ]
  }
}

resource "aws_iam_policy" "external_secrets" {
  name        = "${local.name}-external-secrets-policy"
  description = "Allow External Secrets Operator to access ${local.name} secrets"
  policy      = data.aws_iam_policy_document.external_secrets.json
  
  tags = {
    Name        = "${local.name}-eso-policy"
    Service     = "connectivity"
    Environment = var.environment
  }
  
  lifecycle {
    create_before_destroy = false
  }
}

resource "aws_iam_role_policy_attachment" "eso_attach" {
  role       = data.terraform_remote_state.shared.outputs.eso_irsa_role_name
  policy_arn = aws_iam_policy.external_secrets.arn
}

# ============================================================================
# CloudWatch Log Group
# ============================================================================
resource "aws_cloudwatch_log_group" "connectivity" {
  name              = "/aws/eks/${var.environment}/connectivity-microservice"
  retention_in_days = 30

  tags = {
    Name        = "connectivity-logs"
    Service     = "connectivity"
    Environment = var.environment
  }
}

# ============================================================================
# Outputs - Only microservice-specific resources
# ============================================================================
output "rds_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = aws_db_instance.postgres.address
}

output "rds_port" {
  description = "RDS PostgreSQL port"
  value       = aws_db_instance.postgres.port
}

output "rds_database_name" {
  description = "RDS PostgreSQL database name"
  value       = aws_db_instance.postgres.db_name
}

output "rds_secret_arn" {
  description = "ARN of the RDS credentials secret"
  value       = aws_secretsmanager_secret.rds_credentials.arn
}

output "app_connections_secret_arn" {
  description = "ARN of the app connections secret (DATABASE_URL, RABBITMQ_URL)"
  value       = aws_secretsmanager_secret.app_connections.arn
}

output "app_secret_arn" {
  description = "ARN of the application configuration secret"
  value       = aws_secretsmanager_secret.app.arn
}

output "app_secret_name" {
  description = "Name of the application configuration secret"
  value       = aws_secretsmanager_secret.app.name
}

output "rds_secret_name" {
  description = "Name of the RDS credentials secret"
  value       = aws_secretsmanager_secret.rds_credentials.name
}

output "app_connections_secret_name" {
  description = "Name of the app connections secret"
  value       = aws_secretsmanager_secret.app_connections.name
}

output "rds_security_group_id" {
  description = "Security group ID for RDS PostgreSQL"
  value       = aws_security_group.rds.id
}

output "irsa_role_arn" {
  description = "ARN of the IRSA role for the connectivity service"
  value       = module.irsa.iam_role_arn
}

output "irsa_role_name" {
  description = "Name of the IRSA role for the connectivity service"
  value       = module.irsa.iam_role_name
}

output "cloudwatch_log_group_name" {
  description = "CloudWatch log group name for the connectivity service"
  value       = aws_cloudwatch_log_group.connectivity.name
}

# RabbitMQ (from shared infrastructure)
output "rabbitmq_amqp_url" {
  description = "RabbitMQ AMQP connection URL"
  value       = local.rabbitmq_url
  sensitive   = true
}

# Outputs from shared infrastructure (for convenience)
output "cluster_name" {
  description = "EKS cluster name"
  value       = local.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = data.terraform_remote_state.shared.outputs.cluster_endpoint
}

output "cluster_ca_certificate" {
  description = "EKS cluster CA certificate"
  value       = data.terraform_remote_state.shared.outputs.cluster_ca_certificate
  sensitive   = true
}

output "aws_lb_controller_role_arn" {
  description = "ARN of the AWS Load Balancer Controller IRSA role"
  value       = data.terraform_remote_state.shared.outputs.aws_load_balancer_controller_irsa_role_arn
}

output "vpc_id" {
  description = "VPC ID"
  value       = local.vpc_id
}