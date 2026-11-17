# Demo: the garage serverless application

API Gateway (HTTP API) -> Lambda -> DynamoDB, plus an S3 bucket for static contents, built with
Infrastructure as Intent. Golden path: `platform/golden-paths/serverless-app/v1`.

| Test | Prompt | Adds to the intent | New Terraform | Gate |
| :--- | :--- | :--- | :--- | :--- |
| [01](test-01-s3-bucket/prompt.md) | Create S3 bucket | `storage.blob` | `s3.tf` (+ common files) | `s3.rego`, `tags.rego` |
| [02](test-02-dynamodb/prompt.md) | Create DynamoDB | `storage.nosql` | `dynamodb.tf` | `dynamodb.rego` |
| [03](test-03-lambda/prompt.md) | Create Lambda (CRUD garages, bikes, cars) | `function` | `lambda.tf` | `lambda.rego` |
| [04](test-04-api-gateway/prompt.md) | Create API Gateway | `exposure`, `api` | `apigw.tf` | `apigw.rego` |
| [05](test-05-entire-app/prompt.md) | Create the entire infrastructure | all, in one prompt | all of the above | all |

Each folder has `prompt.md` (what to type, what Kiro must ask, what to answer), `intent.md` (the expected
contract) and `dna-synthesis.md` (tokens, token -> Terraform map, resources, gate). Test 01 also has the
reference Terraform in `expected/`.

## Offline checks (no AWS, no Kiro)
```bash
.venv/bin/python platform/tools/validate.py        # contracts, examples, tokens
.venv/bin/python tests/demo/check.py               # Test 05 == Test 04; Test 01 tfvars == tokens
opa test policy                                    # unit tests of the policies (or: conftest verify -p policy)
.venv/bin/python platform/tools/export_tokens.py prod > build/tokens.prod.json
conftest test tests/policy/fixtures/test01-pass.tfplan.json     -p policy --data build/tokens.prod.json  # pass
conftest test tests/policy/fixtures/test01-deny-kms.tfplan.json -p policy --data build/tokens.prod.json  # 1 deny
```
The fixtures follow the `terraform show -json` format; regenerate them from a real plan of the Test 01
reference code when you have AWS credentials (see Segment 3).

## Live run: 15 minutes, in five segments
The talk explains a step, then the demo shows it. The slides use only Test 01.

| # | After the slide | Time | Mode | What to show |
| :--- | :--- | :--- | :--- | :--- |
| 0 | *Infrastructure as Intent: the Prompt Is Not Enough* | 1 min | recorded | The Test 01 prompt in a workspace **without** `.kiro/`: Kiro guesses SSE-S3, no tags, a made-up name |
| 1 | *Intent Contract: An Example* | 3 min | live | Phase 0 of Test 01 |
| 2 | *Two Kiro Powers Against the Knowledge Cutoff* | 4 min | live (tasks sped up if slow) | Phase 1 of Test 01 |
| 3 | *The Validate Path in Our Pipeline* | 4 min | live | The gate: pass, fault, deny, regenerate, pass |
| 4 | *Human in the Loop, Gate in CI* | 2 min | recorded, sped up | Test 05, then `check.py` live |
| | | 1 min | | buffer |

### Before going on stage
- `tests/demo/reset.sh`; Kiro open on the workspace; `/mcp` shows the three servers running.
- AWS credentials of a sandbox account for `terraform plan` (no `apply`); `terraform init` already done in
  `tests/demo/test-01-s3-bucket/expected/terraform/garage-serverless/` to warm the provider cache.
- `build/tokens.prod.json` exported; recordings of Segments 0, 2 and 4 ready as fallback.

### Segment 1 · Phase 0 (Test 01)
1. Paste the Test 01 prompt.
2. Point out: golden path chosen, owner asked, **no** fields for "private, versioned, encrypted" (see `## Notes`).
3. Show `intents/garage-serverless/prod.md`: frontmatter, `## Request`, `## Decisions`; `validate.py` passed.
4. Confirm.

### Segment 2 · Phase 1 (Test 01)
1. Kiro creates `.kiro/specs/garage-serverless-prod/`: approve requirements and design.
2. Point out in the trace: `read_design_tokens` (governance, network, security, storage) and the Registry calls of
   `terraform-knowledge-guard`.
3. Execute the tasks; open `s3.tf`: five resources, values only from `environments/prod.tfvars`.

### Segment 3 · The gate (Test 01)
```bash
cd terraform/garage-serverless
terraform plan -var-file=environments/prod.tfvars -out tfplan && terraform show -json tfplan > tfplan.json
conftest test tfplan.json -p ../../policy --data ../../build/tokens.prod.json          # PASS
```
Fault: in `s3.tf` set `kms_master_key_id = "alias/aws/s3"`, plan again, `conftest` -> **FAIL** with the message.
Paste the message to Kiro: it restores `var.storage_kms_key_arn`; plan and `conftest` -> **PASS**.
Offline fallback: the two fixtures above.

### Segment 4 · Test 05
Recorded: `reset.sh`, the Test 05 prompt, the same questions, the whole application. Then live:
`.venv/bin/python tests/demo/check.py` -> *same contract: Test 05 (one prompt) == Test 04 (four prompts)*.

## Rehearsal
Run Tests 01 -> 04 in sequence, then `reset.sh` and Test 05. Tick the checklists in each `prompt.md`.
