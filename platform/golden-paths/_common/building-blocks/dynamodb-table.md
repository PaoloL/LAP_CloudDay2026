# Building block: DynamoDB table

Used by: `ContainerService` and `ServerlessApplication` (`spec.storage.nosql.enabled: true`).

- `aws_dynamodb_table` named after `naming_mask` with suffix `table_name`.
- `billing_mode` = token `storage.dynamodb.billing_mode` (always `PAY_PER_REQUEST`).
- `hash_key` = `partition_key`, `range_key` = `sort_key` when not empty; attributes of type `S`.
- `server_side_encryption { enabled = true, kms_key_arn = <security.kms_keys.database_key_arn> }`.
- `point_in_time_recovery { enabled = <storage.dynamodb.point_in_time_recovery> }`.
- `deletion_protection_enabled` = token `security.enable_deletion_protection`.
