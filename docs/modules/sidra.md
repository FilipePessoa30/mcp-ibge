# Module: mcp-sidra (planned)

`mcp-sidra` is a **planned** future module — not implemented yet. This page
documents (1) what's available **today** via SIDRA tools inside `mcp-ibge`,
and (2) what a dedicated `mcp-sidra` module might look like.

## Today: SIDRA tools in `mcp-ibge`

[SIDRA](https://sidra.ibge.gov.br/) (Sistema IBGE de Recuperação Automática)
is IBGE's database of statistical aggregates — censuses, surveys, price
indices, population estimates, and more. `mcp-ibge` already exposes **generic
discovery and query tools for any SIDRA aggregate**:

- [`listar_agregados`](../tools/agregados.md#8-listar_agregados),
  [`obter_metadados_agregado`](../tools/agregados.md#9-obter_metadados_agregado),
  [`listar_variaveis_agregado`](../tools/agregados.md#10-listar_variaveis_agregado),
  [`listar_periodos_agregado`](../tools/agregados.md#11-listar_periodos_agregado),
  [`listar_localidades_agregado`](../tools/agregados.md#12-listar_localidades_agregado)
  and [`consultar_agregado`](../tools/agregados.md#13-consultar_agregado) —
  **stable**, full discovery → query workflow for any of SIDRA's thousands of
  tables.
- The [**SIDRA Query Builder**](../tools/agregados.md#sidra-query-builder) —
  7 additional tools (`buscar_tabelas_sidra`, `explicar_tabela_sidra`,
  `sugerir_consulta_sidra`, `validar_consulta_sidra`,
  `executar_consulta_sidra_validada`, ...) that help an agent figure out
  `agregado_id`, `variaveis`, `localidades`, `periodos` and `classificacao`
  without guessing — keyword/metadata heuristics only, **no LLM on the
  server**.

See [Tools → Agregados/SIDRA](../tools/agregados.md) for the full reference,
including the [step-by-step discovery
workflow](../tools/agregados.md#how-to-discover-an-aggregate-variable-period-and-location).

> 🇧🇷 **Nota**: hoje, todas as *tools* de SIDRA vivem dentro de `mcp-ibge`
> (prefixo de pacote IBGE, mas API genérica para qualquer agregado SIDRA).

## Why a dedicated module might exist later

As SIDRA-specific functionality grows (more aggregates, classifications,
geographic meshes), it may be split into its own `mcp-sidra` package so
`mcp-ibge` can stay focused on Localidades while SIDRA gets dedicated, more
specialized tooling.

- **No breaking changes are planned** for existing `mcp-ibge` tools as part
  of this. If/when a split happens, it will be additive (new package, with
  `mcp-ibge` either re-exporting or deprecating gradually).
- The workspace structure (see
  [Architecture → Adding a new module](../architecture.md#adding-a-new-module))
  is designed so `mcp-sidra` could be added as a new
  `packages/mcp_sidra/` package without touching `mcp-ibge`.
- It would follow the same conventions as every other module: the shared
  response envelope ([Data Sources](../data_sources.md)), the
  [Security baseline](../security.md), `stdio`-safe logging, and
  `pydantic-settings`-based configuration.

This is directional, not a commitment with a date — see [Roadmap](../roadmap.md)
for the full list of planned modules.
