# Claude Desktop

All configurations use the `stdio` transport (the server's default) — Claude
Desktop spawns the server process and talks to it over stdin/stdout, with no
network ports opened.

## Config file location

| OS | Path |
| --- | --- |
| macOS | `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Windows | `%APPDATA%\Claude\claude_desktop_config.json` |
| Linux | `~/.config/Claude/claude_desktop_config.json` |

## macOS / Linux

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "ibge": {
      "command": "uvx",
      "args": ["mcp-ibge"]
    }
  }
}
```

`uvx` downloads and runs the `mcp-ibge` package in an isolated environment
(no repository checkout needed), once it's published to an index such as
PyPI. Until then, use [development mode](#development-mode).

## Windows

On Windows, commands like `uvx` usually need to be invoked through `cmd /c`
so Claude Desktop can find the executable:

```json title="claude_desktop_config.json"
{
  "mcpServers": {
    "ibge-windows": {
      "command": "cmd",
      "args": ["/c", "uvx", "mcp-ibge"]
    }
  }
}
```

If `uvx`/`uv` aren't on the `PATH` of the Claude Desktop process, use the
absolute path to the executable (e.g.
`"C:\\Users\\<user>\\.local\\bin\\uv.exe"` as `command`, with
`args: ["run", ...]` instead of `cmd /c uvx ...`).

## Development mode

To run from source (without publishing the package), point `uv` at the
project directory and run the server module directly:

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

`--directory` must point at the **root of the `mcp-data-br` repository**
(where the workspace `pyproject.toml` lives — `mcp-ibge` is installed as a
workspace member). On Windows, use a path with forward slashes or doubled
backslashes, e.g. `"C:/path/to/mcp-data-br"` or `"C:\\path\\to\\mcp-data-br"`.

A ready-to-use file with all three variants is available at
[`examples/claude_desktop/mcp_ibge.json`](https://github.com/FilipePessoa30/mcp-data-br/blob/main/examples/claude_desktop/mcp_ibge.json).

## Restart the client

After editing the config file, restart Claude Desktop so the server starts
and its tools become available in conversations.

## Test prompts

Use these natural-language prompts to validate the connection — see
[`examples/agent_recipes/mcp_ibge_queries.md`](https://github.com/FilipePessoa30/mcp-data-br/blob/main/examples/agent_recipes/mcp_ibge_queries.md)
for the equivalent tool calls and more examples:

1. "List the Brazilian states."
2. "What is the IBGE code for Niterói, RJ?"
3. "List the municipalities of Rio de Janeiro state."
4. "Search for municipalities named São José."
5. "Get metadata for a SIDRA aggregate (e.g. aggregate 6579)."
6. "List the variables of a SIDRA aggregate (e.g. aggregate 6579)."
7. "Compare the population of Rio de Janeiro and Niterói."

The last prompt can also be triggered directly as the `comparar_municipios`
MCP prompt, which guides the model to cite source, period, territorial unit
and limitations in its answer.

## Limitations

- **Depends on the official IBGE API**: all data comes live from
  `servicodados.ibge.gov.br` (no API key). Outages or schema changes affect
  the server's responses directly — see
  [Data Sources & Response Format](../data_sources.md).
- **SIDRA aggregates require context**: `consultar_agregado` mirrors SIDRA's
  query syntax. Use `listar_agregados`, `obter_metadados_agregado`,
  `listar_variaveis_agregado`, `listar_periodos_agregado` and
  `listar_localidades_agregado` first to discover the right IDs — see
  [Tools → Agregados/SIDRA](../tools/agregados.md).
- **Verify before official use**: responses include `metadata` (source,
  endpoint, parameters, retrieval time) and, where relevant, `warnings`
  about ambiguities or methodological caveats. Use these fields to check
  numbers against the official source before relying on them in reports or
  decisions.
