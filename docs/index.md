# mcp-data-br docs

`mcp-data-br` is a collection of [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) servers for Brazilian public data, organized as a single uv workspace
(monorepo) where each data source gets its own package under
[`packages/`](../packages/).

This directory documents the **monorepo as a whole** — how it's structured,
the conventions every module follows, and where the project is headed.
Module-specific documentation (tools reference, setup, etc.) lives inside
each package, e.g. [packages/mcp_ibge/docs/](../packages/mcp_ibge/docs/).

## Start here

- [architecture.md](architecture.md) — how the workspace and packages are
  organized, and the conventions a new module must follow.
- [data_sources.md](data_sources.md) — the shared response envelope
  (`metadata`/`data`/`error`/`warnings`) used by every module, and a registry
  of data sources per module.
- [security.md](security.md) — the security baseline every module is built
  on (no shell execution, no arbitrary file/URL access, domain allowlists,
  input validation, timeouts, response size limits).
- [roadmap.md](roadmap.md) — current and planned modules.

## Current modules

| Module | Status | Data source | Docs |
| --- | --- | --- | --- |
| [`mcp-ibge`](../packages/mcp_ibge/) | Stable | IBGE (Localidades, Agregados/SIDRA) | [README](../packages/mcp_ibge/README.md) · [docs](../packages/mcp_ibge/docs/) |

See [roadmap.md](roadmap.md) for planned modules.

## Other resources

- [examples/](../examples/) — ready-to-use MCP client configs (Claude
  Desktop, Cursor, Open WebUI) and example prompts.
- [evals/](../evals/) — evaluation datasets and reports for measuring tool
  quality over time.
- [CONTRIBUTING.md](../CONTRIBUTING.md) — how to set up the workspace and
  contribute.
