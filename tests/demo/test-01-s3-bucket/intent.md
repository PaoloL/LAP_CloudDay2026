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
---

# garage-serverless · prod

## Request

Create an S3 bucket to store the static contents of my garage serverless application in production. It must be private, versioned and encrypted.

## Decisions

| Field | Value | Source | Rationale |
| :--- | :--- | :--- | :--- |
| `kind` | `ServerlessApplication` | request | "Serverless application": the serverless-app golden path. |
| `metadata.name` | `garage-serverless` | confirmed | Derived from "my garage serverless application" and confirmed by the user. |
| `metadata.environment` | `prod` | request | "In production". |
| `metadata.owner` | `team-fleet` | confirmed | Not in the request: Kiro asked for it. |
| `spec.storage.blob.enabled` | `true` | request | "Create an S3 bucket". |
| `spec.storage.blob.purpose` | `static-content` | request | "Static contents": becomes the bucket suffix in the naming mask. |

## Notes

"Private, versioned and encrypted" are not fields of the contract: the platform guarantees them.
The `s3-bucket` building block and the prod Design Tokens give a public access block, versioning `Enabled` and
SSE-KMS with the storage key; the gate (`policy/s3.rego`) checks all three on the plan.
