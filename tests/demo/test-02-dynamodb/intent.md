---
apiVersion: intent.acme.io/v1
kind: ServerlessApplication
metadata:
  name: garage-serverless
  environment: prod
  owner: team-fleet
spec:
  storage:
    blob:
      enabled: true
      purpose: static-content
    nosql:
      enabled: true
      table_name: primary
      partition_key: PK
      sort_key: SK
---

# garage-serverless · prod

## Request

Create an S3 bucket to store the static contents of my garage serverless application in production. It must be private, versioned and encrypted.

Add a DynamoDB table to the garage serverless application to store garages, bikes and cars.

## Decisions

| Field | Value | Source | Rationale |
| :--- | :--- | :--- | :--- |
| `kind` | `ServerlessApplication` | request | "Serverless application": the serverless-app golden path. |
| `metadata.name` | `garage-serverless` | confirmed | Derived from "my garage serverless application" and confirmed by the user. |
| `metadata.environment` | `prod` | request | "In production". |
| `metadata.owner` | `team-fleet` | confirmed | Not in the request: Kiro asked for it. |
| `spec.storage.blob.enabled` | `true` | request | "Create an S3 bucket". |
| `spec.storage.blob.purpose` | `static-content` | request | "Static contents": becomes the bucket suffix in the naming mask. |
| `spec.storage.nosql.enabled` | `true` | request | "Add a DynamoDB table". |
| `spec.storage.nosql.table_name` | `primary` | confirmed | One table for the three entities: suffix in the naming mask. |
| `spec.storage.nosql.partition_key` | `PK` | confirmed | Single-table design: `<ENTITY>#<id>`. |
| `spec.storage.nosql.sort_key` | `SK` | confirmed | Single-table design. |

## Notes

"Private, versioned and encrypted" are not fields of the contract: the platform guarantees them.
The `s3-bucket` building block and the prod Design Tokens give a public access block, versioning `Enabled` and
SSE-KMS with the storage key; the gate (`policy/s3.rego`) checks all three on the plan.
