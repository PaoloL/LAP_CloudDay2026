# Test 04 · DNA Synthesis — HTTP API

## Inputs
| Input | Value |
| :--- | :--- |
| Intent | `intents/garage-serverless/prod.md` ([expected](intent.md)): adds `spec.exposure` and `spec.api` |
| Golden path | `platform/golden-paths/serverless-app/v1/synthesis.md` |
| Building block | `platform/golden-paths/_common/building-blocks/http-api-lambda.md` |
| Output | `terraform/garage-serverless/apigw.tf` (new); Test 01–03 files unchanged |

## Design Tokens
| Call | New values used |
| :--- | :--- |
| `read_design_tokens("compute", "prod", "serverless-app")` | `api.throttling_burst_limit`, `throttling_rate_limit`, `jwt_issuer`, `jwt_audience`, `access_log_retention_days` |

## Token -> Terraform map (prod)
| Terraform | Variable | Token | prod value |
| :--- | :--- | :--- | :--- |
| `aws_apigatewayv2_api.name` | `local.name_prefix` + `-api` | `governance.naming_mask` | `acme-prod-garage-serverless-api` |
| `aws_apigatewayv2_authorizer.jwt_configuration.issuer` | `api_jwt_issuer` | `compute.api.jwt_issuer` | `https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_AcmeProd01` |
| `aws_apigatewayv2_authorizer.jwt_configuration.audience` | `api_jwt_audience` | `compute.api.jwt_audience` | `["acme-api-clients-prod"]` |
| `aws_apigatewayv2_route.authorization_type` | from the intent | `spec.exposure: public` | `JWT` on all 15 routes |
| stage `throttling_burst_limit` / `rate_limit` | `api_throttling_*` | `compute.api.*` | `200` / `100` |
| access log group `retention_in_days` | `api_access_log_retention_days` | `compute.api.access_log_retention_days` | `365` |

## Resources (`apigw.tf`)
- `aws_apigatewayv2_api.main`, `aws_apigatewayv2_integration.lambda` (`AWS_PROXY`, payload `2.0`)
- `aws_apigatewayv2_authorizer.jwt`
- `aws_apigatewayv2_route.api` (`for_each` over the 15 routes of the intent, none extra)
- `aws_apigatewayv2_stage.default` with throttling and access logs, `aws_cloudwatch_log_group.apigw`
- `aws_lambda_permission.apigw` with `source_arn = "${aws_apigatewayv2_api.main.execution_arn}/*/*"`

## Knowledge guards
- `terraform-knowledge-guard`: the `aws_apigatewayv2_*` resources and `aws_lambda_permission` at provider 5.x.

## Validate
Expected: all policies pass, including `policy/apigw.rego`: no route with `authorization_type = "NONE"`.
