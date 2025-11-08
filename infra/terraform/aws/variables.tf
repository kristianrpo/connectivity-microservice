# ============================================================================
# Terraform Backend Variables
# ============================================================================

variable "tf_backend_bucket" {
  description = "S3 bucket name for Terraform remote state"
  type        = string
}

variable "aws_region" {
  description = "AWS region for resources"
  type        = string
  default     = "us-east-1"
}

# ============================================================================
# Shared Infrastructure Variables
# ============================================================================

variable "shared_state_key" {
  description = "S3 key for shared infrastructure Terraform state"
  type        = string
  default     = "shared/infra/terraform/aws/terraform.tfstate"
}

# ============================================================================
# Project Variables
# ============================================================================

variable "project" {
  description = "Project name"
  type        = string
  default     = "connectivity"
}

variable "environment" {
  description = "Environment name (dev, staging, production)"
  type        = string
  default     = "production"
}

# ============================================================================
# Database Variables
# ============================================================================

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "Allocated storage for RDS in GB"
  type        = number
  default     = 20
}

variable "db_engine_version" {
  description = "PostgreSQL engine version"
  type        = string
  default     = "16.3"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "connectivity_db"
}

variable "db_username" {
  description = "Database master username"
  type        = string
  default     = "connectivity_admin"
}

variable "db_backup_retention_period" {
  description = "Number of days to retain backups"
  type        = number
  default     = 7
}

variable "db_multi_az" {
  description = "Enable Multi-AZ deployment for RDS"
  type        = bool
  default     = false
}

# ============================================================================
# Application Variables
# ============================================================================

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 8000
}

variable "app_replicas" {
  description = "Number of application replicas"
  type        = number
  default     = 2
}

# ============================================================================
# Tags
# ============================================================================

variable "tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "connectivity"
    ManagedBy   = "Terraform"
    Microservice = "connectivity"
  }
}
