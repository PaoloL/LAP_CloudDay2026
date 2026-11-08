# LAP_CloudDay2026 — Spec-driven AWS infrastructure with Kiro

Demo workspace for AWS CloudDay 2026. It shows how Kiro turns a short **intent file** into AWS Terraform,
using **steering rules** for company conventions, a **Design Tokens MCP server** for per-environment values,
and two **Kiro Powers** that fight the model's knowledge cutoff by reading official sources at runtime
through **remote MCP servers**:

- `terraform-knowledge-guard`: real `hashicorp/aws` syntax and deprecations, from the Terraform Registry.
- `aws-knowledge-guard`: new AWS services and features, What's New, docs and regional availability.

The example service is `garage-management`: an HTTP API on API Gateway, backed by ECS Fargate,
DynamoDB and S3.

## Workflow

```
1. Intent      user request ──► .kiro/templates/intent.template.md ──► infra-intent.md
                                (steering 00-phase0-intent.md)

2. Synthesis   infra-intent.md ──► terraform/*.tf
                                    ▲  steering 01-phase1-synthesis.md       patterns, naming, provider ~> 5.0
                                    ▲  MCP platform-context-engine (local)    design tokens per environment
                                    ▲  power terraform-knowledge-guard        Registry docs: arguments, deprecations
                                    ▲  power aws-knowledge-guard              AWS docs, What's New, regions

3. Validate    terraform fmt -check && terraform validate
```

## Folder structure

```
LAP_CloudDay2026/
├── README.md
├── .gitignore
├── infra-intent.md                     Intent for the garage-management service (filled from the template)
├── .kiro/                              Kiro workspace configuration
│   ├── settings/mcp.json               MCP servers Kiro connects to in this workspace
│   ├── steering/                       Rules Kiro always applies in this workspace
│   │   ├── 00-phase0-intent.md         Phase 0: capture the request into infra-intent.md, no .tf yet
│   │   ├── 01-phase1-synthesis.md      Phase 1: generate primitive aws_* resources, patterns and naming
│   │   └── 02-mcp-design-tokens.md     Phase 1b: environment values only from the Design Tokens server
│   ├── templates/
│   │   └── intent.template.md          Schema and conservative defaults for infra-intent.md
│   └── specs/garage-app/               Kiro spec: parameterise Terraform and add a dev environment
│       ├── requirements.md
│       ├── design.md
│       └── tasks.md
├── platform/                           "Platform team" assets
│   ├── mcp/
│   │   ├── server.py                   Local MCP server "platform-context-engine" (read_design_tokens)
│   │   └── requirements.txt
│   └── tokens/                         Design Tokens: company values per environment
│       ├── dev.yaml
│       └── prd.yaml                    Used when environment = prod
├── powers/                             Kiro Powers: configuration and instructions only, no code
│   ├── terraform-knowledge-guard/
│   │   ├── POWER.md                    Metadata, onboarding (HCP token), tools, behaviour rules
│   │   ├── mcp.json                    Remote server: https://mcp.terraform.io/mcp
│   │   └── steering/
│   │       └── terraform-workflow.md   Provider version → Registry docs per resource → deprecations → validate
│   └── aws-knowledge-guard/
│       ├── POWER.md                    Metadata, tools, behaviour rules
│       ├── mcp.json                    Remote server: https://knowledge-mcp.global.api.aws
│       └── steering/
│           ├── new-features-check.md   Recent announcements, impact on the design, region, Terraform support
│           └── aws-workflow.md         Regions, documented quotas, ARN formats, best practices
└── terraform/                          Generated infrastructure for garage-management (demo output)
    ├── versions.tf                     Terraform >= 1.5, hashicorp/aws ~> 5.0, provider + default tags
    ├── variables.tf                    container_image, acm_certificate_arn, alb_internal_domain_name, log_retention_days
    ├── locals.tf                       Naming prefix, environment values (today: prod values)
    ├── network.tf                      Internal ALB, listener, target group, security groups
    ├── apigw.tf                        HTTP API, VPC link, integration, routes, stage, access logs
    ├── ecs.tf                          ECS cluster, Fargate task definition and service, logs
    ├── dynamodb.tf                     DynamoDB table
    ├── s3.tf                           Photos bucket: public access block, KMS encryption, versioning, logging
    ├── iam.tf                          Task and execution roles and policies
    ├── outputs.tf                      api_endpoint, photos_bucket_name, dynamodb_table_name, ecs_cluster_name
    └── .terraform.lock.hcl             Pinned provider version (hashicorp/aws 5.100.0)
```

Not committed: `.venv/` (Python environment for `platform-context-engine`) and `terraform/.terraform/`
(provider downloaded by `terraform init`).

## Components

### Steering rules (`.kiro/steering/`)

| File | What it enforces |
| :--- | :--- |
| `00-phase0-intent.md` | Do not write `.tf` files yet. Fill `intent.template.md` from the request, use conservative defaults for missing fields, write `infra-intent.md`. |
| `01-phase1-synthesis.md` | Primitive provider resources only, no community modules. Per-service patterns (S3 public access block + KMS, DynamoDB on-demand + encryption, Fargate in private subnets without public IP, HTTP API with VPC link). Naming: `acme-{environment}-{service_name}-{suffix}`. |
| `02-mcp-design-tokens.md` | Read environment values only through `read_design_tokens`, never by opening `platform/tokens/*.yaml` directly. `prod` maps to `prd.yaml`. Provider schema comes from `terraform-knowledge-guard`. |

### MCP server `platform-context-engine` (`platform/mcp/`, local)

| Tool | Purpose |
| :--- | :--- |
| `read_design_tokens(domain, environment)` | Returns values from `platform/tokens/<env>.yaml` for one domain: `network`, `security`, `compute`, `storage`, `governance`. |

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
| Terraform >= 1.5 | Validating and planning `terraform/` |
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
cd terraform && terraform init -backend=false && cd -
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

Test prompt: *"Check whether the `aws_s3_bucket` arguments used in terraform/s3.tf are deprecated in provider
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

## Current status

- Both powers and `platform-context-engine` connect in Kiro CLI (checked 2026-11-08).
- `terraform/` holds the **prod** configuration, with prod values written directly in `locals.tf`.
- `infra-intent.md` declares `environment: "prod"`.
- The `garage-app` spec (all tasks open) moves those values into variables and adds
  `terraform/environments/dev.tfvars` and `prod.tfvars`, generated from the Design Tokens, plus
  consistency tests in `tests/unit/`.
- The provider is pinned to `~> 5.0` (installed 5.100.0) while the latest release is 6.x. Upgrading needs a
  change to `versions.tf` and the synthesis steering rule; `terraform-knowledge-guard` can read the 6.x
  upgrade guide first.
- Until the `.tfvars` files exist, `terraform plan` asks for `container_image`, `acm_certificate_arn` and
  `alb_internal_domain_name`.
