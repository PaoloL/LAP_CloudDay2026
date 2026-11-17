---
apiVersion: intent.acme.io/v1alpha1
kind: KubernetesCluster
metadata:
  name: platform-eks
  environment: dev
  owner: team-platform
spec:
  kubernetes_version: "1.33"   # example: must be verified at runtime against the supported versions
  node_provisioning: managed-node-group
  node_topology: single-az
  endpoint_access: private
  node_size: small
---

# platform-eks · dev (golden example)

## Request

Create an EKS cluster for the DEV environment with the nodes in a single AZ.

## Decisions

| Field | Value | Source | Rationale |
| :--- | :--- | :--- | :--- |
| `spec.node_topology` | `single-az` | confirmed | Control plane on at least two AZs (EKS requirement), nodes on one. |
| `spec.kubernetes_version` | `1.33` | confirmed | Example value: always verify it at runtime against the versions EKS supports. |
| `spec.endpoint_access` | `private` | default | Schema default. |
