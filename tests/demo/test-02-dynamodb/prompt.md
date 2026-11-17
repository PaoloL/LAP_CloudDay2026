# Test 02 · Add the DynamoDB table

## Prompt

> Add a DynamoDB table to the garage serverless application to store garages, bikes and cars.

## Starting state

State after Test 01 (intent and Terraform of Test 01).

## Expected in Phase 0 · Intent Contract

- [ ] Changes only `spec.storage.nosql` in the existing intent; Test 01 rows in `## Decisions` stay as they are.
- [ ] Proposes single-table design (`table_name: primary`, `PK`/`SK`) as an assumption to confirm.

Expected contract: [`intent.md`](intent.md).

## Answers to give

- Single table `primary` with `PK`/`SK`: yes.

## Expected in Phase 1 · DNA Synthesis

- [ ] Adds `dynamodb.tf` and the variables it needs; `s3.tf` unchanged (additive rule).
- [ ] `read_design_tokens` adds the `storage.dynamodb` values and `security.kms_keys.database_key_arn`.

Details: [`dna-synthesis.md`](dna-synthesis.md).

## Expected in Validate

- [ ] `conftest test` on the plan passes with the prod tokens (see `tests/demo/README.md`).
