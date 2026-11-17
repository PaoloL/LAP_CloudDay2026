# Building block: Lambda function (CRUD on entities)

Used by: `ServerlessApplication` (`spec.function.enabled: true`). Requires `spec.storage.nosql.enabled: true`.

Required resources:
- `aws_lambda_function` named after `naming_mask` with suffix `api`:
  - `runtime`, `architectures`, `timeout` from tokens `compute.function.*`;
  - `memory_size` = token `compute.function.memory_mb[spec.function.size]`;
  - `filename` and `source_code_hash` from the variable `function_package` (path of the zip built by the
    service team): the application code is not generated here;
  - `handler` from the variable `function_handler` (default `app.handler`);
  - `environment.variables`: `TABLE_NAME` = the DynamoDB table name, `ENTITIES` = `spec.function.entities`
    joined with commas;
  - `tracing_config.mode` = token `compute.function.tracing_mode`.
- `aws_cloudwatch_log_group` `/aws/lambda/<function name>` with retention = token `compute.function.log_retention_days`.
- `aws_iam_role` for `lambda.amazonaws.com` with an inline policy of least privilege:
  - `logs:CreateLogStream`, `logs:PutLogEvents` on the log group only;
  - `dynamodb:GetItem`, `PutItem`, `UpdateItem`, `DeleteItem`, `Query` on the table ARN only;
  - `kms:Decrypt`, `kms:GenerateDataKey` on token `security.kms_keys.database_key_arn` only;
  - `xray:PutTraceSegments`, `xray:PutTelemetryRecords` (these actions do not support resource-level
    permissions: `Resource = "*"` is allowed here and only here).

The function does not run in a VPC and has no access to the S3 bucket unless the intent asks for it.
Single-table design: one item type per entity, partition key `<ENTITY>#<id>`.
