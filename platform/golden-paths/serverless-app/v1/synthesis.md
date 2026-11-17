# Synthesis: ServerlessApplication v1 (Lambda, HTTP API, DynamoDB, S3)

Applies to intents with `apiVersion: intent.acme.io/v1`, `kind: ServerlessApplication`.
The common rules in `.kiro/steering/01-phase1-synthesis.md` also apply.

## Tokens to read (`read_design_tokens`, environment = `metadata.environment`)
| Domain | kind | Use | When |
| :--- | :--- | :--- | :--- |
| `governance` | | naming mask, tags | always |
| `network` | | `aws_region` only: the function does not run in a VPC | always |
| `security` | | KMS keys, deletion protection | always |
| `storage` | | S3 and DynamoDB settings | `storage.blob` or `storage.nosql` enabled |
| `compute` | `serverless-app` | Lambda runtime, architecture, memory, timeout, tracing, logs; API throttling and JWT issuer | `function` or `api` enabled |

## Runtime checks before writing
- `compute.function.runtime` is supported by Lambda and not deprecated: `aws-knowledge-guard` power.
- Arguments of every resource type at the project's provider version: `terraform-knowledge-guard` power.

## Components
Each component generates resources only if it is present and enabled. Absent means disabled.

| Intent | Building block | File |
| :--- | :--- | :--- |
| `spec.storage.blob` | `_common/building-blocks/s3-bucket.md` | `s3.tf` |
| `spec.storage.nosql` | `_common/building-blocks/dynamodb-table.md` | `dynamodb.tf` |
| `spec.function` | `_common/building-blocks/lambda-function.md` | `lambda.tf` |
| `spec.api` (`type: http`) | `_common/building-blocks/http-api-lambda.md` | `apigw.tf` |

## Common files
- `versions.tf`: `hashicorp/aws ~> 5.0`; provider with `region = var.aws_region` and `default_tags { tags = var.default_tags }`.
- `variables.tf`: one variable for each token used, with no default for environment values.
- `locals.tf`: `service_name` = `metadata.name`; `name_prefix` = the `naming_mask` without `-{resource_suffix}`.
  Nothing environment-specific.
- `environments/<env>.tfvars`: the token values, written from `read_design_tokens`.
- `outputs.tf`: names and ARNs of the generated resources.

## Additive changes
When the intent gains a component, add its file and the variables it needs; do not rewrite the files of the
other components. The same intent, written in one step or in several, must produce the same files.

## Exposure (semantic security)
The intent says who calls the API, never how to authenticate:
- `exposure: public` -> JWT authorizer with issuer and audience from the tokens, on every route;
- `exposure: internal` -> `AWS_IAM` authorization on every route.
No route is ever generated with `authorization_type = "NONE"`.

## Output folder
`terraform/<metadata.name>/`, with per-environment values in `terraform/<metadata.name>/environments/<env>.tfvars`.
