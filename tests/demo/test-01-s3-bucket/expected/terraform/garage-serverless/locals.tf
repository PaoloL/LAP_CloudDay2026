locals {
  service_name = "garage-serverless" # intent metadata.name

  # governance.naming_mask "acme-{environment}-{service_name}-{resource_suffix}" without the suffix
  name_prefix = trimsuffix(
    replace(replace(var.naming_mask, "{environment}", var.environment), "{service_name}", local.service_name),
    "-{resource_suffix}",
  )
}
