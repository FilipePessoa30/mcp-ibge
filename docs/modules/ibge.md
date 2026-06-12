# Module: mcp-ibge

**mcp-ibge** exposes official, public data from the **IBGE** (Instituto
Brasileiro de Geografia e Estatística — Brazilian Institute of Geography and
Statistics) as typed, traceable MCP tools: locations (regions, states,
municipalities, districts), **SIDRA** statistical aggregates, **population**
indicators and **geospatial** meshes.

> **v0.2.0 status**: the **Localidades** tools (regions, states,
> municipalities, districts and code resolution) and the **Agregados/SIDRA**
> tools (generic discovery and query of any SIDRA aggregate) are the stable,
> fully tested core of this release. The **population indicator**
> (`consultar_populacao_municipio`) and **geospatial** tools are
> **experimental previews** — see [Roadmap](../roadmap.md).

## Quick demo

Once configured in an MCP client, ask in natural language:

- *"What is the IBGE code for Niterói, RJ?"*
- *"List all municipalities in Rio de Janeiro state."*
- *"Search municipalities named São José."*
- *"Get metadata for an IBGE aggregate."*
- *"Query an IBGE aggregate with variables, periods and locations."*

The agent picks the right tool (`obter_codigo_municipio`,
`listar_municipios`, `buscar_municipio`, `obter_metadados_agregado`,
`consultar_agregado`, ...), calls the public IBGE API, and returns a typed
JSON response with full source metadata so the answer can be verified.

## Feature areas

| Area | Status | Docs |
| --- | --- | --- |
| **Localidades** — regions, states, municipalities, districts, fuzzy search and code resolution | Stable | [Tools → Localidades](../tools/localidades.md) |
| **Agregados/SIDRA** — generic discovery and query of any SIDRA aggregate | Stable | [Tools → Agregados/SIDRA](../tools/agregados.md) |
| **SIDRA Query Builder** — 7 tools to discover, explain, suggest and validate SIDRA queries (no LLM on the server) | New | [Tools → Agregados/SIDRA](../tools/agregados.md#sidra-query-builder) |
| **Population indicator** — `consultar_populacao_municipio`, built on Agregados/SIDRA | Experimental | [Tools → Agregados/SIDRA](../tools/agregados.md#14-consultar_populacao_municipio) |
| **Perfil Municipal / Comparação** — `gerar_perfil_municipal`, `comparar_municipios` | Experimental | [Examples](../examples/municipal-profile.md) |
| **Geospatial** — municipality/state boundary meshes and bounding boxes (GeoJSON) | New / experimental | [Tools → Geospatial](../tools/geospatial.md) |

Every tool shares:

- **Typed JSON responses**, backed by Pydantic models.
- **Standard response envelope**:
  `{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`,
  on success and on failure — see
  [Data Sources & Response Format](../data_sources.md).
- **Source metadata** on every response — `source_name`, `source_url`,
  `official_source`, `endpoint`, `params`, `retrieved_at`, `period`,
  `territorial_level`, `license_note`, `version`, `cache_hit`.
- **In-memory TTL cache** — avoids repeated calls to the IBGE API within a
  session (configurable, can be disabled — see [Installation](../installation.md)).

## Data sources

All data is fetched live, with no API key, from the **IBGE Serviços de
Dados** API:

- [IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades)
  — regions, states, municipalities and districts.
- [IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados)
  — statistical aggregates, including censuses and population estimates.
- [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas) —
  municipality/state boundary geometries (GeoJSON), used by the geospatial
  tools.

## Resources & prompts

- **`mcp-data-br://status`** (alias: `ibge://status`) — server status:
  version, registered tools, cache config/size, request metrics
  (`total_requests`, `cache_hits`, `cache_misses`, `errors`,
  `cache_hit_rate`, `average_latency_ms`), uptime and data sources.
- **`comparar_municipios`** prompt — guides comparing an indicator across
  municipalities using the `comparar_municipios` tool, always citing source,
  period, territorial unit and limitations.

## Limitations

- **Does not replace official validation.** Always check `metadata` (source,
  endpoint, retrieval time, parameters) and any `warnings` against the
  official IBGE sources before using the data in reports or decisions.
- **Some aggregates require SIDRA knowledge.** `consultar_agregado` mirrors
  the SIDRA query syntax (variables, periods, locations, classifications);
  use the discovery tools in [Tools → Agregados/SIDRA](../tools/agregados.md)
  to find valid IDs first.
- **Changes to the IBGE API may require adjustments.** This server depends on
  `servicodados.ibge.gov.br`; outages, schema changes, or aggregates
  discontinued/renamed after a new Census can affect responses.

## Roadmap

See [packages/mcp_ibge/README.md#roadmap](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/README.md#roadmap)
for the module's version-by-version roadmap, and [Roadmap](../roadmap.md)
for the broader, multi-module roadmap.
