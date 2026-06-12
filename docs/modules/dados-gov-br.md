# Module: mcp-dados-gov-br

**mcp-dados-gov-br** exposes the **Portal Brasileiro de Dados Abertos**
(dados.gov.br) — a catalog of datasets, organizations, groups and tags
published by Brazilian public bodies (federal, state and municipal) — as
typed, traceable [MCP](https://modelcontextprotocol.io/) tools, following the
conventions established by
[`mcp-ibge`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_ibge)
(see [Architecture](../architecture.md) and
[Data Sources](../data_sources.md)).

## Quick demo

Once configured in an MCP client, ask in natural language:

- *"What datasets exist about deforestation in the Amazon?"*
- *"Search for datasets about COVID-19 vaccination."*
- *"Show me the resources (files/links) for this dataset."*
- *"Which government agencies publish education data?"*
- *"What groups/themes exist in the open data catalog?"*

The agent picks the right tool (`buscar_datasets`,
`sugerir_datasets_para_pergunta`, `obter_dataset`,
`listar_recursos_dataset`, `buscar_organizacoes`, ...), calls the public CKAN
API at dados.gov.br, and returns a typed JSON response with full source
metadata so the answer can be verified.

## Data source

All data comes from the **CKAN Action API** of dados.gov.br:

- Base URL: `https://dados.gov.br/api/3/action`
- API docs: <https://docs.ckan.org/en/latest/api/>

Every CKAN action is a `GET <base_url>/<action>?<params>` request that always
returns HTTP 200 with a body `{"success": bool, "result": ..., "error":
{...}}` — `mcp-dados-gov-br` translates both HTTP-level errors and
`"success": false` bodies into the same typed exception hierarchy
(`CkanNotFoundError`, `CkanValidationError`, `CkanRateLimitError`,
`CkanServerError`, `CkanAuthRequiredError`).

Most read-only catalog queries (dataset/organization/group/tag search and
detail) work **without a token**. A consumer token
(`DADOS_GOV_BR_API_TOKEN`) is only required for some
organizations/datasets that restrict access — see
[Authentication](#authentication) below.

## Tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_datasets` | Searches public datasets by free-text query (`package_search`). |
| 2 | `obter_dataset` | Gets full details of a dataset, including its resources (`package_show`). |
| 3 | `listar_recursos_dataset` | Lists a dataset's resources (CSV, JSON, API, PDF, XLSX, ...). |
| 4 | `buscar_organizacoes` | Searches (with `query`) or lists (without `query`) publishing organizations. |
| 5 | `obter_organizacao` | Gets details of a publishing organization (`organization_show`). |
| 6 | `listar_grupos` | Lists thematic groups available in the catalog (`group_list`). |
| 7 | `buscar_tags` | Searches tags by name (`tag_search`). |
| 8 | `sugerir_datasets_para_pergunta` | Suggests datasets for a natural-language question, using keyword extraction (no LLM). |

Plus the shared `status` tool (see
[Architecture: adding a new module](../architecture.md#adding-a-new-module)).

Every tool shares:

- **Typed JSON responses**, backed by Pydantic models
  (`DatasetSummary`/`Dataset`, `Resource`, `Organization`, `Group`, `Tag`).
- **Standard response envelope**:
  `{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`,
  on success and on failure — see
  [Data Sources & Response Format](../data_sources.md). `metadata` includes
  `source_name`, `source_url`, `endpoint`, `params`, `retrieved_at` and
  `cache_hit`.
- **In-memory TTL cache** — avoids repeated calls to the CKAN API for
  identical queries within a session (configurable, can be disabled).
- **No invented data** — every dataset, organization, group or tag returned
  comes directly from a CKAN API response. If nothing matches, tools return
  an empty list (with a `warnings` entry when relevant), never a guess.

### `sugerir_datasets_para_pergunta`

This tool accepts a natural-language question (e.g. *"Quais dados existem
sobre desmatamento na Amazônia?"*) and suggests datasets that might be useful
— **without using any internal LLM**. It works in two steps:

1. **Keyword extraction**: tokenizes the question, lowercases it, and removes
   a curated list of Portuguese stopwords (articles, pronouns, connectives)
   plus a few domain terms that are too generic to refine a search (e.g.
   "dados", "informações", "buscar").
2. **Search**: joins the remaining keywords into a query string and calls
   `package_search` with it.

The extracted keywords are returned in `metadata.params["keywords"]` for
traceability. If no keywords remain after filtering (e.g. the question is
made entirely of stopwords), the tool returns `ok: true` with an empty list
and a `warnings` entry explaining that no suggestion could be made.

## Configuration

Configured via `pydantic-settings`. Most variables follow the shared
`mcp-data-br` convention (`MCP_DATA_BR_*` / `MCP_DADOS_GOV_BR_*`), but the
portal-specific ones (`DADOS_GOV_BR_API_BASE_URL`,
`DADOS_GOV_BR_API_TOKEN`) follow the naming requested for this module and have
no `MCP_` prefix.

| Variable | Default | Description |
| --- | --- | --- |
| `DADOS_GOV_BR_API_BASE_URL` | `https://dados.gov.br/api/3/action` | Base URL of the CKAN Action API. Must be an `https://dados.gov.br/...` URL — any other host/scheme is rejected at startup. |
| `DADOS_GOV_BR_API_TOKEN` | unset | Consumer token (API key), sent as the raw `Authorization` header when set. Most queries work without it. |
| `MCP_DATA_BR_REQUEST_TIMEOUT` | `30.0` | HTTP request timeout, in seconds. |
| `MCP_DATA_BR_ENABLE_CACHE` | `true` | Enables/disables the in-memory TTL cache. |
| `MCP_DATA_BR_CACHE_TTL_SECONDS` | `3600.0` | Cache entry lifetime, in seconds. |

## Authentication

If a CKAN action requires authentication (HTTP 401/403, or a body with
`error.__type == "Authorization Error"`) and `DADOS_GOV_BR_API_TOKEN` is
**not** configured, the tool returns `ok: false` with an error message
explaining that `DADOS_GOV_BR_API_TOKEN` must be set with a valid consumer
token from dados.gov.br. If a token **is** configured but the request still
fails with an authorization error, the message instead suggests the
configured token may be invalid or lack permission for that resource.

## Limitations

- **Does not replace official validation.** Always check `metadata` (source,
  endpoint, retrieval time, parameters) and any `warnings` against the
  dados.gov.br portal before using the data in reports or decisions.
- **Keyword extraction is intentionally simple.** `sugerir_datasets_para_pergunta`
  uses tokenization and a Portuguese stopword list — not a language model —
  so results depend on the words used in the question matching dataset
  titles/descriptions/tags in the catalog.
- **Catalog coverage varies by publisher.** Not all government bodies publish
  the same level of detail (descriptions, tags, groups, resources) for their
  datasets.

## See also

- [packages/mcp_dados_gov_br/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_dados_gov_br/README.md)
- [docs/roadmap.md](../roadmap.md)
- [docs/data_sources.md](../data_sources.md)
