# Test 04 · Add the HTTP API

## Prompt

> Expose the Lambda function to the internet with an HTTP API: CRUD routes for garages, bikes and cars.

## Starting state

State after Test 03.

## Expected in Phase 0 · Intent Contract

- [ ] Adds `spec.api` with 15 CRUD routes and asks to confirm `exposure: public` (security choice).
- [ ] Does not add authentication fields: explains that `public` means a JWT authorizer from the tokens.

Expected contract: [`intent.md`](intent.md).

## Answers to give

- Public: yes, confirmed.

## Expected in Phase 1 · DNA Synthesis

- [ ] Adds `apigw.tf`: HTTP API, Lambda integration, JWT authorizer, 15 routes with `authorization_type = "JWT"`, stage with throttling and access logs, Lambda permission.
- [ ] `read_design_tokens(compute, prod, serverless-app)` for throttling and JWT issuer/audience.

Details: [`dna-synthesis.md`](dna-synthesis.md).

## Expected in Validate

- [ ] `conftest test` on the plan passes with the prod tokens (see `tests/demo/README.md`).
