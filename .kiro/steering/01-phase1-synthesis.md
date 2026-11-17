# Phase 1: AWS Terraform Native Synthesis (spec-driven)

Phase 1 always runs as a Kiro spec. After the user confirms an intent `intents/<name>/<environment>.md`,
DO NOT write `.tf` files directly: create the spec `.kiro/specs/<name>-<environment>/` and follow the spec
workflow, one document at a time, asking for the user's approval after each:
`requirements.md` -> `design.md` -> `tasks.md`. Write Terraform only while executing the approved tasks.
Use `.kiro/specs/garage-app/` as the reference for structure and level of detail.

## Inputs
- The confirmed intent.
- The kind's pattern: `platform/golden-paths/<kind-slug>/<version>/synthesis.md`, where the version is the one
  in `apiVersion` (e.g. `kind: ContainerService`, `apiVersion: intent.acme.io/v1` -> `container-service/v1/`),
  and the building blocks in `_common/building-blocks/` it refers to. Apply ONLY that kind's pattern.
- The Design Tokens (rule `02-mcp-design-tokens.md`).

## requirements.md
- Introduction: the intent file, the golden path and version, the output folder `terraform/<name>/`.
- Read both parts of the intent: the frontmatter gives the values, the `## Decisions` table gives the reasons
  (e.g. a trade-off the user accepted): carry them into the requirements, do not re-negotiate them.
- Glossary of the components (e.g. Generator, Token_Resolver, Schema_Inspector, the resources of the kind).
- Requirements with user stories and EARS acceptance criteria, derived from:
  - every field of the intent's `spec` (e.g. `node_topology: single-az` -> nodes only in the token AZ);
  - every rule of the kind's `synthesis.md` and of the building blocks it uses;
  - the common rules below (no modules, values from tokens, Registry checks, naming, validation, no apply).
- Platform constraints and trade-offs stated as requirements (e.g. EKS control plane on at least two AZs).

## design.md
- Read the tokens now with `read_design_tokens` and record the token -> Terraform variable map with the values.
- Runtime checks requested by the pattern, with their results and sources: versions and regional availability
  (`aws-knowledge-guard`), provider version (`terraform-knowledge-guard`).
- Architecture diagram, file layout of `terraform/<name>/`, resources per file, naming with length limits.
- Error handling, correctness properties, risks and open points (e.g. placeholder tokens, single-AZ risk).

## tasks.md
- Tasks that reference the requirements they satisfy, in this order: Registry check of every resource type
  (`search_providers` + `get_provider_details` at the project's provider version), writing the files,
  name length checks, checkpoint `terraform fmt -check && terraform validate`, optional tests (marked `*`),
  final report.

## Rules while executing the tasks
1. DO NOT use existing Terraform modules. Generate only primitive resources of the AWS provider (`~> 5.0`).
2. VALUES: only from the Design Tokens and from the intent. No values from memory.
3. SYNTAX: before writing each resource type, check its arguments and deprecations with the
   `terraform-knowledge-guard` power at the project's provider version.
4. NAMING: apply the `governance.naming_mask` token, with `{environment}` = `metadata.environment` and
   `{service_name}` = `metadata.name`. Respect AWS name length limits.
5. OUTPUT: write only to `terraform/<metadata.name>/`. Do not touch the folders of other intents.
6. VALIDATION: run `terraform fmt -check && terraform validate` in the output folder and report the result.
   Never run `terraform apply` unless the user explicitly asks.
7. SUMMARY: list the golden path and version used, the MCP calls made (tokens, documents consulted), the resources
   generated and what could not be verified.
