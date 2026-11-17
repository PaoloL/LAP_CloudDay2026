# LAP_CloudDay2026 — Infrastructure as Intent with Kiro

Demo workspace for AWS CloudDay 2026. It shows how Kiro turns a short **intent** into AWS Terraform in two phases:

- **Phase 0 — Intent Contract (Semantic Negotiation):** the request becomes a validated intent that follows the
  contract of a **golden path**.
- **Phase 1 — DNA Synthesis (Native, Constraint-Driven Generation):** the intent becomes primitive Terraform,
  driven by the golden path's synthesis pattern, the **Design Tokens** of the environment and two **Kiro Powers**
  that read official sources at runtime through remote MCP servers:
  - `terraform-knowledge-guard`: real `hashicorp/aws` syntax and deprecations, from the Terraform Registry.
  - `aws-knowledge-guard`: new AWS services and features, What's New, docs and regional availability.

Example intents: `garage-management` (`ContainerService`: API Gateway, ECS Fargate, DynamoDB, S3) and an EKS
cluster example (`KubernetesCluster`, alpha).

## Workflow

```
0. Intent      request ──► golden path <kind>/<version>/intent.schema.json ──► intents/<name>/<env>.md
               (steering 00-phase0-intent.md)            validated by platform/tools/validate.py

1. Synthesis   intents/<name>/<env>.md   ──► spec .kiro/specs/<name>-<env>/ (requirements → design → tasks) ──► terraform/<name>/*.tf
                   ▲  steering 01-phase1-synthesis.md       common rules: no modules, naming, validation
                   ▲  golden path synthesis.md + building blocks   pattern of the kind
                   ▲  MCP platform-context-engine (local)    read_design_tokens(domain, env, kind)
                   ▲  power terraform-knowledge-guard        Registry docs: arguments, deprecations
                   ▲  power aws-knowledge-guard              AWS docs, What's New, regions

2. Validate    terraform plan ──► terraform show -json ──► tfplan.json ──► conftest test -p policy/ --data tokens
                   ▲  policy/*.rego (Security owns them)    deterministic: deny + reasons back to Kiro
                   ▲  platform/tools/export_tokens.py       the same Design Tokens that fed generation
```

## Organising principle

**What changes together lives together; what has different owners lives apart.**

- A **golden path** (`platform/golden-paths/<kind>/<version>/`) packages everything that evolves in the same PR:
  intent schema, token schema, synthesis pattern, examples, changelog.
- **Design Tokens** (`platform/tokens/`) are organised by environment and domain, because values are owned by
  different teams (network, security, FinOps, platform) and change at a different pace.
- **Intents** (`intents/<name>/<env>.md`) and **generated code** (`terraform/<name>/`) belong to the service
  team, one folder and one Terraform state per intent.

Ownership is enforced with `.github/CODEOWNERS`.

## Folder structure

