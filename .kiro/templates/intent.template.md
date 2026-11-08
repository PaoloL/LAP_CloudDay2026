---
service_name: "<string, kebab-case>"
environment: "dev"              # [dev | staging | prod]
exposure: "internal"           # [public | internal]

api:
  type: "http"                 # [http | none]
  routes: []                   # lista di endpoint REST

compute:
  type: "container-serverless" # [container-serverless | lambda | none]
  size: "small"                # [small | medium | large]
  port: 8080

storage:
  nosql:
    enabled: false
    table_name: ""
    partition_key: ""
    sort_key: ""
  blob:
    enabled: false
    purpose: ""
---
