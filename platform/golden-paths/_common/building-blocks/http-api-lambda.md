# Building block: HTTP API with Lambda integration

Used by: `ServerlessApplication` (`spec.api.type: http`). Requires `spec.function.enabled: true`.

Required resources:
- `aws_apigatewayv2_api` with `protocol_type = "HTTP"`, named after `naming_mask` with suffix `api`.
- `aws_apigatewayv2_integration` of type `AWS_PROXY` to the function, `payload_format_version = "2.0"`.
- Authorization, from `spec.exposure` (never `NONE`):
  - `public`: one `aws_apigatewayv2_authorizer` of type `JWT` with `issuer` = token `compute.api.jwt_issuer`
    and `audience` = token `compute.api.jwt_audience`; every route uses `authorization_type = "JWT"`;
  - `internal`: every route uses `authorization_type = "AWS_IAM"`.
- One `aws_apigatewayv2_route` for each item of `spec.api.routes`, same method and path, none extra.
- `aws_apigatewayv2_stage` `$default` with `auto_deploy = true`, `default_route_settings` throttling from tokens
  `compute.api.throttling_burst_limit` and `throttling_rate_limit`, access logs to a dedicated
  `aws_cloudwatch_log_group` (retention = token `compute.api.access_log_retention_days`).
- `aws_lambda_permission` for `apigateway.amazonaws.com`, with `source_arn` limited to this API
  (`<execution_arn>/*/*`).
