output "s3_bucket_name" {
  value = aws_s3_bucket.data_bucket.bucket
}

output "ecr_api_repo_url" {
  value = aws_ecr_repository.api_repo.repository_url
}

output "ecr_frontend_repo_url" {
  value = aws_ecr_repository.frontend_repo.repository_url
}
