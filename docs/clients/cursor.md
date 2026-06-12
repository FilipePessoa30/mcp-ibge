# Cursor

In Cursor, go to **Settings → MCP → Add new MCP Server**, or edit
`~/.cursor/mcp.json` directly. The format is the same `mcpServers` object
used by Claude Desktop.

## macOS / Linux (published package)

```json title="mcp.json"
{
  "mcpServers": {
    "ibge": {
      "command": "uvx",
      "args": ["mcp-ibge"]
    }
  }
}
```

> ⚠️ While `mcp-ibge` is not yet published to PyPI, use
> [development mode](#development-mode) below.

## Windows

```json title="mcp.json"
{
  "mcpServers": {
    "ibge-windows": {
      "command": "cmd",
      "args": ["/c", "uvx", "mcp-ibge"]
    }
  }
}
```

## Development mode

Point `uv --directory` at the repository root and run the `mcp-ibge` console
script (or the module directly):

```json title="mcp.json"
{
  "mcpServers": {
    "ibge-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/mcp-data-br",
        "run",
        "mcp-ibge"
      ]
    }
  }
}
```

A ready-to-use file with all three variants is available at
[`examples/cursor/mcp_ibge.json`](https://github.com/FilipePessoa30/mcp-data-br/blob/main/examples/cursor/mcp_ibge.json).

## Reload the window

After editing `mcp.json`, reload the Cursor window so the server starts and
its tools become available in conversations.

## Test prompts

Same prompts as [Claude Desktop](claude-desktop.md#test-prompts) — e.g. "List
the Brazilian states", "What is the IBGE code for Niterói, RJ?", "Compare the
population of Rio de Janeiro and Niterói."

## Limitations

Same as [Claude Desktop](claude-desktop.md#limitations) — `mcp-ibge` depends
on the live `servicodados.ibge.gov.br` API, SIDRA aggregates require
discovery via the [Agregados/SIDRA tools](../tools/agregados.md), and all
values should be checked against `metadata`/`warnings` before official use.
