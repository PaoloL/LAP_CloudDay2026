# ServerlessApplication — changelog

## v1 (2026-11-12)
- First version. Intent file: Markdown with YAML frontmatter (`intents/<name>/<env>.md`).
- Components, each optional (absent = disabled): `storage.blob` (S3), `storage.nosql` (DynamoDB),
  `function` (Lambda, CRUD on `entities`), `api` (HTTP API).
- Constraints: an HTTP API needs the function; the function needs the DynamoDB table.
- `exposure` decides the authorization (public -> JWT, internal -> IAM): never unauthenticated routes.
- New building blocks: `lambda-function.md`, `http-api-lambda.md`. New token file: `compute/serverless-app.yaml`.
