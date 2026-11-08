output "api_endpoint" {
  value = aws_apigatewayv2_api.main.api_endpoint
}

output "photos_bucket_name" {
  value = aws_s3_bucket.photos.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.primary.name
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}
