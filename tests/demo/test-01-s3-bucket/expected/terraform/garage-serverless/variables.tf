# One variable per Design Token. Values: environments/<env>.tfvars, written from read_design_tokens.

variable "environment" {
  description = "Intent metadata.environment"
  type        = string
}

variable "aws_region" {
  description = "Token network.aws_region"
  type        = string
}

variable "naming_mask" {
  description = "Token governance.naming_mask"
  type        = string
}

variable "default_tags" {
  description = "Token governance.default_tags (merge of _org and environment)"
  type        = map(string)
}

variable "storage_kms_key_arn" {
  description = "Token security.kms_keys.storage_key_arn"
  type        = string
}

variable "s3_versioning_status" {
  description = "Token storage.s3.versioning_status"
  type        = string

  validation {
    condition     = contains(["Enabled", "Suspended"], var.s3_versioning_status)
    error_message = "s3_versioning_status must be Enabled or Suspended."
  }
}

variable "s3_force_destroy" {
  description = "Token storage.s3.force_destroy"
  type        = bool
}

variable "audit_log_bucket" {
  description = "Token storage.s3.audit_log_target_bucket"
  type        = string
}
