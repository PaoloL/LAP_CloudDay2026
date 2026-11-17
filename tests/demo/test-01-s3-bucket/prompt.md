# Test 01 · Create the S3 bucket

## Prompt

> Create an S3 bucket to store the static contents of my garage serverless application in production. It must be private, versioned and encrypted.

## Starting state

No `intents/garage-serverless/` and no `terraform/garage-serverless/` (run `tests/demo/reset.sh`).

## Expected in Phase 0 · Intent Contract

- [ ] Picks `kind: ServerlessApplication`, `apiVersion: intent.acme.io/v1` (golden path `serverless-app/v1`).
- [ ] Writes `intents/garage-serverless/prod.md` with only `spec.storage.blob`: no other component.
- [ ] Asks for `metadata.owner` (not in the request) and confirms `metadata.name`.
- [ ] Does **not** add fields for "private, versioned, encrypted": it explains in `## Notes` that the platform guarantees them.
- [ ] Runs `platform/tools/validate.py` and shows the `## Decisions` table, then waits for confirmation. No `.tf` file.

Expected contract: [`intent.md`](intent.md).

## Answers to give

- Owner: `team-fleet`.
- Name `garage-serverless`: yes.
- Confirm the intent: yes.

## Expected in Phase 1 · DNA Synthesis

- [ ] Spec `.kiro/specs/garage-serverless-prod/`: requirements -> design -> tasks.
- [ ] `read_design_tokens` for `governance`, `network`, `security`, `storage` (environment `prod`).
- [ ] `terraform-knowledge-guard`: the five S3 resource types at provider 5.x.
- [ ] Files: `versions.tf`, `variables.tf`, `locals.tf`, `s3.tf`, `outputs.tf`, `environments/prod.tfvars`.
- [ ] Matches `expected/terraform/garage-serverless/` (same resources and token values).

Details: [`dna-synthesis.md`](dna-synthesis.md).

## Expected in Validate

- [ ] `conftest test` on the plan passes with the prod tokens (see `tests/demo/README.md`).
