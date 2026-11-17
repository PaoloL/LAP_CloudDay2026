output "static_content_bucket_name" {
  value = aws_s3_bucket.static_content.bucket
}

output "static_content_bucket_arn" {
  value = aws_s3_bucket.static_content.arn
}
