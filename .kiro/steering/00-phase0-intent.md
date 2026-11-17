# Phase 0: Intent Capture Protocol

When the user asks for new infrastructure or architectural changes:
1. DO NOT call tools that create files with the `.tf` extension.
2. Pick the golden path that fits the request. The available golden paths are the folders of
   `platform/golden-paths/` (except `_common`); for each one read the latest version:
   - `container-service/v1` -> `kind: ContainerService` (service on ECS Fargate with API, DynamoDB, S3)
   - `kubernetes-cluster/v1alpha1` -> `kind: KubernetesCluster` (EKS cluster, dev only)
   - `serverless-app/v1` -> `kind: ServerlessApplication` (S3 bucket, DynamoDB table, Lambda function, HTTP API:
     each optional). Write only the components the user asked for: an absent component is disabled.
   For the chosen golden path read `intent.schema.json` (fields, `enum`, `default`), the common part
   `_common/intent-common.schema.json`, the `CHANGELOG.md` and the example in `examples/`.
3. Extract the entities from the user's message and fill in `metadata` and `spec`.
4. For fields the user did not specify:
   - Use the schema's `default` value: it is the most conservative choice.
   - If a field has no default (e.g. `kubernetes_version`), verify it with the knowledge-cutoff powers or ask for it.
   - Do not invent keys or structures outside the schema.
   - If the request cannot be expressed with any golden path, or goes against a platform constraint
     (e.g. an EKS cluster on a single AZ: the control plane needs at least two), DO NOT force it: explain the
     constraint and propose the closest alternative as an assumption to confirm, or a change to the
     golden path, which the platform team must approve through a PR.
   - `alpha`/`beta` versions of a golden path are allowed only in `dev`.
5. The target file is `intents/<metadata.name>/<metadata.environment>.md`: Markdown with YAML frontmatter.
   - Frontmatter (between the two `---` lines), for machines: only `apiVersion`, `kind`, `metadata`, `spec`.
   - Body, for humans and LLMs:
     - `## Request`: the user's request in natural language (what, not how);
     - `## Decisions`: the living ADR, a table `| Field | Value | Source | Rationale |` with one row for every
       field you set. `Field` is the dotted path in the frontmatter (e.g. `spec.exposure`); `Source` is
       `request` (stated by the user), `default` (schema default), `confirmed` (an assumption the user
       confirmed) or `platform` (a platform constraint).
     - `## Notes` (optional): requirements in the request that the platform already guarantees (e.g. "private,
       encrypted"), with the building block or token that guarantees them. Do not turn them into fields.
   - If it does not exist, create it from the golden path's example.
   - If it exists, change only the fields the user asked to change and update their rows in `## Decisions`;
     keep the other rows.
   - Never write to the intent of another service or another environment.
   `metadata.owner` is the owning team: if the user does not give it, ask for it.
6. Validate the file before showing it:
   ```bash
   .venv/bin/python platform/tools/validate.py intents/<name>/<environment>.md
   ```
   The validator checks the frontmatter against the schema, the two body sections, that every row of
   `## Decisions` names a field that exists in the frontmatter, and that Design Tokens exist for that
   environment and kind. If it fails,
   fix the file and validate again. If you cannot run it, tell the user.
7. Show the user a precise summary of the assumptions you made (every field with a default or inferred value)
   and ask for explicit confirmation before moving to the next phase.
8. After confirmation, Phase 1 starts as a Kiro spec (rule `01-phase1-synthesis.md`). Do not offer to
   generate Terraform directly.
