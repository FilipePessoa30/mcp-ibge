# mcp-tesouro

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for Brazilian National Treasury fiscal data (Tesouro Transparente / SICONFI) — federal, state and municipal finances — planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package runs (`uv run mcp-tesouro`) and
> exposes the shared `status` tool — no data tool is implemented yet. See
> **[docs/modules/tesouro.md](../../docs/modules/tesouro.md)** for the
> full plan: data sources, planned tools and known challenges.

## What will mcp-tesouro be?

**mcp-tesouro** will expose official, public data from **Tesouro Nacional - Tesouro Transparente**
(<https://www.tesourotransparente.gov.br/>) as typed, traceable [MCP](https://modelcontextprotocol.io/)
tools, following the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_TESOURO_*` env vars).

## Try the scaffold

```bash
uv run mcp-tesouro
```

This starts the server with a single tool, `status`, which returns the
standard envelope without calling any external API — `data.module`,
`data.version`, `data.status` and `data.tools_implemented` (empty for now),
plus `metadata` pointing at Tesouro Nacional - Tesouro Transparente as the (future) source.

## Planned data sources

- **API de Dados Abertos do SICONFI** — `https://apidatalake.tesouro.gov.br/ords/siconfi/tt/...` — RREO, RGF, dívida e finanças de União, estados e municípios.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `consultar_financas_municipio` | Consulta indicadores fiscais (RREO/RGF) de um município por ano. |
| 2 | `consultar_divida_estado` | Consulta a dívida pública de um estado por ano. |
| 3 | `listar_relatorios_disponiveis` | Lista relatórios fiscais (RREO/RGF) disponíveis por ente/período. |

None of these are implemented yet — see
[docs/modules/tesouro.md](../../docs/modules/tesouro.md) for the detailed
design.

## Package layout

```
packages/mcp_tesouro/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_tesouro/
│   ├── server.py          # FastMCP instance, `status` tool registered
│   ├── config.py          # pydantic-settings (MCP_TESOURO_*)
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

See **[docs/modules/tesouro.md](../../docs/modules/tesouro.md)** for the
full plan, and [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-tesouro` fits
into the overall `mcp-data-br` roadmap.
