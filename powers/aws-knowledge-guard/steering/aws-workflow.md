# AWS: anti-knowledge-cutoff workflow during design

## Regions
- Use `list_regions` for the correct identifiers, not memory.
- Before using a service, feature or CloudFormation resource in a Region: `get_regional_availability`.
- If it is not available, propose alternatives and ask for confirmation.

## Limits and quotas
- Look up limits with `search_documentation` (e.g. "Fargate service quotas", "API Gateway HTTP API quotas")
  and read the service's "Quotas" or "Limits" page with `read_documentation`.
- These are **default** values: the value applied to the account may differ. Tell the user and, if the limit is
  critical, suggest checking it in Service Quotas.

## ARNs and IAM policies
- For ARN formats, find the service's "Actions, resources, and condition keys" page
  (`search_documentation` + `read_documentation`) and use the formats listed there.
- In Terraform prefer references (`aws_x.y.arn`) to hand-built strings.
- In IAM policies do not use `Resource: "*"` when the ARN format allows narrowing it.

## Best practices
- For architecture choices (security, reliability, cost) look up the Well-Architected guidance or the service
  documentation and cite the page used.

## What to report
- Pages consulted (URL) for each decision.
- What is a documented default value and not a value verified on the account.
