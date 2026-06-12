# Getting Started

This page gets you from a fresh clone to a working MCP server in a few
minutes, using the `mcp-ibge` module (the first module in `mcp-data-br`).

## Prerequisites

- **Python 3.11+**
- **[uv](https://docs.astral.sh/uv/)** — the workspace's package/dependency
  manager and task runner.

## 1. Clone and sync

```bash
git clone https://github.com/FilipePessoa30/mcp-data-br.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
```

`uv sync --all-extras` installs every package under `packages/` (currently
`mcp-ibge`) plus dev/docs dependencies into a single shared `.venv` at the
repository root.

> 🇧🇷 **Nota**: `mcp-data-br` é um *workspace* uv (monorepo) — `uv sync` na
> raiz instala todos os módulos de uma vez, sem precisar de `--package`.

## 2. Run the server

```bash
uv run mcp-ibge
# equivalent:
uv run python -m mcp_ibge.server
```

This starts the server over **stdio** — the recommended transport for
Claude Desktop, Cursor and other local MCP clients. Logs are written to
**stderr** as structured JSON lines; `stdout` is reserved for the MCP
protocol. Press `Ctrl+C` to stop.

## 3. Connect an MCP client

Point your client at the local checkout. For Claude Desktop, add this to
`claude_desktop_config.json` (see [Installation](installation.md) for the
exact file path per OS):

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "ibge-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-data-br",
        "run",
        "python",
        "-m",
        "mcp_ibge.server"
      ]
    }
  }
}
```

Restart the client. See [Clients](clients/claude-desktop.md) for Cursor and
Open WebUI, and [Installation](installation.md) for the published-package
(`uvx`) form once `mcp-ibge` is on PyPI.

## 4. Try a prompt

Once connected, ask in natural language:

> "Compare Rio de Janeiro, Niterói and Maricá using official Brazilian
> public data."

The agent will resolve each municipality via `obter_codigo_municipio`, then
call `comparar_municipios` once to return a table with sources cited. See
[Compare Municipalities](examples/compare-municipalities.md) for the full
walkthrough, or [Tools → Localidades](tools/localidades.md) and
[Tools → Agregados/SIDRA](tools/agregados.md) for the individual tools.

## 5. Check server status

The `mcp-data-br://status` resource reports the server version, registered
tools, cache configuration, request metrics and data sources — useful for
verifying your setup:

```json
{
  "ok": true,
  "data": {
    "version": "0.2.0",
    "tools_registered": 27,
    "cache": { "enabled": true, "ttl_seconds": 3600.0, "max_size": 256, "size": 3 },
    "metrics": {
      "total_requests": 12,
      "cache_hits": 4,
      "cache_misses": 8,
      "errors": 0,
      "cache_hit_rate": 0.33,
      "average_latency_ms": 142.5
    },
    "uptime_seconds": 87.2,
    "data_sources": ["IBGE - Instituto Brasileiro de Geografia e Estatística"]
  }
}
```

## Next steps

- [Installation](installation.md) — all configuration options
  (`MCP_IBGE_*` / `MCP_DATA_BR_*` environment variables).
- [Modules → mcp-ibge](modules/ibge.md) — full feature list.
- [Examples](examples/municipal-profile.md) — more ready-to-use prompts.
- [Contributing](contributing.md) — running tests, linting, and adding tools.
