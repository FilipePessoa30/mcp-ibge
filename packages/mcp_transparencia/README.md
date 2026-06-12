# mcp-transparencia

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for the Brazilian Federal Transparency Portal (Portal da Transparência / CGU) — public spending, contracts and sanctions — planning stage.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-planning-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

> **Status: planning / scaffold.** This package runs (`uv run mcp-transparencia`) and
> exposes the shared `status` tool — no data tool is implemented yet. See
> **[docs/modules/transparencia.md](../../docs/modules/transparencia.md)** for the
> full plan: data sources, planned tools and known challenges.

## What will mcp-transparencia be?

**mcp-transparencia** will expose official, public data from **Portal da Transparência (CGU)**
(<https://www.portaltransparencia.gov.br/>) as typed, traceable [MCP](https://modelcontextprotocol.io/)
tools, following the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings` (`MCP_TRANSPARENCIA_*` env vars).

## Try the scaffold

```bash
uv run mcp-transparencia
```

This starts the server with a single tool, `status`, which returns the
standard envelope without calling any external API — `data.module`,
`data.version`, `data.status` and `data.tools_implemented` (empty for now),
plus `metadata` pointing at Portal da Transparência (CGU) as the (future) source.

## Planned data sources

- **API do Portal da Transparência** — `https://api.portaldatransparencia.gov.br/` — despesas, contratos, convênios, sanções (CEIS, CNEP, etc.).

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `consultar_despesas_orgao` | Consulta despesas de um órgão público por ano/mês. |
| 2 | `consultar_sancoes` | Consulta sanções administrativas (CEIS/CNEP) por CPF/CNPJ. |
| 3 | `consultar_contratos_orgao` | Lista contratos de um órgão público por ano. |
| 4 | `listar_orgaos` | Lista órgãos cadastrados no Portal da Transparência. |

None of these are implemented yet — see
[docs/modules/transparencia.md](../../docs/modules/transparencia.md) for the detailed
design.

## Atenção — chave de API

Diferente da maioria dos módulos do `mcp-data-br`, a API do Portal da Transparência exige uma chave de acesso pessoal (gratuita, cadastrada por e-mail). Quando este módulo for implementado, a chave deve ser configurada via variável de ambiente (`MCP_TRANSPARENCIA_API_KEY` ou similar) e nunca commitada — ver [docs/security.md](../security.md).


## Package layout

```
packages/mcp_transparencia/
├── pyproject.toml
├── README.md            # this file
├── src/mcp_transparencia/
│   ├── server.py          # FastMCP instance, `status` tool registered
│   ├── config.py          # pydantic-settings (MCP_TRANSPARENCIA_*)
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

See **[docs/modules/transparencia.md](../../docs/modules/transparencia.md)** for the
full plan, and [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-transparencia` fits
into the overall `mcp-data-br` roadmap.
