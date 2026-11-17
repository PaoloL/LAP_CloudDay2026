#!/usr/bin/env bash
# Resets the workspace before Test 01 or Test 05: removes what Kiro generated for garage-serverless.
set -euo pipefail
cd "$(dirname "$0")/../.."
rm -rf intents/garage-serverless terraform/garage-serverless .kiro/specs/garage-serverless-prod
echo "Clean: no intent, spec or Terraform for garage-serverless."
