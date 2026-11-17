# Test 02 · DNA Synthesis — DynamoDB table

## Inputs
| Input | Value |
| :--- | :--- |
| Intent | `intents/garage-serverless/prod.md` ([expected](intent.md)): adds `spec.storage.nosql` |
| Golden path | `platform/golden-paths/serverless-app/v1/synthesis.md` |
| Building block | `platform/golden-paths/_common/building-blocks/dynamodb-table.md` |
| Output | `terraform/garage-serverless/dynamodb.tf` (new); Test 01 files unchanged |

## Design Tokens
| Call | New values used |
| :--- | :--- |
| `read_design_tokens("storage", "prod")` | `dynamodb.billing_mode`, `dynamodb.point_in_time_recovery` |
| `read_design_tokens("security", "prod")` | `kms_keys.database_key_arn`, `enable_deletion_protection` |

## Token -> Terraform map (prod)
| Terraform | Variable | Token | prod value |
| :--- | :--- | :--- | :--- |
| `aws_dynamodb_table.name` | `local.name_prefix` + `-primary` | `governance.naming_mask` + `nosql.table_name` | `acme-prod-garage-serverless-primary` |
| `billing_mode` | `dynamodb_billing_mode` | `storage.dynamodb.billing_mode` | `PAY_PER_REQUEST` |
| `hash_key` / `range_key` | from the intent | `nosql.partition_key` / `sort_key` | `PK` / `SK` |
| `server_side_encryption.kms_key_arn` | `database_kms_key_arn` | `security.kms_keys.database_key_arn` | `arn:aws:kms:eu-west-1:444455556666:key/prod-pci-database-cmk` |
| `point_in_time_recovery.enabled` | `dynamodb_pitr_enabled` | `storage.dynamodb.point_in_time_recovery` | `true` |
| `deletion_protection_enabled` | `enable_deletion_protection` | `security.enable_deletion_protection` | `true` |

## Resources (`dynamodb.tf`)
- `aws_dynamodb_table.primary`: attributes `PK` and `SK` of type `S`, single-table design for garages, bikes and cars.

## Knowledge guards
- `terraform-knowledge-guard`: `aws_dynamodb_table` at provider 5.x.

## Validate
Expected: all policies pass, including `policy/dynamodb.rego` (database key, PITR and deletion protection as in the tokens).
