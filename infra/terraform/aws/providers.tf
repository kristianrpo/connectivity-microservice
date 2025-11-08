# ============================================================================
# Provider Configuration
# ============================================================================
# Note: terraform block with required_providers is in backend.tf

provider "aws" {
  region = var.aws_region
  
  default_tags {
    tags = {
      Project     = var.project
      Environment = var.environment
      ManagedBy   = "Terraform"
      Service     = "connectivity-microservice"
    }
  }
}
