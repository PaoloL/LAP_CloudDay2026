# Building block: S3 bucket

Used by: `ContainerService` and `ServerlessApplication` (`spec.storage.blob.enabled: true`).

Required resources:
- `aws_s3_bucket`, named after `naming_mask` with suffix equal to `blob.purpose`.
- `aws_s3_bucket_public_access_block` with all four flags set to `true`
  (`block_public_acls`, `block_public_policy`, `ignore_public_acls`, `restrict_public_buckets`).
- `aws_s3_bucket_server_side_encryption_configuration` with `sse_algorithm = "aws:kms"` and
  `kms_master_key_id` = token `security.kms_keys.storage_key_arn`.
- `aws_s3_bucket_versioning` with `status` = token `storage.s3.versioning_status`.
- `aws_s3_bucket_logging` to the bucket in token `storage.s3.audit_log_target_bucket`.

`force_destroy` = token `storage.s3.force_destroy`.
Do not use the deprecated inline blocks of `aws_s3_bucket` (versioning, encryption, logging): they belong in the
dedicated resources. Check the arguments with the `terraform-knowledge-guard` power.
