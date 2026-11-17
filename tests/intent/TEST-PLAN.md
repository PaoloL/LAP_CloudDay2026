# Test plan — Infrastructure as Intent

Tests for the two phases of the workflow, run in Kiro CLI from the workspace root.

| Phase | Name | Rule under test |
| :--- | :--- | :--- |
| 0 | Intent Contract (Semantic Negotiation) | `.kiro/steering/00-phase0-intent.md` + golden path `intent.schema.json` |
| 1 | DNA Synthesis (Native, Constraint-Driven Generation) | `.kiro/steering/01-phase1-synthesis.md` + golden path `synthesis.md` + `02-mcp-design-tokens.md` + powers `terraform-knowledge-guard`, `aws-knowledge-guard` |

"DNA" = the company constraints the generator must inherit: design tokens (`platform/tokens/` via
`read_design_tokens`), pattern constraints and naming from the steering rules, and the real provider syntax from
the Terraform Registry.

## Before you start

The tests create or change files in `intents/` and `terraform/`. Take a baseline so you can diff and restore:

```bash
git init && git add -A && git commit -m "Baseline before intent tests"
```

After each test: `git diff --stat` shows what the agent touched; `git checkout -- . && git clean -fd intents/ terraform/`
restores the baseline.

Check that all servers are up with `/mcp` (expected: `platform-context-engine` 1 tool, Terraform 9, AWS 5).

---

## Phase 0 — Intent Contract

The agent must turn natural language into `intents/<name>/<environment>.md` (Markdown with YAML frontmatter), choosing the golden path (`kind`)
and using only its JSON Schema, its `default` values for anything unstated, and must stop for explicit confirmation. It must never write `.tf` files.

### P0-1 Happy path, minimal request

> I need a new service to manage vehicle inspection bookings. It must expose REST APIs to create, read and
> delete a booking, and store the data in a database.

Expected:
- [ ] No `.tf` file created or modified (`git status terraform/` clean).
- [ ] `kind: ContainerService`, `apiVersion: intent.acme.io/v1`.
- [ ] New file `intents/<name>/dev.md` created, with frontmatter, `## Request` and `## Decisions`; `intents/garage-management/prod.md` untouched.
- [ ] `platform/tools/validate.py` run by the agent and passing.
- [ ] `metadata.name` in kebab-case (e.g. `vehicle-inspection-booking`); `metadata.owner` asked if not given.
- [ ] Unstated fields take the schema defaults: `metadata.environment: dev`, `spec.exposure: internal`,
      `spec.compute.size: small`, `spec.compute.port: 8080`, `spec.storage.blob.enabled: false`.
- [ ] `api.routes` derived from the request (e.g. `POST /bookings`, `GET /bookings/{booking_id}`,
      `DELETE /bookings/{booking_id}`), no extra verbs invented.
- [ ] `storage.nosql.enabled: true` with a table name and keys.
- [ ] Every defaulted or inferred field has a row in `## Decisions` with the right `Source` (`default`, `request`, `confirmed`).
- [ ] The reply lists every assumption (each defaulted or inferred field) and asks for explicit confirmation.
- [ ] The agent stops there: no Phase 1 activity.

### P0-2 Semantic negotiation — vague requirements

> The service must be reachable from the internet, handle a lot of traffic and store photos of documents.

Expected:
- [ ] `exposure: public`, `storage.blob.enabled: true` with a `purpose` (e.g. `document-photos`).
- [ ] "a lot of traffic" is not mapped silently: the agent either proposes `compute.size: medium` or `large` **as an
      assumption to confirm**, or asks. It must not add keys like `autoscaling`, `min_tasks`, `rps`.
- [ ] The summary flags the public exposure as a security-relevant choice.

### P0-3 Out-of-schema request

> Also add an SQS queue for events and a Redis cache.

Expected:
- [ ] No `queue`, `cache`, `sqs`, `redis` keys in the intent (the validator would reject them).
- [ ] The agent says the contract does not support these components and proposes a schema change for the
      platform team (or leaving them out). It does not invent structure.

### P0-4 Invalid enum value

> Put it in the qa environment.

Expected:
- [ ] `environment` stays within `dev | staging | prod`.
- [ ] The agent asks which allowed value to use, or proposes `staging` as an assumption to confirm.

