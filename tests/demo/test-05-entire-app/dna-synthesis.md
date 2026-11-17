# Test 05 · DNA Synthesis — the entire application in one prompt

## Inputs
| Input | Value |
| :--- | :--- |
| Intent | `intents/garage-serverless/prod.md` ([expected](intent.md)): all components in one step |
| Golden path | `platform/golden-paths/serverless-app/v1/synthesis.md` |
| Building blocks | `s3-bucket.md`, `dynamodb-table.md`, `lambda-function.md`, `http-api-lambda.md` |
| Output | `terraform/garage-serverless/` from a clean state |

## The property this test proves
**Same contract, same result, whatever the path.**
- The intent frontmatter is identical to the one built step by step in Tests 01–04
  (`python3 tests/demo/check.py` compares them).
- The generated files are the same as Tests 01–04 together:

| File | Component | Test |
| :--- | :--- | :--- |
| `versions.tf`, `variables.tf`, `locals.tf`, `outputs.tf`, `environments/prod.tfvars` | common | 01 |
| `s3.tf` | `spec.storage.blob` | 01 |
| `dynamodb.tf` | `spec.storage.nosql` | 02 |
| `lambda.tf` | `spec.function` | 03 |
| `apigw.tf` | `spec.exposure` + `spec.api` | 04 |

## Design Tokens
All five domains for `prod`: `governance`, `network`, `security`, `storage`, `compute` (`serverless-app`).
The values are the ones listed in the DNA synthesis of Tests 01–04.

## Knowledge guards
The union of Tests 01–04: provider documentation for every resource type, Lambda runtime support.

## Validate
Expected: all policies pass (`policy/s3.rego`, `tags.rego`, `dynamodb.rego`, `lambda.rego`, `apigw.rego`).
