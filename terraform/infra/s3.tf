resource "aws_s3_bucket" "data_bucket" {
    bucket = "s3-${var.group_name}"
    force_destroy = true
}

resource "aws_s3_bucket_public_access_block" "block_public" {
    bucket = aws_s3_bucket.data_bucket.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}