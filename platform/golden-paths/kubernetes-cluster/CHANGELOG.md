# KubernetesCluster — changelog

## v1alpha1 (2026-11-12) — intent file format
- Intents and golden examples are Markdown with YAML frontmatter (`intents/<name>/<env>.md`): the frontmatter
  holds the same fields, validated by the same schema; the body adds `## Request` and `## Decisions` (living ADR).
- No change to the schema fields: existing intents only move from `.yaml` to `.md`.

## v1alpha1 (2026-11-08)
- First version. Dev environment only.
- Fields: `kubernetes_version`, `node_provisioning` (managed-node-group | auto-mode), `node_topology`
  (multi-az | single-az), `endpoint_access` (private | public-and-private), `node_size`.
- The control plane always uses subnets in at least two AZs; `single-az` applies to nodes only.
