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
  function:
    enabled: true
    entities:
      - garages
      - bikes
      - cars
    size: small
  exposure: public
  api:
    type: http
    routes:
      - "GET /garages"
      - "POST /garages"
      - "GET /garages/{garage_id}"
      - "PUT /garages/{garage_id}"
      - "DELETE /garages/{garage_id}"
      - "GET /bikes"
      - "POST /bikes"
      - "GET /bikes/{bike_id}"
      - "PUT /bikes/{bike_id}"
      - "DELETE /bikes/{bike_id}"
      - "GET /cars"
      - "POST /cars"
      - "GET /cars/{car_id}"
      - "PUT /cars/{car_id}"
      - "DELETE /cars/{car_id}"
---

# garage-serverless · prod

## Request

Create the infrastructure of my garage serverless application in production: a public HTTP API with CRUD operations on garages, bikes and cars, served by a Lambda function that stores them in a DynamoDB table, and a private, versioned and encrypted S3 bucket for the static contents.

## Decisions

| Field | Value | Source | Rationale |
| :--- | :--- | :--- | :--- |
| `kind` | `ServerlessApplication` | request | "Serverless application": the serverless-app golden path. |
| `metadata.name` | `garage-serverless` | confirmed | Derived from "my garage serverless application" and confirmed by the user. |
| `metadata.environment` | `prod` | request | "In production". |
| `metadata.owner` | `team-fleet` | confirmed | Not in the request: Kiro asked for it. |
| `spec.storage.blob.enabled` | `true` | request | "An S3 bucket for the static contents". |
| `spec.storage.blob.purpose` | `static-content` | request | "Static contents": becomes the bucket suffix in the naming mask. |
| `spec.storage.nosql.enabled` | `true` | request | "Add a DynamoDB table". |
| `spec.storage.nosql.table_name` | `primary` | confirmed | One table for the three entities: suffix in the naming mask. |
| `spec.storage.nosql.partition_key` | `PK` | confirmed | Single-table design: `<ENTITY>#<id>`. |
| `spec.storage.nosql.sort_key` | `SK` | confirmed | Single-table design. |
| `spec.function.enabled` | `true` | request | "Served by a Lambda function". |
| `spec.function.entities` | `garages`, `bikes`, `cars` | request | CRUD on the three entities, stored in the DynamoDB table. |
| `spec.function.size` | `small` | default | The request says nothing about load: conservative schema default. |
| `spec.exposure` | `public` | confirmed | "Public HTTP API" is a security choice: confirmed explicitly by the user. |
| `spec.api.type` | `http` | request | "An HTTP API". |
| `spec.api.routes` | 15 CRUD routes | request | Five routes per entity (list, create, read, update, delete), no extra verbs. |

## Notes

"Private, versioned and encrypted" are not fields of the contract: the platform guarantees them.
The `s3-bucket` building block and the prod Design Tokens give a public access block, versioning `Enabled` and
SSE-KMS with the storage key; the gate (`policy/s3.rego`) checks all three on the plan.

Authentication is not a field of the contract: `exposure: public` means a JWT authorizer with the issuer and
audience from the Design Tokens on every route. No route is generated without authorization (`policy/apigw.rego`).
