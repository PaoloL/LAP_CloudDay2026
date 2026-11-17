---
name: "terraform-knowledge-guard"
displayName: "Terraform Knowledge Guard"
description: "Overcomes the LLM knowledge cutoff on Terraform: real syntax and deprecated arguments of the hashicorp/aws provider, read at runtime from the Terraform Registry through HashiCorp's remote Terraform MCP server."
keywords: ["terraform", "tf", "hcl", "provider", "hashicorp/aws", "aws_", "resource", "data source", "deprecated", "deprecation", "schema", "arguments", "upgrade", "provider version", "registry", "module", "iac", "knowledge cutoff"]
author: "maverick"
---

# Terraform Knowledge Guard

Your training has a cutoff: the `hashicorp/aws` provider ships new versions every week, adds resources,
deprecates and removes arguments. This power connects you to **HashiCorp's remote Terraform MCP server**
(`https://mcp.terraform.io/mcp`), which reads the official Terraform Registry documentation for the provider
version you specify.

**Golden rule: before writing the name of a resource, argument or block "from memory", check it in the Registry
documentation for the provider version the project uses.**

# Onboarding

## Step 1: HCP Terraform token
The remote server requires an HCP Terraform account (the Free plan is fine, US-region organisation) and an API
token (user or team).
1. Create the token: HCP Terraform -> User settings -> Tokens.
2. Add this line to `~/.kiro/.env` (the value includes the word `Bearer` and a space):
   ```
   HCP_TERRAFORM_AUTH_HEADER="Bearer <token>"
   ```
3. `mcp.json` starts `mcp-remote` through `dotenv`, which reads `~/.kiro/.env` and forwards requests to
   `https://mcp.terraform.io/mcp` with the `Authorization` header. Never write the token into `mcp.json`.

Prerequisites: `dotenv` (in `/opt/homebrew/bin`) and Node.js (`npx`).
If the server answers `Authorization bearer token is required`, the line in `~/.kiro/.env` is missing or wrong.

## Step 2: Check
In Kiro CLI run `/mcp` (or `/tools`): the `terraform-registry` server must be connected with 9 tools,
such as `search_providers` and `get_provider_details`.

# Server tools (`terraform-registry`)

| Tool | When to use it |
| :--- | :--- |
| `get_latest_provider_version` | At the start of any IaC work: compare the latest `hashicorp/aws` version with the project's. |
| `search_providers` | Find the document of a resource, data source or guide (e.g. upgrade guide) and get its ID, for a specific provider version. |
| `get_provider_details` | Read the full documentation of that resource: arguments, blocks, exported attributes, deprecation notes. |
| `get_provider_capabilities` | Overview of what the provider offers (resources, data sources, functions). |
| `search_modules` / `get_module_details` / `get_latest_module_version` | Only if the user asks for a module: the workspace rules may forbid them. |
| `search_policies` / `get_policy_details` | Sentinel policy libraries from the Registry. |

The remote server also exposes HCP Terraform tools for workspaces, runs, teams, variables and the private
registry. They are disabled in `mcp.json` (`disabledTools`): this power only reads the public Registry
documentation.

# Workflow steering
- Writing, reviewing or upgrading `.tf` files -> `terraform-workflow.md`

# Behaviour rules
1. Never rely on memory for resource names, arguments, blocks or allowed values: read the documentation.
2. Always read the documentation for the **provider version the project uses** (from `.terraform.lock.hcl` or
   the constraint in `versions.tf`), not the latest: arguments change between major versions.
3. If the server is not reachable or cannot find the document, **stop and report it**; do not fall back on
   remembered values and do not present them as verified.
4. In the final summary, list the documents consulted (resource + version) and what you could NOT verify.
