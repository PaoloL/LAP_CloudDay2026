# Building block _common/building-blocks/s3-bucket.md · intent spec.storage.blob

resource "aws_s3_bucket" "static_content" {
  bucket        = "${local.name_prefix}-static-content" # naming mask + blob.purpose
  force_destroy = var.s3_force_destroy
}

resource "aws_s3_bucket_public_access_block" "static_content" {
  bucket                  = aws_s3_bucket.static_content.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "static_content" {
  bucket = aws_s3_bucket.static_content.id

  versioning_configuration {
    status = var.s3_versioning_status
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "static_content" {
  bucket = aws_s3_bucket.static_content.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm     = "aws:kms"
      kms_master_key_id = var.storage_kms_key_arn
    }
    bucket_key_enabled = true
  }
}

resource "aws_s3_bucket_logging" "static_content" {
  bucket        = aws_s3_bucket.static_content.id
  target_bucket = var.audit_log_bucket
  target_prefix = "s3/${local.name_prefix}-static-content/"
}
