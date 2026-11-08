# Valori derivati dai Design Tokens platform/tokens/prd.yaml (environment: prod)
locals {
  environment  = "prod"
  service_name = "garage-management"
  name_prefix  = "acme-${local.environment}-${local.service_name}"
  aws_region   = "eu-west-1"

  vpc_id          = "vpc-0999999999prod000"
  private_subnets = ["subnet-0prodapp1a", "subnet-0prodapp1b", "subnet-0prodapp1c"]

  storage_key_arn  = "arn:aws:kms:eu-west-1:444455556666:key/prod-pci-storage-cmk"
  database_key_arn = "arn:aws:kms:eu-west-1:444455556666:key/prod-pci-database-cmk"
  tls_policy       = "ELBSecurityPolicy-TLS13-1-2-2021-06"

  fargate_cpu    = "512"
  fargate_memory = "1024"
  desired_count  = 2
  container_port = 8080

  audit_log_bucket = "acme-prod-security-audit-logs"

  default_tags = {
    Organization    = "AcmeCorp"
    Environment     = "prod"
    ManagedBy       = "Kiro-IaI"
    CostCenter      = "Fleet-Core-Prod"
    ComplianceScope = "pci-dss"
  }

  # Route dichiarate in infra-intent.md
  api_routes = [
    "GET /garages",
    "POST /garages",
    "GET /garages/{garage_id}",
    "PUT /garages/{garage_id}",
    "DELETE /garages/{garage_id}",
    "GET /cars",
    "POST /cars",
    "GET /cars/{car_id}",
    "PUT /cars/{car_id}",
    "DELETE /cars/{car_id}",
    "GET /motorcycles",
    "POST /motorcycles",
    "GET /motorcycles/{motorcycle_id}",
    "PUT /motorcycles/{motorcycle_id}",
    "DELETE /motorcycles/{motorcycle_id}",
  ]
}
