# Test 01 · DNA Synthesis — S3 bucket

## Inputs
| Input | Value |
| :--- | :--- |
| Intent | `intents/garage-serverless/prod.md` ([expected](intent.md)): only `spec.storage.blob` |
| Golden path | `platform/golden-paths/serverless-app/v1/synthesis.md` |
| Building block | `platform/golden-paths/_common/building-blocks/s3-bucket.md` |
| Output | `terraform/garage-serverless/` |

## Design Tokens (MCP `platform-context-engine`)
| Call | Values used |
| :--- | :--- |
| `read_design_tokens("governance", "prod")` | `naming_mask`, `default_tags` (merge of `_org` + `prod`) |
| `read_design_tokens("network", "prod")` | `aws_region` |
| `read_design_tokens("security", "prod")` | `kms_keys.storage_key_arn` |
| `read_design_tokens("storage", "prod")` | `s3.versioning_status`, `s3.force_destroy`, `s3.audit_log_target_bucket` |

`compute` is not read: no function and no API in this intent.

## Token -> Terraform map (prod)
| Terraform | Variable | Token | prod value |
| :--- | :--- | :--- | :--- |
| `aws_s3_bucket.bucket` | `local.name_prefix` + `-static-content` | `governance.naming_mask` + `blob.purpose` | `acme-prod-garage-serverless-static-content` |
| `aws_s3_bucket.force_destroy` | `s3_force_destroy` | `storage.s3.force_destroy` | `false` |
| `aws_s3_bucket_versioning.status` | `s3_versioning_status` | `storage.s3.versioning_status` | `Enabled` |
| `..._encryption_configuration.kms_master_key_id` | `storage_kms_key_arn` | `security.kms_keys.storage_key_arn` | `arn:aws:kms:eu-west-1:444455556666:key/prod-pci-storage-cmk` |
| `aws_s3_bucket_logging.target_bucket` | `audit_log_bucket` | `storage.s3.audit_log_target_bucket` | `acme-prod-security-audit-logs` |
| provider `default_tags` | `default_tags` | `governance.default_tags` | Organization, ManagedBy, Environment, CostCenter, ComplianceScope |
| provider `region` | `aws_region` | `network.aws_region` | `eu-west-1` |

## Resources (`s3.tf`): five, not one
| Resource | Guarantees |
| :--- | :--- |
| `aws_s3_bucket.static_content` | name from the naming mask, tags from the tokens |
| `aws_s3_bucket_public_access_block.static_content` | **private**: all four flags `true` |
| `aws_s3_bucket_versioning.static_content` | **versioned**: status from the token |
| `aws_s3_bucket_server_side_encryption_configuration.static_content` | **encrypted**: `aws:kms` with the approved storage key |
| `aws_s3_bucket_logging.static_content` | access logs to the security audit bucket |

No inline `versioning`, `server_side_encryption_configuration` or `logging` blocks on `aws_s3_bucket`: deprecated
since provider v4, and exactly what a model with an old training snapshot tends to write.

## Knowledge guards
- `terraform-knowledge-guard`: `search_providers` + `get_provider_details` for the five resource types at the
  version in `.terraform.lock.hcl` (5.x).
- `aws-knowledge-guard`: not needed (no runtime or regional choice).

## Validate
```bash
python3 platform/tools/export_tokens.py prod > build/tokens.prod.json
cd terraform/garage-serverless
terraform init && terraform plan -var-file=environments/prod.tfvars -out tfplan
terraform show -json tfplan > tfplan.json
conftest test tfplan.json -p ../../policy --data ../../build/tokens.prod.json
```
Expected: all policies pass (`policy/s3.rego`, `policy/tags.rego`).

### Fault injection for the live gate
Replace the approved key with the AWS-managed one, the most common model default:
```hcl
kms_master_key_id = "alias/aws/s3"
```
Expected deny, then Kiro regenerates from the message:
```
FAIL - aws_s3_bucket_server_side_encryption_configuration.static_content: KMS key alias/aws/s3 is not the
       approved storage key (token security.kms_keys.storage_key_arn)
```
Offline rehearsal, no AWS account: `tests/policy/fixtures/test01-deny-kms.tfplan.json`.

## Reference output
[`expected/terraform/garage-serverless/`](expected/terraform/garage-serverless/): the backup if the live
generation diverges.
