resource "aws_cloudwatch_dashboard" "main" {
  dashboard_name = "MLOps-Dashboard-${var.group_name}"

  dashboard_body = jsonencode({
    # Widget 1 : API Requests
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            [
              "AWS/AppRunner",
              "Requests",
              "ServiceName",
              "service-api-${var.group_name}",
              "ServiceID",
              aws_apprunner_service.api_service.service_id
            ]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "API Requests Count"
        }
      },
      # Widget 2 : API Resources
      {
        type   = "metric"
        x      = 12
        y      = 0
        width  = 12
        height = 6
        properties = {
          metrics = [
            # Memory on the left axis (default)
            [
              "AWS/AppRunner",
              "MemoryUtilization",
              "ServiceName",
              "service-api-${var.group_name}",
              "ServiceID",
              aws_apprunner_service.api_service.service_id,
              { "label" : "Memory (MB)" }
            ],
            # CPU on the right axis
            [
              "AWS/AppRunner",
              "CPUUtilization",
              "ServiceName",
              "service-api-${var.group_name}",
              "ServiceID",
              aws_apprunner_service.api_service.service_id,
              { "yAxis" : "right", "label" : "CPU (%)" }
            ]
          ]
          period = 300
          stat   = "Average"
          region = var.aws_region
          title  = "API Resources (CPU & RAM)"
          view   = "timeSeries"
        }
      },
      # Widget 3 : Frontend Traffic
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6
        properties = {
          metrics = [
            [
              "AWS/AppRunner",
              "Requests",
              "ServiceName",
              "service-frontend-${var.group_name}",
              "ServiceID",
              aws_apprunner_service.frontend_service.service_id,
              { "color" : "#ff7f0e" }
            ]
          ]
          period = 300
          stat   = "Sum"
          region = var.aws_region
          title  = "Frontend Traffic"
        }
      }
    ]
  })
}
