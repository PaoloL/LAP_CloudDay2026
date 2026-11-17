---
apiVersion: intent.acme.io/v1
kind: ContainerService
metadata:
  name: garage-management
  environment: dev
  owner: team-fleet
spec:
  exposure: public
  api:
    type: http
    routes:
      - "GET /garages"
      - "POST /garages"
      - "GET /garages/{garage_id}"
  compute:
    size: small
    port: 8080
  storage:
    nosql:
      enabled: true
      table_name: garage-management-primary
      partition_key: PK
      sort_key: SK
    blob:
      enabled: true
      purpose: vehicle-photos
---

# garage-management · dev (golden example)

## Request

HTTP API to manage garages (create and read), storing the data in a database and the vehicle photos
in a bucket. Reachable from the internet.

## Decisions

| Field | Value | Source | Rationale |
| :--- | :--- | :--- | :--- |
| `spec.exposure` | `public` | confirmed | "Reachable from the internet" is a security choice: confirmed explicitly. |
| `spec.api.routes` | 3 routes | request | Only the operations in the request. |
| `spec.compute.size` | `small` | default | Schema default. |
| `spec.storage.blob.purpose` | `vehicle-photos` | request | Becomes the bucket suffix in the naming mask. |
