"""Consistency checks of the demo tests, offline (no AWS, no Kiro).

    python3 tests/demo/check.py

1. Every expected intent (tests/demo/*/intent.md) passes platform/tools/validate.py.
2. Same contract, whatever the path: the Test 05 frontmatter (one prompt) equals Test 04 (four prompts).
3. Fidelity to the tokens: Test 01 expected prod.tfvars holds exactly the prod Design Tokens.
Exit code 1 on any failure.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "platform/tools"))
import export_tokens  # noqa: E402
import validate  # noqa: E402

DEMO = ROOT / "tests/demo"
failures = []

for f in sorted(DEMO.glob("*/intent.md")):
    errs = validate.check_intent(f, check_path=False)
    failures += [f"{f.relative_to(ROOT)}: {e}" for e in errs]
    print(f"{'OK  ' if not errs else 'FAIL'} contract  {f.parent.name}")

t04, _ = validate._split_intent(DEMO / "test-04-api-gateway/intent.md")
t05, _ = validate._split_intent(DEMO / "test-05-entire-app/intent.md")
same = t04 == t05
print(f"{'OK  ' if same else 'FAIL'} same contract: Test 05 (one prompt) == Test 04 (four prompts)")
if not same:
    failures.append("Test 05 frontmatter differs from Test 04")

tok = export_tokens.export("prod")["tokens"]
expected = {
    "environment": "prod",
    "aws_region": tok["network"]["aws_region"],
    "naming_mask": tok["governance"]["naming_mask"],
    "storage_kms_key_arn": tok["security"]["kms_keys"]["storage_key_arn"],
    "s3_versioning_status": tok["storage"]["s3"]["versioning_status"],
    "s3_force_destroy": str(tok["storage"]["s3"]["force_destroy"]).lower(),
    "audit_log_bucket": tok["storage"]["s3"]["audit_log_target_bucket"],
}
tfvars = (DEMO / "test-01-s3-bucket/expected/terraform/garage-serverless/environments/prod.tfvars").read_text()
values = dict(re.findall(r'^(\w+)\s*=\s*"?([^"\n]*?)"?\s*$', tfvars, re.M))
tags = dict(re.findall(r"^[ \t]+(\w+)[ \t]*=[ \t]*\"([^\"]*)\"", tfvars, re.M))
for k, v in expected.items():
    if values.get(k) != v:
        failures.append(f"prod.tfvars {k} = {values.get(k)!r}, token says {v!r}")
if tags != tok["governance"]["default_tags"]:
    failures.append(f"prod.tfvars default_tags {tags} != token {tok['governance']['default_tags']}")
print(f"{'OK  ' if not [x for x in failures if 'prod.tfvars' in x] else 'FAIL'} Test 01 prod.tfvars == prod Design Tokens")

for f in failures:
    print(f"     - {f}")
sys.exit(1 if failures else 0)
