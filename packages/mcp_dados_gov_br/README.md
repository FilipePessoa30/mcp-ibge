# mcp-dados-gov-br

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for the Brazilian Open Data Portal (dados.gov.br) — dataset catalog search and metadata — planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package runs (`uv run mcp-dados-gov-br`) and
> exposes the shared `status` tool — no data tool is implemented yet. See
> **[docs/modules/dados-gov-br.md](../../docs/modules/dados-gov-br.md)** for the
> full plan: data sources, planned tools and known challenges.

## What will mcp-dados-gov-br be?

**mcp-dados-gov-br** will expose official, public data from **dados.gov.br - Portal Brasileiro de Dados Abertos**
(<https://dados.gov.br/>) as typed, traceable [MCP](https://modelcontextprotocol.io/)
tools, following the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_DADOS_GOV_BR_*` env vars).

## Try the scaffold

```bash
uv run mcp-dados-gov-br
```

This starts the server with a single tool, `status`, which returns the
standard envelope without calling any external API — `data.module`,
`data.version`, `data.status` and `data.tools_implemented` (empty for now),
plus `metadata` pointing at dados.gov.br - Portal Brasileiro de Dados Abertos as the (future) source.

## Planned data sources

- **dados.gov.br (CKAN) API** — `https://dados.gov.br/api/3/action/...` — catálogo de datasets, organizações e recursos (CSV, JSON, APIs) publicados por órgãos federais, estaduais e municipais.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_datasets` | Busca datasets no catálogo por termo, organização ou tema. |
| 2 | `obter_dataset` | Detalhes de um dataset (descrição, organização, licença, recursos). |
| 3 | `listar_organizacoes` | Lista organizações publicadoras cadastradas. |
| 4 | `listar_recursos_dataset` | Lista os recursos (arquivos/links) de um dataset. |

None of these are implemented yet — see
[docs/modules/dados-gov-br.md](../../docs/modules/dados-gov-br.md) for the detailed
design.

## Package layout

```
packages/mcp_dados_gov_br/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_dados_gov_br/
│   ├── server.py          # FastMCP instance, `status` tool registered
│   ├── config.py          # pydantic-settings (MCP_DADOS_GOV_BR_*)
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

See **[docs/modules/dados-gov-br.md](../../docs/modules/dados-gov-br.md)** for the
full plan, and [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-dados-gov-br` fits
into the overall `mcp-data-br` roadmap.
