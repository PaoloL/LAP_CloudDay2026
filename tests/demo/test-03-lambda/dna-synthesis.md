# Test 03 · DNA Synthesis — Lambda function (CRUD on garages, bikes, cars)

## Inputs
| Input | Value |
| :--- | :--- |
| Intent | `intents/garage-serverless/prod.md` ([expected](intent.md)): adds `spec.function` |
| Golden path | `platform/golden-paths/serverless-app/v1/synthesis.md` |
| Building block | `platform/golden-paths/_common/building-blocks/lambda-function.md` |
| Output | `terraform/garage-serverless/lambda.tf` (new); Test 01–02 files unchanged |

## Design Tokens
| Call | New values used |
| :--- | :--- |
| `read_design_tokens("compute", "prod", "serverless-app")` | `function.runtime`, `architecture`, `timeout_seconds`, `memory_mb.small`, `tracing_mode`, `log_retention_days` |

## Token -> Terraform map (prod)
| Terraform | Variable | Token | prod value |
| :--- | :--- | :--- | :--- |
| `aws_lambda_function.function_name` | `local.name_prefix` + `-api` | `governance.naming_mask` | `acme-prod-garage-serverless-api` |
| `runtime` | `lambda_runtime` | `compute.function.runtime` | `python3.13` |
| `architectures` | `lambda_architecture` | `compute.function.architecture` | `["arm64"]` |
| `memory_size` | `lambda_memory_mb` | `compute.function.memory_mb[spec.function.size]` | `256` (small) |
| `timeout` | `lambda_timeout_seconds` | `compute.function.timeout_seconds` | `10` |
| `tracing_config.mode` | `lambda_tracing_mode` | `compute.function.tracing_mode` | `Active` |
| log group `retention_in_days` | `lambda_log_retention_days` | `compute.function.log_retention_days` | `365` |
| `environment.variables` | from the intent | `function.entities`, table name | `ENTITIES = "garages,bikes,cars"`, `TABLE_NAME` |
| `filename`, `source_code_hash` | `function_package` | none: built by the service team | (no default) |

## Resources (`lambda.tf`)
- `aws_lambda_function.api`, `aws_cloudwatch_log_group.api`
- `aws_iam_role.api` (`lambda.amazonaws.com`) and `aws_iam_role_policy.api`: logs on the log group, CRUD on the
  table ARN, `kms:Decrypt`/`GenerateDataKey` on the database key, X-Ray (the only `Resource = "*"`).

## Knowledge guards
- `aws-knowledge-guard`: `python3.13` is a supported Lambda runtime and not deprecated (cite the page and date).
- `terraform-knowledge-guard`: `aws_lambda_function`, `aws_iam_role`, `aws_iam_role_policy`, `aws_cloudwatch_log_group`.

## Validate
Expected: all policies pass, including `policy/lambda.rego` (runtime, architecture and tracing as in the tokens).
Not visible to the gate: the IAM policy document references the table ARN, unknown at plan time, so the JSON of
the policy is unknown too. Least privilege here is enforced by the building block and by review.
