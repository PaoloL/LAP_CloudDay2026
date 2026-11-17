"""Validates intents and Design Tokens against the golden path schemas.

Usage (from the workspace root):
    .venv/bin/python platform/tools/validate.py              # all intents, examples and tokens
    .venv/bin/python platform/tools/validate.py intents/x/dev.md

Intents are Markdown files with YAML frontmatter:
  - frontmatter (machines): apiVersion, kind, metadata, spec. The schema is chosen from kind + apiVersion
    (platform/golden-paths/<kind-slug>/<version>/intent.schema.json);
  - body (humans and LLMs): a '## Request' section with the request in natural language and a
    '## Decisions' table (the living ADR) whose 'Field' column names fields that exist in the frontmatter.
  The path must be intents/<metadata.name>/<metadata.environment>.md.
Tokens: for each environment, the merge of tokens/_org/<domain> + tokens/<env>/<domain> against
  golden-paths/_common/tokens/<domain>.schema.json, and tokens/<env>/compute/<kind>.yaml against
  golden-paths/<kind>/<version>/tokens.schema.json.
Exits with code 1 if anything is invalid: suitable for CI.
"""
import json
import re
import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

ROOT = Path(__file__).resolve().parents[2]
GP = ROOT / "platform/golden-paths"
TOKENS = ROOT / "platform/tokens"
KIND_DIRS = {
    "ContainerService": "container-service",
    "KubernetesCluster": "kubernetes-cluster",
    "ServerlessApplication": "serverless-app",
}
SHARED_DOMAINS = ("network", "security", "storage", "governance")
REQUIRED_SECTIONS = ("Request", "Decisions")
DECISION_SOURCES = ("request", "default", "confirmed", "platform")


def _schema(path: Path) -> dict:
    return json.loads(path.read_text())


REGISTRY = Registry().with_resources(
    (s["$id"], Resource.from_contents(s))
    for s in (_schema(p) for p in GP.rglob("*.schema.json"))
    if "$id" in s
)


def _errors(schema: dict, data) -> list[str]:
    v = Draft202012Validator(schema, registry=REGISTRY)
    return [
        f"{'.'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
        for e in sorted(v.iter_errors(data), key=lambda e: list(e.absolute_path))
    ]


def _yaml(path: Path):
    return yaml.safe_load(path.read_text()) or {}


def _split_intent(path: Path) -> tuple[dict, str]:
    """Splits an intent into (frontmatter, body). Raises ValueError if the frontmatter is missing."""
    text = path.read_text()
    m = re.match(r"\A---[ \t]*\n(.*?)\n---[ \t]*(?:\n|\Z)(.*)\Z", text, re.S)
    if not m:
        raise ValueError("missing YAML frontmatter: the file must start with '---', the YAML, then '---'")
    data = yaml.safe_load(m.group(1)) or {}
    if not isinstance(data, dict):
        raise ValueError("the frontmatter must be a YAML mapping")
    return data, m.group(2)


def _sections(body: str) -> dict[str, str]:
    parts = re.split(r"^##[ \t]+(.+?)[ \t]*$", body, flags=re.M)
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def _has_path(data, dotted: str) -> bool:
    for key in dotted.split("."):
        if not isinstance(data, dict) or key not in data:
            return False
        data = data[key]
    return True


def check_body(data: dict, body: str) -> list[str]:
    """The prose part: the request and the decision log, traceable to the frontmatter."""
    errs = []
    sections = _sections(body)
    for name in REQUIRED_SECTIONS:
        if not sections.get(name):
            errs.append(f"body: missing or empty '## {name}' section")
    rows = [r for r in sections.get("Decisions", "").splitlines() if r.strip().startswith("|")]
    rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows[2:]]  # skip header + separator
    if sections.get("Decisions") and not rows:
        errs.append("body: '## Decisions' needs a table: | Field | Value | Source | Rationale |")
    for cells in rows:
        if len(cells) < 4:
            errs.append(f"body: decision row with {len(cells)} columns, expected 4: {' | '.join(cells)}")
            continue
        field, source = cells[0].strip("`"), cells[2].strip("`").lower()
        if not _has_path(data, field):
            errs.append(f"body: decision on '{field}', which is not in the frontmatter")
        if source not in DECISION_SOURCES:
            errs.append(f"body: decision on '{field}' has source '{cells[2]}': allowed {list(DECISION_SOURCES)}")
    return errs


