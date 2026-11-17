# platform-mcp/server.py
import functools
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

# ------------------------------------------------------------------------------
# Logging: stderr (stdout is reserved for the MCP protocol) + log file.
# Level from env LOG_LEVEL (default DEBUG), file from env LOG_FILE.
# ------------------------------------------------------------------------------
LOG_FILE = os.environ.get("LOG_FILE", "/tmp/platform-context-engine.log")
log = logging.getLogger("platform-context-engine")
log.setLevel(os.environ.get("LOG_LEVEL", "DEBUG").upper())
_fmt = logging.Formatter("%(asctime)s %(levelname)s [pid=%(process)d] %(message)s")
for _h in (logging.StreamHandler(sys.stderr), logging.FileHandler(LOG_FILE)):
    _h.setFormatter(_fmt)
    log.addHandler(_h)
log.propagate = False

log.info("Module start: python=%s exe=%s cwd=%s", sys.version.split()[0], sys.executable, os.getcwd())
log.info("Argv=%s LOG_FILE=%s", sys.argv, LOG_FILE)

try:
    import yaml
    from mcp.server.mcpserver import MCPServer

    log.info("Import of yaml (%s) and mcp OK", getattr(yaml, "__version__", "n/a"))
except Exception:
    log.exception("Import of dependencies (yaml / mcp.server.mcpserver) FAILED")
    raise

# Initialise the MCP server (mcp 2.x: MCPServer, formerly FastMCP)
mcp = MCPServer("AWS-Platform-Context-Engine")
log.info("MCPServer instance created")

_orig_tool = mcp.tool


def _logged_tool(*t_args: Any, **t_kwargs: Any):
    """Like mcp.tool(), but logs input, duration and outcome of every call."""
    register = _orig_tool(*t_args, **t_kwargs)

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            start = time.monotonic()
            log.info("TOOL %s called args=%s kwargs=%s", fn.__name__, args, kwargs)
            try:
                result = fn(*args, **kwargs)
            except Exception:
                log.exception("TOOL %s exception after %.2fs", fn.__name__, time.monotonic() - start)
                raise
            text = result if isinstance(result, str) else repr(result)
            level = logging.WARNING if '"error"' in text[:200] else logging.INFO
            log.log(level, "TOOL %s ok in %.2fs (%d characters)%s", fn.__name__, time.monotonic() - start,
                    len(text), " [contains error]" if level == logging.WARNING else "")
            return result

        register(wrapper)
        log.debug("Tool registered: %s", fn.__name__)
        return fn

    return decorator


mcp.tool = _logged_tool  # type: ignore[method-assign]

TOKENS_BASE_PATH = Path(__file__).resolve().parent.parent / "tokens"
log.info("TOKENS_BASE_PATH=%s (exists=%s)", TOKENS_BASE_PATH, TOKENS_BASE_PATH.exists())

# Layout: tokens/_org/<domain>.yaml (company-wide values) -> tokens/<env>/<domain>.yaml (environment)
#         tokens/<env>/compute/<kind>.yaml (compute, one per golden path)
SHARED_DOMAINS = ("network", "security", "storage", "governance")
COMPUTE_KINDS = ("container-service", "kubernetes-cluster", "serverless-app")


def _load(path: Path) -> dict:
    if not path.exists():
        return {}
    with open(path) as f:
        return yaml.safe_load(f) or {}


def _merge(base: dict, override: dict) -> dict:
    """Recursive merge: environment values override company-wide ones."""
    out = dict(base)
    for key, value in override.items():
        out[key] = _merge(out[key], value) if isinstance(value, dict) and isinstance(out.get(key), dict) else value
    return out


def _error(message: str, **extra: Any) -> str:
    return json.dumps({"error": message, **extra}, indent=2)


# ==============================================================================
# TOOL: DYNAMIC CONTEXT (avoids context stuffing)
# ==============================================================================
@mcp.tool()
def read_design_tokens(domain: str, environment: str, kind: str = "") -> str:
    """
    Returns the company Design Tokens for one environment and one domain, on demand.
    - domain: network | security | storage | governance | compute
    - environment: dev | staging | prod (the intent's metadata.environment)
    - kind: required only for domain=compute: container-service | kubernetes-cluster
    Values are already merged: company-wide (tokens/_org) overridden by the environment's.
    """
    env_dir = TOKENS_BASE_PATH / environment
    if not env_dir.is_dir():
        available = sorted(p.name for p in TOKENS_BASE_PATH.iterdir() if p.is_dir() and not p.name.startswith("_"))
        return _error(f"No tokens for environment '{environment}'", available_environments=available)

    try:
        if domain == "compute":
            if kind not in COMPUTE_KINDS:
                return _error("domain=compute requires 'kind'", allowed_kinds=list(COMPUTE_KINDS))
            token_file = env_dir / "compute" / f"{kind}.yaml"
            if not token_file.exists():
                available = sorted(p.stem for p in (env_dir / "compute").glob("*.yaml"))
                return _error(f"No compute tokens '{kind}' for environment '{environment}'",
                              available_kinds=available)
            tokens = _load(token_file)
            sources = [str(token_file.relative_to(TOKENS_BASE_PATH))]
        elif domain in SHARED_DOMAINS:
            org_file = TOKENS_BASE_PATH / "_org" / f"{domain}.yaml"
            env_file = env_dir / f"{domain}.yaml"
            if not env_file.exists() and not org_file.exists():
                return _error(f"No '{domain}' tokens for environment '{environment}'")
            tokens = _merge(_load(org_file), _load(env_file))
            sources = [str(p.relative_to(TOKENS_BASE_PATH)) for p in (org_file, env_file) if p.exists()]
        else:
            return _error(f"Unknown domain '{domain}'", allowed_domains=[*SHARED_DOMAINS, "compute"])

        log.debug("read_design_tokens: domain=%s env=%s kind=%s sources=%s", domain, environment, kind, sources)
        return json.dumps({"environment": environment, "domain": domain, "kind": kind or None,
                           "sources": sources, "tokens": tokens}, indent=2)
    except Exception as e:
        log.exception("read_design_tokens: error (domain=%s env=%s kind=%s)", domain, environment, kind)
        return _error(f"Error reading tokens: {e}")


if __name__ == "__main__":
    # stdout is reserved for the MCP protocol: a print() here would corrupt it.
    log.info("MCP server starting (stdio transport)")
    try:
        mcp.run()
    except BaseException:
        log.exception("MCP server stopped with an error")
        raise
    finally:
        log.info("MCP server stopped")
