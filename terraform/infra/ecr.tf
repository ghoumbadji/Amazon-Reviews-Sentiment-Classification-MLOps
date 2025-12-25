resource "aws_ecr_repository" "api_repo" {
    name = "ecr-${var.group_name}-api"
    force_delete = true
}

resource "aws_ecr_repository" "frontend_repo" {
    name = "ecr-${var.group_name}-frontend"
    force_delete = true
}