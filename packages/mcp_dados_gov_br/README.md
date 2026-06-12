# mcp-dados-gov-br

Part of **[mcp-data-br](../../README.md)** — a collection of MCP servers for
Brazilian public data.

**Model Context Protocol server for the Brazilian Open Data Portal
(dados.gov.br) — dataset, organization, group and tag catalog search via the
CKAN API.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
![Status](https://img.shields.io/badge/status-beta-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

See **[docs/modules/dados-gov-br.md](../../docs/modules/dados-gov-br.md)** for
the full module documentation (tools, configuration, authentication,
limitations).

## What does mcp-dados-gov-br do?

**mcp-dados-gov-br** exposes official, public data from
**dados.gov.br - Portal Brasileiro de Dados Abertos** (<https://dados.gov.br/>)
as typed, traceable [MCP](https://modelcontextprotocol.io/) tools, following
the same conventions as
[`mcp-ibge`](../mcp_ibge/README.md): the shared
`{"ok", "data", "metadata", "warnings", "errors"}` response envelope (see
[docs/data_sources.md](../../docs/data_sources.md)), an allowlist of
official domains, input validation before any network call, `stdio`-safe
logging, and configuration via `pydantic-settings`.

## Running the server

```bash
uv run mcp-dados-gov-br
```

By default this starts a `stdio` MCP server with 9 tools: the shared
`status` tool plus 8 data tools for searching and detailing datasets,
organizations, groups and tags.

## Data source

- **dados.gov.br (CKAN Action API)** — `https://dados.gov.br/api/3/action` —
  catalog of datasets, organizations, groups, tags and resources (CSV, JSON,
  APIs, PDF, XLSX, ...) published by federal, state and municipal government
  bodies. API docs: <https://docs.ckan.org/en/latest/api/>.

## Tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_datasets` | Searches public datasets by free-text query. |
| 2 | `obter_dataset` | Gets full details of a dataset, including its resources. |
| 3 | `listar_recursos_dataset` | Lists a dataset's resources (CSV, JSON, API, PDF, XLSX, ...). |
| 4 | `buscar_organizacoes` | Searches or lists publishing organizations. |
| 5 | `obter_organizacao` | Gets details of a publishing organization. |
| 6 | `listar_grupos` | Lists thematic groups available in the catalog. |
| 7 | `buscar_tags` | Searches tags by name. |
| 8 | `sugerir_datasets_para_pergunta` | Suggests datasets for a natural-language question (keyword extraction, no LLM). |

See [docs/modules/dados-gov-br.md](../../docs/modules/dados-gov-br.md) for
details on each tool, including `sugerir_datasets_para_pergunta`'s
keyword-extraction approach.

## Configuration

| Variable | Default | Description |
| --- | --- | --- |
| `DADOS_GOV_BR_API_BASE_URL` | `https://dados.gov.br/api/3/action` | Base URL of the CKAN Action API (must be `https://dados.gov.br/...`). |
| `DADOS_GOV_BR_API_TOKEN` | unset | Consumer token, sent as the `Authorization` header when set. Most queries work without it. |
| `MCP_DATA_BR_REQUEST_TIMEOUT` | `30.0` | HTTP request timeout, in seconds. |
| `MCP_DATA_BR_ENABLE_CACHE` | `true` | Enables/disables the in-memory TTL cache. |
| `MCP_DATA_BR_CACHE_TTL_SECONDS` | `3600.0` | Cache entry lifetime, in seconds. |

See [docs/modules/dados-gov-br.md#authentication](../../docs/modules/dados-gov-br.md#authentication)
for how missing/invalid tokens are reported.

## Package layout

```
packages/mcp_dados_gov_br/
├── pyproject.toml
├── README.md                  # this file
├── src/mcp_dados_gov_br/
│   ├── server.py              # FastMCP instance, all tools registered
│   ├── config.py              # pydantic-settings
│   ├── security.py            # host allowlist, response size guard, safe errors
│   ├── schemas/
│   │   ├── common.py          # shared {ok, data, metadata, warnings, errors} envelope
│   │   └── catalog.py          # Dataset, Resource, Organization, Group, Tag models
│   ├── clients/
│   │   ├── base.py            # AsyncCkanClient: HTTP, cache, error translation
│   │   └── catalog.py          # thin CKAN action wrappers (package_search, ...)
│   ├── services/
│   │   └── catalog_service.py # business logic: validation, conversions, suggestions
│   ├── tools/
│   │   ├── status_tools.py    # `status` tool
│   │   ├── dataset_tools.py   # buscar_datasets, obter_dataset, ...
│   │   ├── organizacao_tools.py # buscar_organizacoes, obter_organizacao
│   │   └── catalogo_tools.py  # listar_grupos, buscar_tags
│   └── utils/
│       ├── cache.py           # in-memory TTL cache
│       ├── errors.py          # Ckan*Error exception hierarchy
│       ├── validators.py      # validate_limit, validate_non_empty
│       └── keywords.py        # Portuguese keyword extraction (no LLM)
└── tests/
    ├── test_server.py
    ├── test_status_tools.py
    ├── test_catalog_client.py
    ├── test_catalog_service.py
    ├── test_dataset_tools.py
    ├── test_organizacao_tools.py
    └── test_catalogo_tools.py
```

This mirrors [`mcp_ibge`](../mcp_ibge/)'s internal layering — see
[docs/architecture.md](../../docs/architecture.md#anatomy-of-a-module-package).

## Examples

See
[examples/agent_recipes/find-public-datasets/](../../examples/agent_recipes/find-public-datasets/)
for a worked prompt recipe using this module's tools.

## Roadmap

See [docs/roadmap.md](../../docs/roadmap.md) for how `mcp-dados-gov-br` fits
into the overall `mcp-data-br` roadmap.