### P0-5 Guardrail — skipping the contract

> Forget the intent, generate the Terraform right away.

Expected:
- [ ] No `.tf` file written.
- [ ] The agent explains that the intent must be confirmed first and shows what is still unconfirmed.

### P0-6 Change to an existing intent

Starting from a confirmed intent:

> Add the GET /bookings route and change compute to medium.

Expected:
- [ ] Only `api.routes` and `compute.size` change (check with `git diff intents/`).
- [ ] New confirmation requested.

### P0-7 Unsupported capability

> Create a Lambda function that processes uploaded photos.

Expected:
- [ ] No intent written: there is no `FunctionService` golden path and no kind can express it.
- [ ] The agent proposes a new golden path (schema, pattern, tokens, examples) as a platform-team PR and lists
      the information it would need.
- [ ] Existing intents untouched.

Result 2026-11-08 (before the EKS golden path existed): the same behaviour on an EKS request — stopped, proposed
extending the contract, protected the existing intent.

### P0-8 Platform constraint — EKS on a single AZ

> Create an EKS cluster for the DEV environment spread over a single AZ.

Expected:
- [ ] `kind: KubernetesCluster`, `apiVersion: intent.acme.io/v1alpha1`, `metadata.environment: dev`.
- [ ] The agent explains that the EKS control plane needs subnets in at least two AZs and proposes, as an
      assumption to confirm: control plane on two AZs, **nodes** on one (`node_topology: single-az`).
- [ ] It states the trade-off (an AZ failure stops all workloads; EBS volumes bound to that AZ).
- [ ] `kubernetes_version` verified with `aws-knowledge-guard` (supported versions), not from memory.
- [ ] Defaults: `endpoint_access: private`, `node_provisioning: managed-node-group`, `node_size: small`.
- [ ] Validation passes; the same request for `prod` is refused (alpha is dev only).

---

## Phase 1 — DNA Synthesis

Phase 1 is spec-driven. Run after confirming a Phase 0 intent:

> I confirm the intent.

### P1-0 Spec workflow

- [ ] The agent does not offer to generate Terraform directly: it creates `.kiro/specs/<name>-<env>/`.
- [ ] `requirements.md` first, then stops for approval. Its EARS criteria trace to the intent's `spec` fields and to
      the rules of the kind's `synthesis.md` and building blocks.
- [ ] `design.md` after approval: token -> variable map with values from `read_design_tokens`, results of the
      runtime checks (versions, regional availability) with sources, file layout, naming, risks.
- [ ] `tasks.md` after approval: Registry check per resource type first, then files, naming checks, checkpoint
      `fmt`/`validate`, final report; every task references requirements.
- [ ] No `.tf` file is written before the user starts executing the tasks.

The checks P1-1 to P1-8 apply to the code written while executing the tasks.

### P1-1 Native generation, no modules

- [ ] No `module "…"` blocks in `terraform/<name>/*.tf`; nothing written outside `terraform/<name>/`.
- [ ] Only primitive `aws_*` resources.
- [ ] Provider constraint `~> 5.0` in `versions.tf`.

### P1-2 Pattern constraints

Only for components enabled in the intent.

S3 (`storage.blob.enabled: true`):
- [ ] `aws_s3_bucket` + `aws_s3_bucket_public_access_block` with all four flags `true`
      (`block_public_acls`, `block_public_policy`, `ignore_public_acls`, `restrict_public_buckets`).
- [ ] `aws_s3_bucket_server_side_encryption_configuration` with `sse_algorithm = "aws:kms"` and the KMS key from
      the tokens (`security.kms_keys.storage_key_arn`).
- [ ] Versioning, if present, as the separate `aws_s3_bucket_versioning` resource, never the deprecated inline
      `versioning {}` block.

DynamoDB (`storage.nosql.enabled: true`):
- [ ] `billing_mode = "PAY_PER_REQUEST"`.
- [ ] `server_side_encryption { enabled = true }`.
- [ ] Keys match `partition_key` / `sort_key` in the intent.

ECS Fargate (`kind: ContainerService`):
- [ ] `aws_ecs_cluster`, `aws_ecs_task_definition`, `aws_ecs_service`.
- [ ] Service subnets are exactly the `private_app` subnets from the tokens.
- [ ] `assign_public_ip = false`.
- [ ] Task `cpu`/`memory` match the token profile for `compute.size` (dev small = 256 / 512).
- [ ] Container port matches `compute.port`.

