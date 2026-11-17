# Test 05 · Create the entire infrastructure in one prompt

## Prompt

> Create the infrastructure of my garage serverless application in production: a public HTTP API with CRUD operations on garages, bikes and cars, served by a Lambda function that stores them in a DynamoDB table, and a private, versioned and encrypted S3 bucket for the static contents.

## Starting state

Clean state, as before Test 01 (run `tests/demo/reset.sh`).

## Expected in Phase 0 · Intent Contract

- [ ] Writes the whole intent in one step: the frontmatter must be **identical** to Test 04 (`tests/demo/check.py` compares them).
- [ ] Asks the same questions: owner, name, table design, `exposure: public`.

Expected contract: [`intent.md`](intent.md).

## Answers to give

- Same answers as Tests 01–04.

## Expected in Phase 1 · DNA Synthesis

- [ ] Same files as Tests 01–04 together: `s3.tf`, `dynamodb.tf`, `lambda.tf`, `apigw.tf` plus the common files.
- [ ] Same token values: one contract, one result, whatever the path.

Details: [`dna-synthesis.md`](dna-synthesis.md).

## Expected in Validate

- [ ] `conftest test` on the plan passes with the prod tokens (see `tests/demo/README.md`).
