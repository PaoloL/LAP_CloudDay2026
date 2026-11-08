resource "aws_dynamodb_table" "primary" {
  name         = "${local.name_prefix}-primary"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "PK"
  range_key    = "SK"

  attribute {
    name = "PK"
    type = "S"
  }

  attribute {
    name = "SK"
    type = "S"
  }

  server_side_encryption {
    enabled     = true
    kms_key_arn = local.database_key_arn
  }

  point_in_time_recovery {
    enabled = true
  }

  deletion_protection_enabled = true
}
