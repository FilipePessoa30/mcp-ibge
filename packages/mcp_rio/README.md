# mcp-rio

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for City of Rio de Janeiro open data (Data.Rio) — municipal datasets and indicators — planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package runs (`uv run mcp-rio`) and
> exposes the shared `status` tool — no data tool is implemented yet. See
> **[docs/modules/rio.md](../../docs/modules/rio.md)** for the
> full plan: data sources, planned tools and known challenges.

## What will mcp-rio be?

**mcp-rio** will expose official, public data from **Prefeitura do Rio de Janeiro - Data.Rio**
(<https://www.data.rio/>) as typed, traceable [MCP](https://modelcontextprotocol.io/)
tools, following the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_RIO_*` env vars).

## Try the scaffold

```bash
uv run mcp-rio
```

This starts the server with a single tool, `status`, which returns the
standard envelope without calling any external API — `data.module`,
`data.version`, `data.status` and `data.tools_implemented` (empty for now),
plus `metadata` pointing at Prefeitura do Rio de Janeiro - Data.Rio as the (future) source.

## Planned data sources

- **Data.Rio (CKAN)** — `https://www.data.rio/` — catálogo de datasets publicados pelas secretarias municipais do Rio de Janeiro.
- Integração futura com `mcp-ibge` (código IBGE do município do Rio de Janeiro: `3304557`) para cruzar indicadores municipais com dados do IBGE.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_datasets_rio` | Busca datasets no catálogo Data.Rio por termo ou secretaria. |
| 2 | `obter_dataset_rio` | Detalhes de um dataset do Data.Rio (recursos, formato, licença). |
| 3 | `listar_indicadores_municipais_rio` | Lista indicadores municipais já mapeados por este módulo. |

None of these are implemented yet — see
[docs/modules/rio.md](../../docs/modules/rio.md) for the detailed
design.

## Package layout

```
packages/mcp_rio/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_rio/
│   ├── server.py          # FastMCP instance, `status` tool registered
│   ├── config.py          # pydantic-settings (MCP_RIO_*)
│   ├── schemas/
│   │   └── common.py        # shared {ok, data, metadata, warnings, errors} envelope
│   ├── clients/            # planned: HTTP clients
│   ├── services/           # planned: business logic
│   ├── tools/
│   │   └── status_tools.py  # `status` tool (implemented)
│   └── utils/               # planned: shared helpers (cache, etc.)
└── tests/
    ├── test_server.py       # scaffold test: server boots, only `status` registered
    └── test_status_tools.py # contract test for the `status` tool
```

This mirrors [`mcp_ibge`](../mcp_ibge/)'s internal layering — see
[docs/architecture.md](../../docs/architecture.md#anatomy-of-a-module-package).

## Roadmap

See **[docs/modules/rio.md](../../docs/modules/rio.md)** for the
full plan, and [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-rio` fits
into the overall `mcp-data-br` roadmap.
