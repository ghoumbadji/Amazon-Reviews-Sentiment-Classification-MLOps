terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket  = "terraform-state-g1mg05"
    key     = "prod/infra.tfstate"
    region  = "eu-west-3"
    encrypt = true
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = {
      Project   = "MLOps-Project"
      Group     = var.group_name
      ManagedBy = "Terraform-Infra"
    }
  }
}