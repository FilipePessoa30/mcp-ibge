# Open WebUI

[Open WebUI](https://github.com/open-webui/open-webui) talks to tools over
OpenAPI, not MCP directly, so the recommended bridge is
[`mcpo`](https://github.com/open-webui/mcpo) — a small proxy that turns any
MCP server into an OpenAPI server.

## Option 1: `mcpo` + stdio (recommended)

Run `mcpo` with the bundled [`mcpo_config.json`](mcpo_config.json), which
starts `mcp-ibge` over stdio (the default transport):

```bash
uvx mcpo --config mcpo_config.json --port 8000
```

This exposes the `mcp-ibge` tools at `http://localhost:8000/ibge` with an
OpenAPI schema at `http://localhost:8000/ibge/openapi.json`. In Open WebUI,
add a new tool server pointing at that URL.

## Option 2: `streamable-http` transport

`mcp-ibge` can also run as a standalone `streamable-http` server:

```bash
MCP_IBGE_TRANSPORT=streamable-http MCP_IBGE_PORT=8000 uv run mcp-ibge
```

Use this if your client (or `mcpo`) connects to MCP servers over HTTP
instead of spawning them via stdio. The `streamable-http` transport is meant
for local/trusted use — see
[packages/mcp_ibge/docs/security.md](../../packages/mcp_ibge/docs/security.md).

## See also

- [packages/mcp_ibge/docs/client_setup.md](../../packages/mcp_ibge/docs/client_setup.md) —
  Claude Desktop and Cursor setup
- [examples/agent_recipes/mcp_ibge_queries.md](../agent_recipes/mcp_ibge_queries.md) —
  example prompts to try once the server is connected
