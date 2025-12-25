# API SERVICE
resource "aws_apprunner_service" "api_service" {
  service_name = "service-api-${var.group_name}"

  source_configuration {
    authentication_configuration {
      access_role_arn = data.aws_iam_role.app_runner_access_role.arn
    }

    image_repository {
      image_identifier      = "${data.aws_ecr_repository.api_repo.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "8000"
        runtime_environment_variables = {
          BUCKET_NAME = data.aws_s3_bucket.data_bucket.bucket
        }
      }
    }
    auto_deployments_enabled = true
  }

  instance_configuration {
    instance_role_arn = data.aws_iam_role.app_runner_instance_role.arn
  }
}

# FRONTEND SERVICE
resource "aws_apprunner_service" "frontend_service" {
  service_name = "service-frontend-${var.group_name}"

  source_configuration {
    authentication_configuration {
      access_role_arn = data.aws_iam_role.app_runner_access_role.arn
    }

    image_repository {
      image_identifier      = "${data.aws_ecr_repository.frontend_repo.repository_url}:latest"
      image_repository_type = "ECR"

      image_configuration {
        port = "7860"
        runtime_environment_variables = {
          # Inject the URL of the API created just above
          API_URL = "https://${aws_apprunner_service.api_service.service_url}"
        }
      }
    }
    auto_deployments_enabled = true
  }

  instance_configuration {
    instance_role_arn = data.aws_iam_role.app_runner_instance_role.arn
  }

  depends_on = [aws_apprunner_service.api_service]
}
