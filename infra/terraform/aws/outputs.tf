# ============================================================================
# Outputs
# ============================================================================

# Cluster Information
output "cluster_name" {
  description = "EKS cluster name from shared infrastructure"
  value       = local.cluster_name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint from shared infrastructure"
  value       = data.terraform_remote_state.shared.outputs.cluster_endpoint
}

output "cluster_ca_certificate" {
  description = "EKS cluster CA certificate from shared infrastructure"
  value       = data.terraform_remote_state.shared.outputs.cluster_ca_certificate
  sensitive   = true
}

# Database Outputs
output "rds_endpoint" {
  description = "RDS instance endpoint"
  value       = try(aws_db_instance.postgres.endpoint, "")
}

output "rds_secret_arn" {
  description = "ARN of the RDS credentials secret"
  value       = try(aws_secretsmanager_secret.rds_credentials.arn, "")
}

# RabbitMQ Outputs
output "rabbitmq_amqp_url" {
  description = "RabbitMQ AMQP URL from shared infrastructure"
  value       = local.rabbitmq_url
  sensitive   = true
}

# Secrets Manager Outputs
output "secretsmanager_secret_name" {
  description = "Name of the Secrets Manager secret for application"
  value       = try(aws_secretsmanager_secret.app.name, "")
}

output "secretsmanager_secret_arn" {
  description = "ARN of the Secrets Manager secret for application"
  value       = try(aws_secretsmanager_secret.app.arn, "")
}

# IAM Outputs
output "irsa_role_arn" {
  description = "ARN of the IRSA role for the application"
  value       = try(module.irsa.iam_role_arn, "")
}

# Network Outputs
output "vpc_id" {
  description = "VPC ID from shared infrastructure"
  value       = local.vpc_id
}

output "private_subnet_ids" {
  description = "Private subnet IDs from shared infrastructure"
  value       = local.private_subnet_ids
}
