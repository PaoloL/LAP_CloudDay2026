# Building block: private HTTP API through a VPC link

Used by: `ContainerService` (`spec.api.type: http`).

- `aws_apigatewayv2_api` with `protocol_type = "HTTP"`.
- `aws_apigatewayv2_vpc_link` on the subnets of the `private_app` tier (all AZs) from the `network` tokens.
- `aws_apigatewayv2_integration` of type `HTTP_PROXY` with `connection_type = "VPC_LINK"` to the listener of the
  internal ALB, with TLS verified against the certificate name.
- One `aws_apigatewayv2_route` for each item of `spec.api.routes`, same method and path, none extra.
- `aws_apigatewayv2_stage` `$default` with `auto_deploy` and access logs to CloudWatch
  (retention from the `log_retention_days` variable).
