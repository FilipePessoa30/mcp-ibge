# Module: mcp-dados-gov-br (planned)

> **Status: planning / scaffold.** `packages/mcp_dados_gov_br/` exists and runs
> (`uv run mcp-dados-gov-br`), exposing only the shared `status` tool — no data tool is
> implemented yet. This page is the initial plan: data sources, planned
> tools and known challenges.

## Overview

`mcp-dados-gov-br` will expose the Brazilian Open Data Portal (dados.gov.br) — dataset catalog search and metadata as typed, traceable
[MCP](https://modelcontextprotocol.io/) tools, following the conventions
established by [`mcp-ibge`](../../packages/mcp_ibge/README.md) (see
[Architecture](../architecture.md) and [Data Sources](../data_sources.md)).

## Planned data sources

- **dados.gov.br (CKAN) API** — `https://dados.gov.br/api/3/action/...` — catálogo de datasets, organizações e recursos (CSV, JSON, APIs) publicados por órgãos federais, estaduais e municipais.

## Planned tools

| # | Tool | Description |
| --- | --- | --- |
| 1 | `buscar_datasets` | Busca datasets no catálogo por termo, organização ou tema. |
| 2 | `obter_dataset` | Detalhes de um dataset (descrição, organização, licença, recursos). |
| 3 | `listar_organizacoes` | Lista organizações publicadoras cadastradas. |
| 4 | `listar_recursos_dataset` | Lista os recursos (arquivos/links) de um dataset. |

None of these are implemented yet — the package currently exposes only the
shared `status` tool described in
[Architecture: adding a new module](../architecture.md#adding-a-new-module).

## Conventions

Like every module in `mcp-data-br`, `mcp-dados-gov-br` will follow:

- The shared `{"ok", "data", "metadata", "warnings", "errors"}` response
  envelope (see [data_sources.md](../data_sources.md)).
- An allowlist of official domains for outbound requests (see
  [security.md](../security.md)).
- Configuration via `pydantic-settings`, env prefix `MCP_DADOS_GOV_BR_`.
- Portuguese tool-naming convention (`listar_`, `obter_`, `buscar_`,
  `consultar_`).

## See also

- [packages/mcp_dados_gov_br/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_dados_gov_br/README.md)
- [docs/roadmap.md](../roadmap.md)