```
LAP_CloudDay2026/
├── README.md
├── .gitignore
├── .github/CODEOWNERS                  Who approves which folder
├── .kiro/
│   ├── settings/mcp.json               MCP servers Kiro connects to in this workspace
│   ├── steering/                       Always loaded, short and common to every kind
│   │   ├── 00-phase0-intent.md         Phase 0: pick the golden path, fill and validate the intent, ask confirmation
│   │   ├── 01-phase1-synthesis.md      Phase 1: load the kind's pattern, common rules, output folder, validation
│   │   └── 02-mcp-design-tokens.md     Values only from read_design_tokens
│   └── specs/                          One Phase 1 spec per intent (<name>-<env>); garage-app is the reference
├── intents/                            One intent per service and environment
│   └── garage-management/
│       └── prod.md                     ContainerService v1, prod (Markdown + YAML frontmatter)
├── platform/                           Platform team assets
│   ├── golden-paths/
│   │   ├── _common/
│   │   │   ├── intent-common.schema.json   apiVersion, kind, metadata (name, environment, owner)
│   │   │   ├── tokens/*.schema.json        Schemas of the shared token domains
│   │   │   └── building-blocks/            Patterns reused by several kinds (s3-bucket, dynamodb-table, http-api,
│   │   │                                   lambda-function, http-api-lambda)
│   │   ├── container-service/          ECS Fargate
│   │   │   ├── CHANGELOG.md
│   │   │   └── v1/                     intent.schema.json, tokens.schema.json, synthesis.md, examples/
│   │   ├── kubernetes-cluster/         Amazon EKS
│   │   │   ├── CHANGELOG.md
│   │   │   └── v1alpha1/               intent.schema.json, tokens.schema.json, synthesis.md, examples/
│   │   └── serverless-app/             S3 + DynamoDB + Lambda + HTTP API (the demo)
│   │       ├── CHANGELOG.md
│   │       └── v1/                     intent.schema.json, tokens.schema.json, synthesis.md, examples/
│   ├── tokens/
│   │   ├── _org/                       Company-wide values (naming mask, base tags, TLS policy)
│   │   ├── dev/                        network, security, storage, governance + compute/<kind>.yaml
│   │   └── prod/                       same layout (no kubernetes-cluster: alpha is dev only)
│   ├── tools/validate.py               Validates intents, golden path examples and tokens; exit 1 on error
│   ├── tools/export_tokens.py          Merged Design Tokens of one environment as JSON, for Conftest --data
│   └── mcp/                            Local MCP server "platform-context-engine" (read_design_tokens)
├── powers/                             Kiro Powers: configuration and instructions only, no code
│   ├── terraform-knowledge-guard/      POWER.md, mcp.json (remote https://mcp.terraform.io/mcp), steering/
│   └── aws-knowledge-guard/            POWER.md, mcp.json (remote https://knowledge-mcp.global.api.aws), steering/
├── policy/                             The Validate gate: Rego v1 for Conftest (s3, tags, dynamodb, lambda, apigw)
│   └── policy_test.rego                Unit tests: opa test policy
├── tests/
│   ├── intent/TEST-PLAN.md             Test plan for Phase 0 and Phase 1
│   ├── demo/                           CloudDay demo: Test 01–05 (prompt, expected intent, DNA synthesis), runbook
│   └── policy/fixtures/                Plan JSON of Test 01: pass and deny (KMS key)
└── terraform/
    └── garage-management/              Generated infrastructure (prod values in locals.tf today)
        ├── versions.tf, variables.tf, locals.tf
        ├── network.tf, apigw.tf, ecs.tf, iam.tf
        ├── dynamodb.tf, s3.tf, outputs.tf
        └── .terraform.lock.hcl         Pinned provider version (hashicorp/aws 5.100.0)
```

Not committed: `.venv/` (Python environment for the local tools) and `.terraform/` folders.

## Intent contract

An intent is a Markdown file with YAML frontmatter, `intents/<name>/<env>.md`. Humans and LLMs read the same
file: the frontmatter is for machines, the prose is for intent, and both are reviewed in the same pull request.

```markdown
---
apiVersion: intent.acme.io/v1        # contract version of the kind
kind: ContainerService               # ContainerService | KubernetesCluster
metadata:
  name: garage-management            # = intents/<name>/ and terraform/<name>/
  environment: prod                  # dev | staging | prod = file name and token folder
  owner: team-fleet                  # team that approves changes
spec: { ... }                        # defined by the kind's schema
---

# garage-management · prod

## Request
Public HTTP API to manage garages, cars and motorcycles ...

## Decisions
| Field | Value | Source | Rationale |
| :--- | :--- | :--- | :--- |
| `spec.exposure` | `public` | confirmed | Explicit security choice, confirmed by the owner. ... |
| `spec.compute.size` | `small` | default | The request says nothing about load: conservative schema default. |
```

- **Frontmatter**: only `apiVersion`, `kind`, `metadata`, `spec`, validated by the golden path's JSON Schema.
- **`## Request`**: the request in natural language: what, not how.
- **`## Decisions`**: the living ADR of the intent. One row per field set; `Field` is the dotted path in the
  frontmatter, `Source` is `request`, `default`, `confirmed` or `platform`.

| kind | apiVersion | Golden path | Status |
| :--- | :--- | :--- | :--- |
| `ContainerService` | `intent.acme.io/v1` | `container-service/v1` (ECS Fargate, HTTP API, DynamoDB, S3) | stable |
| `KubernetesCluster` | `intent.acme.io/v1alpha1` | `kubernetes-cluster/v1alpha1` (EKS) | alpha: dev only |
| `ServerlessApplication` | `intent.acme.io/v1` | `serverless-app/v1` (S3, DynamoDB, Lambda, HTTP API; each optional) | stable: the CloudDay demo |

