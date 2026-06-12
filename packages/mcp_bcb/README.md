# mcp-bcb

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for Banco Central do Brasil economic and financial indicators (SGS time series, exchange rates, Selic) — planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package runs (`uv run mcp-bcb`) and
> exposes the shared `status` tool — no data tool is implemented yet. See
> **[docs/modules/bcb.md](../../docs/modules/bcb.md)** for the
> full plan: data sources, planned tools and known challenges.

## What will mcp-bcb be?

**mcp-bcb** will expose official, public data from **Banco Central do Brasil**
(<https://www.bcb.gov.br/>) as typed, traceable [MCP](https://modelcontextprotocol.io/)
tools, following the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_BCB_*` env vars).

## Try the scaffold

```bash
uv run mcp-bcb
```

This starts the server with a single tool, `status`, which returns the
standard envelope without calling any external API — `data.module`,
`data.version`, `data.status` and `data.tools_implemented` (empty for now),
plus `metadata` pointing at Banco Central do Brasil as the (future) source.

## Planned data sources

- **SGS — Sistema Gerenciador de Séries Temporais** — `https://api.bcb.gov.br/dados/serie/bcdata.sgs.<codigo>/dados` — séries históricas (Selic, IPCA, câmbio, etc.), sem chave de API.
- **PTAX** — `https://olinda.bcb.gov.br/olinda/servico/PTAX/...` — cotações diárias de câmbio.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `obter_serie_temporal` | Retorna uma série temporal do SGS por código, com filtro de período. |
| 2 | `consultar_taxa_selic` | Retorna a taxa Selic (meta ou efetiva) em um período. |
| 3 | `consultar_cotacao_cambio` | Retorna a cotação de uma moeda (ex.: USD) em uma data. |
| 4 | `listar_series_disponiveis` | Lista séries do SGS conhecidas/catalogadas por este módulo. |

None of these are implemented yet — see
[docs/modules/bcb.md](../../docs/modules/bcb.md) for the detailed
design.

## Package layout

```
packages/mcp_bcb/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_bcb/
│   ├── server.py          # FastMCP instance, `status` tool registered
│   ├── config.py          # pydantic-settings (MCP_BCB_*)
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

See **[docs/modules/bcb.md](../../docs/modules/bcb.md)** for the
full plan, and [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-bcb` fits
into the overall `mcp-data-br` roadmap.
