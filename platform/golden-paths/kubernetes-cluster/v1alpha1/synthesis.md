# Synthesis: KubernetesCluster v1alpha1 (Amazon EKS)

Applies to intents with `apiVersion: intent.acme.io/v1alpha1`, `kind: KubernetesCluster`. Alpha version: dev only.
The common rules in `.kiro/steering/01-phase1-synthesis.md` also apply.

## Tokens to read (`read_design_tokens`, environment = `metadata.environment`)
| Domain | kind | Use |
| :--- | :--- | :--- |
| `network` | | region, VPC, subnets per tier and AZ |
| `security` | | `kms_keys.kubernetes_secrets_key_arn`, deletion protection |
| `governance` | | naming mask, tags |
| `compute` | `kubernetes-cluster` | subnet tiers, AZ for single-az, node profiles, logs |

If a required token is missing (e.g. `kubernetes_secrets_key_arn`), stop and report it.

## Runtime checks before writing
- `spec.kubernetes_version` is among the versions EKS supports in standard support: check with the
  `aws-knowledge-guard` power (documentation and recent announcements). If it is not, stop and propose a version.
- EKS (and Auto Mode if requested) is available in the token region: `get_regional_availability`.
- Arguments of `aws_eks_cluster`, `aws_eks_node_group`, `aws_eks_access_entry` at the project's provider
  version: `terraform-knowledge-guard` power.

## Resources
Control plane:
- `aws_eks_cluster` with `vpc_config.subnet_ids` = ALL subnets of the `control_plane_subnet_tier` tier
  (at least two AZs: an EKS requirement, even when nodes run in a single AZ).
- `endpoint_private_access = true`; `endpoint_public_access = true` only if
  `spec.endpoint_access: public-and-private`.
- `encryption_config` for secrets with the `security.kms_keys.kubernetes_secrets_key_arn` key.
- `enabled_cluster_log_types` from the tokens.
- `access_config.authentication_mode = "API"`; access through `aws_eks_access_entry`, never by editing the
  authentication configuration by hand.
- Dedicated IAM role for the cluster.

Nodes (`spec.node_provisioning: managed-node-group`):
- `aws_eks_node_group` with `instance_types` and scaling from `node_profiles[spec.node_size]`.
- `subnet_ids`: with `node_topology: multi-az` all subnets of the `node_subnet_tier` tier; with `single-az` ONLY
  the subnet of the `single_az_zone` AZ.
- Dedicated IAM role for the nodes.

Nodes (`spec.node_provisioning: auto-mode`): use the EKS Auto Mode arguments documented in the Registry for the
provider version; if that provider version does not support them, stop and report it.

## Tell the user
With `node_topology: single-az`, a problem in that AZ stops all workloads, and EBS volumes stay bound to that AZ.
Acceptable in dev to reduce costs.

## Output folder
`terraform/<metadata.name>/`.