Rules enforced by the schemas: no extra keys anywhere, enums with a conservative `default`, conditional fields
(e.g. an enabled bucket needs a `purpose`), alpha/beta versions only in `dev`.

Validate locally or in CI:

```bash
.venv/bin/python platform/tools/validate.py                       # all intents, examples and tokens
.venv/bin/python platform/tools/validate.py intents/x/dev.md      # one intent
```

Besides the schemas, the validator checks that the file has a frontmatter, a `## Request` and a `## Decisions`
section, that every decision names a field that exists in the frontmatter with an allowed `Source`, that the path matches `metadata`, that tokens exist for the intent's
environment and kind, and that `single_az_zone` exists in the EKS node subnets.

### Extending the contract (platform team PR)

A new capability (a new kind, version or field) is a PR on `platform/golden-paths/` that contains, together:

1. the intent schema (new version folder for breaking changes; `v1alpha1` → `v1beta1` → `v1`);
2. the synthesis pattern (`synthesis.md`, reusing building blocks where possible);
3. the token schema and token values at least for `dev`;
4. golden examples in `examples/` (and, as CI grows, policy-as-code checks);
5. a `CHANGELOG.md` entry.

CI runs `platform/tools/validate.py`: every existing intent must still validate. CODEOWNERS requires the platform
team, plus Security when network, encryption or exposure change.

## Design Tokens

```
platform/tokens/_org/<domain>.yaml  ──merge──►  platform/tokens/<env>/<domain>.yaml        (network, security, storage, governance)
                                                platform/tokens/<env>/compute/<kind>.yaml  (container-service, kubernetes-cluster)
```

- Each value lives in one place; environment files override company-wide ones.
- Subnets are described per tier and per AZ (`private_app: {eu-west-1a: subnet-…}`), so patterns can choose AZs.
- Token schemas live with the golden paths and are checked by the validator.

## Components

### Steering rules (`.kiro/steering/`)

| File | What it enforces |
| :--- | :--- |
| `00-phase0-intent.md` | No `.tf` yet. Pick the golden path, fill `metadata`/`spec` from the request with schema defaults, explain platform constraints (e.g. EKS needs two AZs) instead of forcing them, write `intents/<name>/<env>.md` with frontmatter, `## Request` and `## Decisions` (change only requested fields and their decisions if it exists), validate, ask for confirmation. |
| `01-phase1-synthesis.md` | Spec-driven: after confirmation create `.kiro/specs/<name>-<env>/` (requirements → design → tasks, approval after each) and write Terraform only while executing tasks. Load the kind's `synthesis.md` and building blocks; primitive resources only; values from tokens; Registry and AWS checks through the powers; naming from `governance.naming_mask`; write only to `terraform/<name>/`; `terraform validate`; report. |
| `02-mcp-design-tokens.md` | Read values only through `read_design_tokens(domain, environment, kind)`, never by opening `platform/tokens/`. Stop on `error`. |

### MCP server `platform-context-engine` (`platform/mcp/`, local)

| Tool | Purpose |
| :--- | :--- |
| `read_design_tokens(domain, environment, kind="")` | `domain` = `network`, `security`, `storage`, `governance` (merged `_org` + environment) or `compute` with `kind` = `container-service` / `kubernetes-cluster`. Returns the values and their `sources`; returns `error` with the available options when an environment, domain or kind is missing. |

### Power `terraform-knowledge-guard` (remote HashiCorp Terraform MCP server)

HashiCorp-hosted server, currently in beta. Requires an HCP Terraform account (Free plan works) and an API token,
read from `~/.kiro/.env` and sent through the `mcp-remote` bridge.

| Tool | Use |
| :--- | :--- |
| `get_latest_provider_version` | Latest `hashicorp/aws` release, to compare with `.terraform.lock.hcl` |
| `search_providers` | Find the doc ID of a resource, data source or guide (e.g. upgrade guide) for a given provider version |
| `get_provider_details` | Full documentation: arguments, blocks, exported attributes, deprecation notes |
| `get_provider_capabilities` | Overview of resources, data sources and functions in the provider |
| `search_modules`, `get_module_details`, `get_latest_module_version` | Registry modules (the synthesis rule forbids them unless asked) |
| `search_policies`, `get_policy_details` | Sentinel policy libraries from the Registry |

