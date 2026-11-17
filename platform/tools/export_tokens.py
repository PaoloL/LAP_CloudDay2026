"""Exports the merged Design Tokens of one environment as JSON, for OPA / Conftest (--data).

One source of truth: the same files and the same merge as the MCP server `platform-context-engine`
(tokens/_org/<domain> overridden by tokens/<env>/<domain>; tokens/<env>/compute/<kind>.yaml as is).
Generation reads them through MCP, validation reads them here: change a token once, both sides follow.

Usage (from the workspace root):
    python3 platform/tools/export_tokens.py prod > build/tokens.prod.json
Policies read them as data.tokens.<domain>..., e.g. data.tokens.security.kms_keys.storage_key_arn.
"""
import json
import sys
from pathlib import Path

import yaml

TOKENS = Path(__file__).resolve().parents[2] / "platform/tokens"
SHARED_DOMAINS = ("network", "security", "storage", "governance")


def _load(path: Path) -> dict:
    return (yaml.safe_load(path.read_text()) or {}) if path.exists() else {}


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def export(environment: str) -> dict:
    env_dir = TOKENS / environment
    if not env_dir.is_dir():
        available = sorted(p.name for p in TOKENS.iterdir() if p.is_dir() and not p.name.startswith("_"))
        raise SystemExit(f"no tokens for environment '{environment}': available {available}")
    tokens = {"environment": environment}
    for d in SHARED_DOMAINS:
        tokens[d] = _merge(_load(TOKENS / "_org" / f"{d}.yaml"), _load(env_dir / f"{d}.yaml"))
    tokens["compute"] = {f.stem: _load(f) for f in sorted((env_dir / "compute").glob("*.yaml"))}
    return {"tokens": tokens}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: export_tokens.py <environment>")
    json.dump(export(sys.argv[1]), sys.stdout, indent=2)
    sys.stdout.write("\n")
