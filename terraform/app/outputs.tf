output "api_url" {
  description = "The public URL of the API"
  value       = "https://${aws_apprunner_service.api_service.service_url}"
}

output "frontend_url" {
  description = "The public URL of the frontend (Gradio)"
  value       = "https://${aws_apprunner_service.frontend_service.service_url}"
}
