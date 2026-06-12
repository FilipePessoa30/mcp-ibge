# Installation

`mcp-data-br` is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
(monorepo). The first module, `mcp-ibge`, requires **Python 3.11+**.

## Option 1 — `uvx` (published package)

```bash
uvx mcp-ibge
```

> ⚠️ While `mcp-ibge` is not yet published to PyPI, use
> [Option 2 (development mode)](#option-2-development-mode-recommended-for-now) and point your
> MCP client at the local checkout instead.

Minimal MCP client config once published:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uvx",
      "args": ["mcp-ibge"]
    }
  }
}
```

## Option 2 — Development mode (recommended for now)

Clone the repository and sync the whole workspace from its root:

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
```

Run it directly from the repository root:

```bash
uv run mcp-ibge
# or, equivalent:
uv run python -m mcp_ibge.server
```

Point your MCP client at the local checkout using `uv --directory`:

```json
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

On Windows, use an absolute path with forward or doubled-backslashes, e.g.
`"C:/path/to/mcp-data-br"` or `"C:\\path\\to\\mcp-data-br"`.

## Option 3 — `streamable-http` (for HTTP-based clients)

For HTTP-based clients (e.g. [Open WebUI](clients/open-webui.md) via
[`mcpo`](https://github.com/open-webui/mcpo)), start the server with the
`streamable-http` transport:

```bash
MCP_IBGE_TRANSPORT=streamable-http MCP_IBGE_PORT=8000 uv run mcp-ibge
```

`streamable-http` is intended for **local/trusted use** — see
[Security](security.md#transports).

## Configuration

All settings have sensible defaults and can be overridden via environment
variables (prefix `MCP_IBGE_`) or a `.env` file — copy
[`packages/mcp_ibge/.env.example`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/.env.example)
to `.env` and adjust as needed.

Cache and log level can also be set via shared `MCP_DATA_BR_*` names — useful
for configuring every `mcp-data-br` module the same way. If both a
`MCP_DATA_BR_*` and a `MCP_IBGE_*` variable are set, `MCP_DATA_BR_*` takes
precedence.

| Variable | Default | Description |
| --- | --- | --- |
| `MCP_IBGE_API_BASE_URL` | `https://servicodados.ibge.gov.br/api` | Base URL shared by the IBGE APIs. Restricted to official IBGE domains — see [Security](security.md). |
| `MCP_IBGE_SOURCE_NAME` | `IBGE - Instituto Brasileiro de Geografia e Estatística` | Name shown in `metadata.source_name`. |
| `MCP_IBGE_OFFICIAL_SOURCE_URL` | `https://www.ibge.gov.br/` | Institutional URL shown in `metadata.official_source`. |
| `MCP_IBGE_LICENSE_NOTE` | _(see `.env.example`)_ | License/usage note shown in `metadata.license_note`. |
| `MCP_IBGE_USER_AGENT` | `mcp-ibge/0.2.0` | `User-Agent` header used for IBGE requests. |
| `MCP_IBGE_TIMEOUT` | `30.0` | HTTP timeout (seconds) for each IBGE request. |
| `MCP_IBGE_MAX_RESPONSE_SIZE_BYTES` | `5000000` | Maximum response body size (bytes) accepted from the IBGE API. |
| `MCP_DATA_BR_ENABLE_CACHE` / `MCP_IBGE_CACHE_ENABLED` | `true` | Enable/disable the in-memory cache. |
| `MCP_DATA_BR_CACHE_TTL_SECONDS` / `MCP_IBGE_CACHE_TTL_SECONDS` | `3600.0` | Cache entry time-to-live (seconds). |
| `MCP_IBGE_CACHE_MAX_SIZE` | `256` | Maximum number of cached responses. |
| `MCP_DATA_BR_LOG_LEVEL` / `MCP_IBGE_LOG_LEVEL` | `INFO` | Log level (`DEBUG`, `INFO`, ...); always written to `stderr` as structured JSON lines. |
| `MCP_IBGE_TRANSPORT` | `stdio` | MCP transport (`stdio` or `streamable-http`). |
| `MCP_IBGE_PORT` | `8000` | Port used by the `streamable-http` transport. |

Example `.env`:

```bash title=".env"
MCP_IBGE_TIMEOUT=30.0
MCP_DATA_BR_ENABLE_CACHE=true
MCP_DATA_BR_CACHE_TTL_SECONDS=3600.0
MCP_DATA_BR_LOG_LEVEL=INFO
MCP_IBGE_TRANSPORT=stdio
```

## Next steps

- [Clients](clients/claude-desktop.md) — full client setup for Claude
  Desktop, Cursor and Open WebUI.
- [Getting Started](getting-started.md) — first run and first prompt.
