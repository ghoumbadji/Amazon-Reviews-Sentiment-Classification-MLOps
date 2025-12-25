# Retrieve the bucket created by Infra
data "aws_s3_bucket" "data_bucket" {
  bucket = "s3-${var.group_name}"
}

# Retrieve the ECR repositories created by Infra
data "aws_ecr_repository" "api_repo" {
  name = "ecr-${var.group_name}-api"
}

data "aws_ecr_repository" "frontend_repo" {
  name = "ecr-${var.group_name}-frontend"
}

# Retrieve the IAM roles created by Infra.
data "aws_iam_role" "app_runner_access_role" {
  name = "AppRunnerECRAccessRole-${var.group_name}"
}

data "aws_iam_role" "app_runner_instance_role" {
  name = "AppRunnerInstanceRole-${var.group_name}"
}
