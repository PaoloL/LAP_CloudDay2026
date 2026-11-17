# Terraform: anti-knowledge-cutoff workflow

Mandatory sequence when you create, change or review `.tf` files with `aws_*` resources.

## 1. Provider version
- Read the installed version from `.terraform.lock.hcl` (block `provider "registry.terraform.io/hashicorp/aws"`,
  field `version`) and the constraint declared in `versions.tf`.
- Call `get_latest_provider_version` for `hashicorp/aws`.
- If the installed major is lower than the latest, tell the user. Do not change the constraint without their
  consent: it can change the behaviour of existing resources.

## 2. Documentation of every resource you write
For each resource or data source type:
1. `search_providers` with `provider_namespace = "hashicorp"`, `provider_name = "aws"`, the service
   (e.g. `s3_bucket_versioning`) and **the project's version**.
2. `get_provider_details` with the returned ID.
3. Use ONLY documented arguments and blocks. Respect the `Required` ones. Do not assign attributes that appear
   only in "Attribute Reference" (they are computed).
4. Avoid anything the documentation marks as **Deprecated**, and use the alternative it gives.

If an argument you expected is not there, look for a dedicated resource: configuration is often extracted into
`aws_<service>_<resource>_<feature>` (e.g. S3 versioning, encryption and public access live in `aws_s3_bucket_*`
resources).

## 3. Reviewing existing code (deprecations)
For each resource already in the `.tf` files:
- read its documentation at the project's version and compare the arguments used;
- list those marked Deprecated, with file, resource and the suggested alternative.

## 4. Major version upgrade (e.g. 5.x -> 6.x)
- `search_providers` for the provider's guides (`guides`), in particular the upgrade guide of the new major
  (e.g. `version-6-upgrade`).
- `get_provider_details` on the guide, and compare the changes with the resources used in the project.
- Tell the user what breaks and what must change **before** touching the version constraint.

## 5. Validation
The server reads documentation only, not your code. After every change, if you can run commands, run in the
Terraform folder:
```bash
terraform fmt -check && terraform validate
```
Treat every deprecation warning as something to fix or report.

## What to report in the summary
- Project provider version vs latest.
- Documents consulted (resource + version).
- Deprecated arguments found and the proposed alternative.
- Result of `terraform validate`, or the fact that it was not run.

## Known limits (do not hide them)
- The documentation does not express every semantic constraint (forbidden combinations, dependencies between
  resources): they show up with `terraform plan`.
- The remote server is in beta and needs the HCP Terraform token: if it does not answer, say so.
