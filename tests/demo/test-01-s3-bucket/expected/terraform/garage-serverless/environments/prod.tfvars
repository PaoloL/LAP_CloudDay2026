# Written from read_design_tokens(environment = "prod"): governance, network, security, storage.
environment = "prod"
aws_region  = "eu-west-1"
naming_mask = "acme-{environment}-{service_name}-{resource_suffix}"

default_tags = {
  Organization    = "AcmeCorp"
  ManagedBy       = "Kiro-IaI"
  Environment     = "prod"
  CostCenter      = "Fleet-Core-Prod"
  ComplianceScope = "pci-dss"
}

storage_kms_key_arn  = "arn:aws:kms:eu-west-1:444455556666:key/prod-pci-storage-cmk"
s3_versioning_status = "Enabled"
s3_force_destroy     = false
audit_log_bucket     = "acme-prod-security-audit-logs"
