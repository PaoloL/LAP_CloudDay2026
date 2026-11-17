# Test 03 · Add the Lambda function

## Prompt

> Add a Lambda function that exposes CRUD operations on garages, bikes and cars, using the DynamoDB table.

## Starting state

State after Test 02.

## Expected in Phase 0 · Intent Contract

- [ ] Adds `spec.function` with `entities: [garages, bikes, cars]` and `size: small` (default).
- [ ] If the table were missing, the schema would refuse the function: the function needs the table.

Expected contract: [`intent.md`](intent.md).

## Answers to give

- Size small: yes.

## Expected in Phase 1 · DNA Synthesis

- [ ] `read_design_tokens(compute, prod, serverless-app)`: runtime, architecture, memory, tracing, log retention.
- [ ] `aws-knowledge-guard`: the token runtime is supported and not deprecated.
- [ ] Adds `lambda.tf` (function, role, inline policy, log group); the code zip is a variable, not generated.

Details: [`dna-synthesis.md`](dna-synthesis.md).

## Expected in Validate

- [ ] `conftest test` on the plan passes with the prod tokens (see `tests/demo/README.md`).