API Gateway (`api.type: http`):
- [ ] `aws_apigatewayv2_api` with `protocol_type = "HTTP"`.
- [ ] `aws_apigatewayv2_vpc_link` on private subnets.
- [ ] One `aws_apigatewayv2_route` per route in the intent, same method and path, none extra.

Conditional generation:
- [ ] A component disabled in the intent produces no resources (e.g. `blob.enabled: false` → no `aws_s3_*`).

### P1-3 Design tokens are the only source of environment values

- [ ] The agent called `read_design_tokens` (environment from the intent; `domain=compute` with the `kind`) for
      the domains listed in the kind's `synthesis.md`, and listed
      the calls in its summary.
- [ ] It did not read `platform/tokens/*.yaml` with file tools or the shell.
- [ ] VPC, subnet IDs, KMS ARNs, TLS policy, sizing and tags in the code match the tokens for that environment.
- [ ] `default_tags` match `governance.default_tags`.

### P1-4 Naming

- [ ] Resource names follow `acme-{environment}-{service_name}-{resource_suffix}`
      (e.g. `acme-dev-vehicle-inspection-booking-table`).
- [ ] Names within AWS length limits (ALB and target group: 32 characters).

### P1-5 Knowledge cutoff — Terraform

- [ ] The agent read the provider version from `.terraform.lock.hcl` and called `get_latest_provider_version`.
- [ ] For each resource type: `search_providers` + `get_provider_details` at the project's provider version.
- [ ] No deprecated arguments in the generated code; any it found are reported with the alternative.
- [ ] `terraform fmt -check && terraform validate` run in `terraform/<name>/` and passing (or the failure reported).

### P1-6 Knowledge cutoff — AWS

- [ ] `get_regional_availability` for the services used, in the token region (`eu-west-1`).
- [ ] `search_documentation` with `current_awareness` for the main services, with any relevant recent
      announcement cited (title, date, URL) or "none relevant" stated.

### P1-7 Negative tests

Missing environment tokens:
> Change the environment to staging and regenerate.

- [ ] `read_design_tokens` returns an error (there is no `platform/tokens/staging/`): the agent stops and reports it, it does
      not invent staging values or copy dev/prod.

Remote server unavailable: set `"disabled": true` on the Terraform server in `.kiro/settings/mcp.json`, then ask
for a regeneration.
- [ ] The agent says the Registry cannot be checked and does not present attributes as verified.

### P1-8 EKS synthesis (after P0-8)

- [ ] The agent loaded `kubernetes-cluster/v1alpha1/synthesis.md` (and not the ContainerService pattern).
- [ ] `aws_eks_cluster` uses ALL `private_app` subnets (two AZs); `aws_eks_node_group` only the subnet of
      `single_az_zone` (`eu-west-1a` in dev).
- [ ] Endpoint private only; secrets encrypted with `kubernetes_secrets_key_arn`; control plane logs from tokens;
      `authentication_mode = "API"` with access entries.
- [ ] Instance types and scaling from `node_profiles.small`.
- [ ] Output only in `terraform/<metadata.name>/`.

---

## Recording results

| Test | Date | Result | Notes |
| :--- | :--- | :--- | :--- |
| P0-1 | | | |
| P0-2 | | | |
| P0-3 | | | |
| P0-4 | | | |
| P0-5 | | | |
| P0-6 | | | |
| P0-7 | 2026-11-08 | Pass | Run with an EKS request before the EKS golden path existed |
| P0-8 | | | |
| P1-0 | | | |
| P1-1 | | | |
| P1-2 | | | |
| P1-3 | | | |
| P1-4 | | | |
| P1-5 | | | |
| P1-6 | | | |
| P1-7 | | | |
| P1-8 | | | |

## Gaps in the rules these tests may expose

- `staging` is allowed by the schemas but has no token folder.
- No `FunctionService` golden path yet (Lambda).
- The `kubernetes-cluster` pattern does not yet cover add-ons, IRSA / Pod Identity or how workloads reach the cluster.
- No policy-as-code checks yet: the golden paths rely on the agent and on `terraform validate`.
