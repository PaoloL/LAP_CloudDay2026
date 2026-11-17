# Phase 1b: Design Tokens via MCP

The `platform-context-engine` MCP server is the source of environment values.
When you write the design of a Phase 1 spec, or generate or change Terraform files, from an intent
`intents/<name>/<environment>.md`:

1. ENVIRONMENT VALUES: call the `read_design_tokens` tool with `environment` = `metadata.environment` and:
   - `domain` = `network`, `security`, `storage` or `governance` for shared values;
   - `domain` = `compute` with `kind` = the golden path slug (`container-service`, `kubernetes-cluster`)
     for compute values.
   The kind's synthesis.md says which domains are needed. The server returns values already merged
   (company-wide `_org` + environment) and the files they come from (`sources`).
   - DO NOT read `platform/tokens/` with file-reading tools or shell commands.
   - DO NOT invent or recall from memory VPCs, subnets, KMS ARNs, TLS policy, sizing, naming mask or tags.
   - If the tool returns an `error` field, STOP and report the error to the user.
2. PROVIDER SCHEMA: not this server's job. Follow the `terraform-knowledge-guard` power.
3. TRACE: in the final summary, list the MCP calls made (tool, environment, domain, kind).
   If the MCP server is not available, tell the user and DO NOT fall back to reading the files directly.
