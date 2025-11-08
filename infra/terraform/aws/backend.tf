terraform {
  required_version = ">= 1.5.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = ">= 3.6"
    }
  }
  
  # Backend configuration will be provided via backend config file or CLI
  # Example usage: terraform init -backend-config=backend.hcl
  # backend.hcl should contain:
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "connectivity/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "terraform-state-lock" # optional but recommended
  backend "s3" {}
}
