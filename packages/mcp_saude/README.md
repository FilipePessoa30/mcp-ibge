# mcp-saude

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for Brazilian public health data (DataSUS / Ministério da Saúde) — facilities and indicators by município/UF — planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package runs (`uv run mcp-saude`) and
> exposes the shared `status` tool — no data tool is implemented yet. See
> **[docs/modules/saude.md](../../docs/modules/saude.md)** for the
> full plan: data sources, planned tools and known challenges.

## What will mcp-saude be?

**mcp-saude** will expose official, public data from **Ministério da Saúde - DataSUS**
(<https://datasus.saude.gov.br/>) as typed, traceable [MCP](https://modelcontextprotocol.io/)
tools, following the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_SAUDE_*` env vars).

## Try the scaffold

```bash
uv run mcp-saude
```

This starts the server with a single tool, `status`, which returns the
standard envelope without calling any external API — `data.module`,
`data.version`, `data.status` and `data.tools_implemented` (empty for now),
plus `metadata` pointing at Ministério da Saúde - DataSUS as the (future) source.

## Planned data sources

- **CNES — Cadastro Nacional de Estabelecimentos de Saúde** — `https://cnes.datasus.gov.br/` — estabelecimentos de saúde por município/UF.
- **DataSUS / TabNet / OpenDataSUS** — indicadores agregados de saúde; sem API REST simples e estável, exige avaliação de formato (TabNet exporta CSV/TabWin) — ver Desafios abaixo.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_estabelecimentos_saude` | Lista estabelecimentos de saúde (CNES) por município/UF. |
| 2 | `obter_indicadores_saude_municipio` | Retorna indicadores de saúde agregados para um município. |
| 3 | `listar_indicadores_disponiveis` | Lista indicadores de saúde catalogados por este módulo. |

None of these are implemented yet — see
[docs/modules/saude.md](../../docs/modules/saude.md) for the detailed
design.

## Desafios

Ao contrário do `mcp-ibge` (`servicodados.ibge.gov.br`), a maior parte dos indicadores do DataSUS é publicada via TabNet (interface web/TabWin), sem uma API REST simples e estável. A implementação real provavelmente dependerá de datasets derivados/pré-processados (ver `services/`), seguindo a estratégia já prevista para `mcp-inep` em [docs/modules/inep.md](inep.md).


## Package layout

```
packages/mcp_saude/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_saude/
│   ├── server.py          # FastMCP instance, `status` tool registered
│   ├── config.py          # pydantic-settings (MCP_SAUDE_*)
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

See **[docs/modules/saude.md](../../docs/modules/saude.md)** for the
full plan, and [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-saude` fits
into the overall `mcp-data-br` roadmap.