The server also exposes about 50 HCP Terraform tools (workspaces, runs, teams, variables, private registry),
several of which create or delete things. They are listed in `disabledTools` in both `mcp.json` files, so only the
9 public Registry tools are available to the agent.

### Power `aws-knowledge-guard` (remote AWS Knowledge MCP server)

AWS-managed, public, free, rate-limited. No AWS account or credentials.

| Tool | Use |
| :--- | :--- |
| `search_documentation` | Docs, What's New announcements (`current_awareness` topic), API reference, troubleshooting |
| `read_documentation` | Read a full page |
| `recommend` | Related and recently added pages |
| `list_regions` | Current list of AWS Regions |
| `get_regional_availability` | Availability of a service, feature, API or CloudFormation resource in a Region |

It cannot see your AWS account: quotas it returns are documented defaults, not your applied values.
Do not configure the AWS MCP Server or AWS API MCP server alongside it: AWS advises against overlapping tools.

## Setup

### Prerequisites

| Tool | Used by |
| :--- | :--- |
| Kiro (CLI or IDE) | Everything |
| Python 3.12 | `platform-context-engine` |
| Terraform >= 1.5 | Validating and planning `terraform/<name>/` |
| Node.js (`npx`) | `mcp-remote` bridge for the Terraform MCP server |
| `dotenv` CLI in `/opt/homebrew/bin` | Loading `~/.kiro/.env` for the Terraform MCP server |
| HCP Terraform account, **US region** (Free plan works) | Token for the remote Terraform MCP server. HCP Europe tokens are rejected. |

AWS Knowledge needs no account and no credentials.

### Steps

```bash
# 1. Python environment for platform-context-engine
python3.12 -m venv .venv
.venv/bin/pip install -r platform/mcp/requirements.txt

# 2. Terraform provider for validating the generated code
cd terraform/garage-management && terraform init -backend=false && cd -
```

3. Create an HCP Terraform API token (User settings → Tokens) and add it to `~/.kiro/.env`,
   with `Bearer` inside the value:
   ```
   HCP_TERRAFORM_AUTH_HEADER="Bearer <token>"
   ```

Install both powers from Kiro: **Powers → Add Custom Power → Import power from a folder** →
`powers/terraform-knowledge-guard` and `powers/aws-knowledge-guard`.

### Kiro CLI: register the powers' MCP servers

Kiro CLI installs a power's `POWER.md` and steering files but does not connect its MCP servers. Calls then
fail with `MCP server 'power-<power>-<server>' is not connected`. This workspace's `.kiro/settings/mcp.json`
already registers them under the names the powers look for:

```json
"power-terraform-knowledge-guard-terraform-registry": {
  "command": "/opt/homebrew/bin/dotenv",
  "args": ["-f", "/Users/maverick/.kiro/.env", "run", "--",
           "/opt/homebrew/bin/npx", "-y", "mcp-remote", "https://mcp.terraform.io/mcp",
           "--header", "Authorization:${HCP_TERRAFORM_AUTH_HEADER}"],
  "disabledTools": ["whoami", "list_workspaces", "create_workspace", "create_run", "...52 HCP Terraform tools"]
},
"power-aws-knowledge-guard-aws-knowledge": {
  "url": "https://knowledge-mcp.global.api.aws"
}
```

The Terraform entry reads the token from `~/.kiro/.env` through `dotenv` and forwards requests with
`mcp-remote` (a local stdio-to-remote bridge), so it works from Kiro CLI and from the IDE opened from the Dock.
Never write the token into `mcp.json`. To use the powers in other workspaces, copy these entries
(with the full `disabledTools` list) into `~/.kiro/settings/mcp.json`. Paths to `dotenv`, `npx` and `~/.kiro/.env`
are absolute: update them on another machine.

### Verify

Run `/mcp` in Kiro CLI. Expected:

```
platform-context-engine                             local   ● running   1 tool
power-terraform-knowledge-guard-terraform-registry  local   ● running   9 tools
power-aws-knowledge-guard-aws-knowledge             local   ● running   5 tools
```

Test prompt: *"Check whether the `aws_s3_bucket` arguments used in terraform/garage-management/s3.tf are deprecated in provider
5.100.0, and whether recent S3 announcements would change this design."*

