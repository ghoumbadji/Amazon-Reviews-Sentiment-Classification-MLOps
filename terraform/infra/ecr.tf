resource "aws_ecr_repository" "api_repo" {
  name         = "ecr-api-${var.group_name}"
  force_delete = true
}

resource "aws_ecr_repository" "frontend_repo" {
  name         = "ecr-frontend-${var.group_name}"
  force_delete = true
}