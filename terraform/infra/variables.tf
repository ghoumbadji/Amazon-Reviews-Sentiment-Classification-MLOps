variable "aws_region" {
  description = "AWS Region"
  default     = "eu-west-3"  # Paris
}

variable "group_name" {
  description = "Group identifier"
  type        = string
}
