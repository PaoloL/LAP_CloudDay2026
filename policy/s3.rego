# Every S3 bucket: private, versioned, encrypted with the approved key, logged.
# Expected values come from the Design Tokens (data.tokens): the same values that fed generation.
package main

import rego.v1

buckets := changed("aws_s3_bucket")

storage := data.tokens.storage.s3

storage_key := data.tokens.security.kms_keys.storage_key_arn

public_access_flags := ["block_public_acls", "block_public_policy", "ignore_public_acls", "restrict_public_buckets"]

# --- private ---------------------------------------------------------------------------------------
deny contains msg if {
	some b in buckets
	count(attached("aws_s3_bucket_public_access_block", b.address)) == 0
	msg := sprintf("%s: no aws_s3_bucket_public_access_block: the bucket is not guaranteed private", [b.address])
}

deny contains msg if {
	some b in buckets
	some pab in attached("aws_s3_bucket_public_access_block", b.address)
	some flag in public_access_flags
	object.get(pab.change.after, flag, false) != true
	msg := sprintf("%s: %s must be true", [pab.address, flag])
}

# --- versioned -------------------------------------------------------------------------------------
deny contains msg if {
	some b in buckets
	count(attached("aws_s3_bucket_versioning", b.address)) == 0
	msg := sprintf("%s: no aws_s3_bucket_versioning (token storage.s3.versioning_status = %s)", [b.address, storage.versioning_status])
}

deny contains msg if {
	some b in buckets
	some v in attached("aws_s3_bucket_versioning", b.address)
	some cfg in v.change.after.versioning_configuration
	cfg.status != storage.versioning_status
	msg := sprintf("%s: versioning %s, the token storage.s3.versioning_status requires %s", [v.address, cfg.status, storage.versioning_status])
}

# --- encrypted -------------------------------------------------------------------------------------
deny contains msg if {
	some b in buckets
	count(attached("aws_s3_bucket_server_side_encryption_configuration", b.address)) == 0
	msg := sprintf("%s: no aws_s3_bucket_server_side_encryption_configuration", [b.address])
}

deny contains msg if {
	some b in buckets
	some enc in attached("aws_s3_bucket_server_side_encryption_configuration", b.address)
	some rule in enc.change.after.rule
	some sse in rule.apply_server_side_encryption_by_default
	sse.sse_algorithm != "aws:kms"
	msg := sprintf("%s: sse_algorithm %s, aws:kms required", [enc.address, sse.sse_algorithm])
}

deny contains msg if {
	some b in buckets
	some enc in attached("aws_s3_bucket_server_side_encryption_configuration", b.address)
	some rule in enc.change.after.rule
	some sse in rule.apply_server_side_encryption_by_default
	sse.sse_algorithm == "aws:kms"
	sse.kms_master_key_id != storage_key
	msg := sprintf("%s: KMS key %v is not the approved storage key (token security.kms_keys.storage_key_arn)", [enc.address, sse.kms_master_key_id])
}

# --- logged ----------------------------------------------------------------------------------------
deny contains msg if {
	some b in buckets
	count(attached("aws_s3_bucket_logging", b.address)) == 0
	msg := sprintf("%s: no aws_s3_bucket_logging to %s", [b.address, storage.audit_log_target_bucket])
}

deny contains msg if {
	some b in buckets
	some l in attached("aws_s3_bucket_logging", b.address)
	l.change.after.target_bucket != storage.audit_log_target_bucket
	msg := sprintf("%s: access logs to %v, the token storage.s3.audit_log_target_bucket requires %s", [l.address, l.change.after.target_bucket, storage.audit_log_target_bucket])
}
