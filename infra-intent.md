---
service_name: "garage-management"
environment: "prod"
exposure: "public"

api:
  type: "http"
  routes:
    - "GET /garages"
    - "POST /garages"
    - "GET /garages/{garage_id}"
    - "PUT /garages/{garage_id}"
    - "DELETE /garages/{garage_id}"
    - "GET /cars"
    - "POST /cars"
    - "GET /cars/{car_id}"
    - "PUT /cars/{car_id}"
    - "DELETE /cars/{car_id}"
    - "GET /motorcycles"
    - "POST /motorcycles"
    - "GET /motorcycles/{motorcycle_id}"
    - "PUT /motorcycles/{motorcycle_id}"
    - "DELETE /motorcycles/{motorcycle_id}"

compute:
  type: "container-serverless"
  size: "small"
  port: 8080

storage:
  nosql:
    enabled: true
    table_name: "garage-management-primary"
    partition_key: "PK"
    sort_key: "SK"
  blob:
    enabled: true
    purpose: "vehicle-photos"
---