def _merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in override.items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def check_intent(path: Path, check_path: bool = True) -> list[str]:
    if path.suffix != ".md":
        return [f"intents are Markdown files with YAML frontmatter: expected a .md file, found '{path.suffix}'"]
    try:
        data, body = _split_intent(path)
    except yaml.YAMLError as exc:
        return [f"invalid YAML in the frontmatter: {exc}"]
    except ValueError as exc:
        return [str(exc)]
    kind, api = data.get("kind"), str(data.get("apiVersion", ""))
    if kind not in KIND_DIRS:
        return [f"unknown kind '{kind}': allowed {sorted(KIND_DIRS)}"]
    version = api.rsplit("/", 1)[-1]
    schema_path = GP / KIND_DIRS[kind] / version / "intent.schema.json"
    if not schema_path.exists():
        available = sorted(p.parent.name for p in (GP / KIND_DIRS[kind]).glob("*/intent.schema.json"))
        return [f"apiVersion '{api}' not available for {kind}: versions {available}"]
    errs = _errors(_schema(schema_path), data) + check_body(data, body)
    meta = data.get("metadata") or {}
    if check_path:
        expected = Path("intents") / str(meta.get("name")) / f"{meta.get('environment')}.md"
        try:
            rel = path.resolve().relative_to(ROOT)
        except ValueError:
            rel = path
        if rel != expected:
            errs.append(f"path: expected {expected}, found {rel}")
    env = meta.get("environment")
    if env and not (TOKENS / env).is_dir():
        errs.append(f"no tokens for environment '{env}' (platform/tokens/{env}/)")
    elif env and not (TOKENS / env / "compute" / f"{KIND_DIRS[kind]}.yaml").exists():
        errs.append(f"no compute/{KIND_DIRS[kind]}.yaml tokens for environment '{env}'")
    return errs


def check_tokens() -> dict[str, list[str]]:
    results = {}
    for env_dir in sorted(p for p in TOKENS.iterdir() if p.is_dir() and not p.name.startswith("_")):
        for d in SHARED_DOMAINS:
            merged = _merge(_yaml(TOKENS / "_org" / f"{d}.yaml") if (TOKENS / "_org" / f"{d}.yaml").exists() else {},
                            _yaml(env_dir / f"{d}.yaml") if (env_dir / f"{d}.yaml").exists() else {})
            results[f"tokens/{env_dir.name}/{d}"] = _errors(_schema(GP / "_common/tokens" / f"{d}.schema.json"), merged)
        for f in sorted((env_dir / "compute").glob("*.yaml")):
            schemas = sorted((GP / f.stem).glob("*/tokens.schema.json"))
            key = f"tokens/{env_dir.name}/compute/{f.stem}"
            if not schemas:
                results[key] = [f"no golden path '{f.stem}'"]
                continue
            data = _yaml(f)
            errs = _errors(_schema(schemas[-1]), data)
            net = _merge({}, _yaml(env_dir / "network.yaml")) if (env_dir / "network.yaml").exists() else {}
            zone = data.get("single_az_zone")
            tier = data.get("node_subnet_tier")
            if zone and tier and zone not in (net.get("subnets", {}).get(tier) or {}):
                errs.append(f"single_az_zone '{zone}' not found in network.subnets.{tier}")
            results[key] = errs
    return results


def main(argv: list[str]) -> int:
    results: dict[str, list[str]] = {}
    if argv:
        for a in argv:
            results[a] = check_intent(Path(a))
    else:
        for f in sorted((ROOT / "intents").glob("*/*.md")):
            results[str(f.relative_to(ROOT))] = check_intent(f)
        for f in sorted(GP.glob("*/*/examples/*.md")):
            results[str(f.relative_to(ROOT))] = check_intent(f, check_path=False)
        for f in sorted((ROOT / "tests/demo").glob("*/intent.md")):  # expected contracts of the demo tests
            results[str(f.relative_to(ROOT))] = check_intent(f, check_path=False)
        results.update(check_tokens())
    for name, errs in results.items():
        print(f"{'OK  ' if not errs else 'FAIL'} {name}")
        for e in errs:
            print(f"     - {e}")
    return 1 if any(results.values()) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
