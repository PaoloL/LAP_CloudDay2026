# ContainerService — changelog

## v1 (2026-11-12) — intent file format
- Intents and golden examples are Markdown with YAML frontmatter (`intents/<name>/<env>.md`): the frontmatter
  holds the same fields, validated by the same schema; the body adds `## Request` and `## Decisions` (living ADR).
- No change to the schema fields: existing intents only move from `.yaml` to `.md`.

## v1 (2026-11-08)
- First version in the `apiVersion` / `kind` / `metadata` / `spec` format, migrated from `intent.schema.json` 1.0.
- `compute.type` removed: the kind of compute is given by `kind`.
- Added `metadata.owner`.
