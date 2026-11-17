# AWS: checking new services and features

Use this when you choose a service or feature for a solution, when the user asks what's new, or when your
knowledge of a service may be out of date.

## 1. Look for recent announcements
- `search_documentation` with topic `current_awareness` and a specific phrase
  (e.g. "ECS Fargate new features", "API Gateway HTTP API launch").
- Read the relevant announcements with `read_documentation` and note title, date and URL.
- Treat as "new" anything you did not know or that was published after your cutoff: do not discard it because
  you do not remember it.

## 2. Compare with the proposed solution
For each chosen service ask yourself, and check in the documentation:
- is there a recent feature that simplifies the solution or replaces a workaround you were about to propose?
- has what you were about to use been deprecated, renamed or put into end of support?
- has a relevant limit or default changed?

## 3. Check availability in the Region
- `get_regional_availability` for the service, feature or CloudFormation resource in the project's Region
  (e.g. `eu-west-1`).
- If it is not available, propose alternatives (another Region or another service) and ask the user to confirm.

## 4. Check that Terraform supports it
A feature announced by AWS is not necessarily in the `hashicorp/aws` provider at the project's version yet. If the
`terraform-knowledge-guard` power is active, check the resource or argument there; otherwise flag the risk to the
user.

## What to report
- Announcements and pages consulted (title, date, URL).
- News that changes the solution, and how.
- Result of the regional check.
- What could not be verified.
