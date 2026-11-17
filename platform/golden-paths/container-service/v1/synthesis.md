# Synthesis: ContainerService v1 (ECS Fargate)

Applies to intents with `apiVersion: intent.acme.io/v1`, `kind: ContainerService`.
The common rules in `.kiro/steering/01-phase1-synthesis.md` also apply.

## Tokens to read (`read_design_tokens`, environment = `metadata.environment`)
| Domain | kind | Use |
| :--- | :--- | :--- |
| `network` | | region, VPC, subnets per tier and AZ |
| `security` | | KMS keys, TLS policy, deletion protection |
| `storage` | | S3 and DynamoDB settings |
| `governance` | | naming mask, tags |
| `compute` | `container-service` | Fargate profiles, desired_count, assign_public_ip |

## Resources
ECS Fargate (always):
- `aws_ecs_cluster`, `aws_ecs_task_definition` (`requires_compatibilities = ["FARGATE"]`, `network_mode = "awsvpc"`),
  `aws_ecs_service` (`launch_type = "FARGATE"`).
- Task `cpu`/`memory` = `fargate_profiles[spec.compute.size]`; `desired_count` from the tokens.
- The service uses ONLY the subnets of the `private_app` tier (all AZs) with `assign_public_ip = false`.
- Container port = `spec.compute.port`.
- Separate IAM roles for task execution and task; dedicated CloudWatch log group.

Ingress:
- Internal ALB (`internal = true`) on the `private_app` subnets, HTTPS listener with `ssl_policy` = token
  `security.tls_policy`, target group of type `ip` on the container port.
- If `spec.api.type: http`: building block `_common/building-blocks/http-api.md`.
- `spec.exposure: public` makes only the HTTP API public; the ALB and the tasks stay private.

Storage:
- `spec.storage.nosql.enabled: true` -> `_common/building-blocks/dynamodb-table.md`.
- `spec.storage.blob.enabled: true` -> `_common/building-blocks/s3-bucket.md`.
- Disabled components generate no resources.

## Output folder
`terraform/<metadata.name>/`, with per-environment values in `terraform/<metadata.name>/environments/<env>.tfvars`.
