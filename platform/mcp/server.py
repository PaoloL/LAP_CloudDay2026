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
# Logging: stderr (stdout e' riservato al protocollo MCP) + file di log.
# Livello con env LOG_LEVEL (default DEBUG), file con env LOG_FILE.
# ------------------------------------------------------------------------------
LOG_FILE = os.environ.get("LOG_FILE", "/tmp/platform-context-engine.log")
log = logging.getLogger("platform-context-engine")
log.setLevel(os.environ.get("LOG_LEVEL", "DEBUG").upper())
_fmt = logging.Formatter("%(asctime)s %(levelname)s [pid=%(process)d] %(message)s")
for _h in (logging.StreamHandler(sys.stderr), logging.FileHandler(LOG_FILE)):
    _h.setFormatter(_fmt)
    log.addHandler(_h)
log.propagate = False

log.info("Avvio modulo: python=%s exe=%s cwd=%s", sys.version.split()[0], sys.executable, os.getcwd())
log.info("Argv=%s LOG_FILE=%s", sys.argv, LOG_FILE)

try:
    import yaml
    from mcp.server.mcpserver import MCPServer

    log.info("Import yaml (%s) e mcp OK", getattr(yaml, "__version__", "n/d"))
except Exception:
    log.exception("Import delle dipendenze (yaml / mcp.server.mcpserver) FALLITO")
    raise

# Inizializza il server MCP (mcp 2.x: MCPServer, ex FastMCP)
mcp = MCPServer("AWS-Platform-Context-Engine")
log.info("Istanza MCPServer creata")

_orig_tool = mcp.tool


def _logged_tool(*t_args: Any, **t_kwargs: Any):
    """Come mcp.tool(), ma logga ingresso, durata ed esito di ogni chiamata."""
    register = _orig_tool(*t_args, **t_kwargs)

    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            start = time.monotonic()
            log.info("TOOL %s chiamato args=%s kwargs=%s", fn.__name__, args, kwargs)
            try:
                result = fn(*args, **kwargs)
            except Exception:
                log.exception("TOOL %s eccezione dopo %.2fs", fn.__name__, time.monotonic() - start)
                raise
            text = result if isinstance(result, str) else repr(result)
            level = logging.WARNING if '"error"' in text[:200] else logging.INFO
            log.log(level, "TOOL %s ok in %.2fs (%d caratteri)%s", fn.__name__, time.monotonic() - start,
                    len(text), " [contiene error]" if level == logging.WARNING else "")
            return result

        register(wrapper)
        log.debug("Tool registrato: %s", fn.__name__)
        return fn

    return decorator


mcp.tool = _logged_tool  # type: ignore[method-assign]

TOKENS_BASE_PATH = Path(__file__).resolve().parent.parent / "tokens"
log.info("TOKENS_BASE_PATH=%s (esiste=%s)", TOKENS_BASE_PATH, TOKENS_BASE_PATH.exists())

# Alias ambiente -> nome file token (prod e' salvato in prd.yaml)
ENVIRONMENT_ALIASES = {"prod": "prd"}

# ==============================================================================
# TOOL 1: DYNAMIC CONTEXT (Risolve Context Stuffing)
# ==============================================================================
@mcp.tool()
def read_design_tokens(domain: str, environment: str) -> str:
    """
    Recupera on-demand i Design Tokens aziendali (VPC, Subnet, KMS Key ARN, Naming)
    per uno specifico ambiente (dev, staging, prod) e dominio (storage, network, compute).
    Evita di caricare tutti i file nel prompt.
    """
    token_file = TOKENS_BASE_PATH / f"{ENVIRONMENT_ALIASES.get(environment, environment)}.yaml"
    log.debug("read_design_tokens: file token=%s", token_file)
    if not token_file.exists():
        log.warning("read_design_tokens: file token inesistente: %s", token_file)
        return json.dumps({"error": f"Nessun token trovato per l'ambiente '{environment}'"})

    try:
        with open(token_file, "r") as f:
            data = yaml.safe_load(f)

        # Filtra per dominio se richiesto, o restituisce il blocco per intero
        if domain not in data:
            log.warning("read_design_tokens: dominio '%s' assente, domini disponibili=%s; restituisco tutto",
                        domain, list(data))
        result = data.get(domain, data)
        return json.dumps({
            "environment": environment,
            "domain": domain,
            "tokens": result
        }, indent=2)
    except Exception as e:
        log.exception("read_design_tokens: errore nella lettura di %s", token_file)
        return json.dumps({"error": f"Errore nella lettura dei token: {str(e)}"})


if __name__ == "__main__":
    # stdout è riservato al protocollo MCP: un print() qui lo corromperebbe.
    log.info("MCP Server in avvio (transport stdio)")
    try:
        mcp.run()
    except BaseException:
        log.exception("MCP Server terminato con errore")
        raise
    finally:
        log.info("MCP Server terminato")