### Troubleshooting

Kiro writes one log folder per session in `~/.kiro/logs/<session>/`; MCP connections are in `mcp.log`,
power loading in `powers.log`.

| Symptom | Cause | Fix |
| :--- | :--- | :--- |
| `MCP server 'power-…' is not connected` | Kiro CLI installed the power but has no server entry for it | Check the entries in `.kiro/settings/mcp.json` |
| Terraform server `✗ failed`, `Connection closed` or HTML (`<!DOCTYPE`) in `mcp.log` | Token missing from `~/.kiro/.env` | Add `HCP_TERRAFORM_AUTH_HEADER`, then restart the session |
| `Terraform token is unauthorized` | Token expired, revoked, or from an HCP Europe organization | Create a new token in a US-region organization |
| `rate limit exceeded` | More than 5 requests per second to the Terraform server | Wait and retry |
| Terraform server shows more than 9 tools | HashiCorp added tools not in `disabledTools` | Add their names to `disabledTools` |
| `Could not read …/installed.json: JSON Parse error` | Kiro's installed-powers file is empty or truncated | Restore valid JSON in `~/.kiro/powers/installed.json` and reinstall the powers |

To see the Terraform bridge's own errors, run it in a terminal:

```bash
/opt/homebrew/bin/dotenv -f ~/.kiro/.env run -- npx -y mcp-remote https://mcp.terraform.io/mcp \
  --header 'Authorization:${HCP_TERRAFORM_AUTH_HEADER}'
```

## Validate: the gate (`policy/`)

Kiro proposes, OPA decides. Policies run on the plan JSON, with the same Design Tokens that fed generation:

```bash
.venv/bin/python platform/tools/export_tokens.py prod > build/tokens.prod.json
terraform -chdir=terraform/<name> plan -var-file=environments/prod.tfvars -out tfplan
terraform -chdir=terraform/<name> show -json tfplan > terraform/<name>/tfplan.json
conftest test terraform/<name>/tfplan.json -p policy --data build/tokens.prod.json
```

| Policy | Denies |
| :--- | :--- |
| `s3.rego` | a bucket without public access block (all four flags), versioning as the token, SSE-KMS with the storage key, logs to the audit bucket |
| `tags.rego` | a taggable resource without all the `governance.default_tags` keys (`tags_all`) |
| `dynamodb.rego` | a table not encrypted with the database key, PITR or deletion protection not as the tokens |
| `lambda.rego` | runtime, architecture or tracing not as `compute/serverless-app` |
| `apigw.rego` | a route with `authorization_type = "NONE"` |

Companion resources (versioning, encryption, ...) are linked to their bucket through `configuration` references:
a new bucket's ID is unknown at plan time. Not visible at plan time: values computed by AWS, such as an IAM policy
document that references a new table ARN; those stay with the building blocks, review and runtime guardrails.
CI: `.github/workflows/iac-gate.yml`. Unit tests: `opa test policy`.

## Demo (`tests/demo/`)

Five tests on the garage serverless application (`ServerlessApplication`): S3 bucket, DynamoDB table, Lambda
function, HTTP API, then the entire application in one prompt. See `tests/demo/README.md` for the 15-minute runbook.

## Current status

- Both powers and `platform-context-engine` connect in Kiro CLI (checked 2026-11-08).
- `terraform/garage-management/` holds the **prod** configuration, with prod values written directly in `locals.tf`.
- Only the prod intent exists (`intents/garage-management/prod.md`); the dev intent is task 1.1 of the spec.
- The `kubernetes-cluster/v1alpha1` golden path (EKS) exists with dev tokens and an example; no EKS intent yet.
- The `garage-app` spec (all tasks open) moves those values into variables and adds
  `terraform/garage-management/environments/dev.tfvars` and `prod.tfvars`, generated from the Design Tokens, plus
  consistency tests in `tests/unit/`.
- The provider is pinned to `~> 5.0` (installed 5.100.0) while the latest release is 6.x. Upgrading needs a
  change to `versions.tf`, the steering rule and the golden path patterns; `terraform-knowledge-guard` can read the 6.x
  upgrade guide first.
- Until the `.tfvars` files exist, `terraform plan` asks for `container_image`, `acm_certificate_arn` and
  `alb_internal_domain_name`.
