# Roadmap

`mcp-data-br` aims to grow into a collection of focused MCP servers for
Brazilian public data sources, each independently installable and following
the same conventions (see [architecture.md](architecture.md),
[data_sources.md](data_sources.md), [security.md](security.md)).

This page tracks **modules** (new packages). For the detailed,
version-by-version roadmap of an individual module's tools, see that
module's own README (e.g.
[packages/mcp_ibge/README.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_ibge/README.md#roadmap)).

## Available

- **`mcp-ibge`** — IBGE data: Localidades (regions, states, municipalities,
  districts) and Agregados/SIDRA (statistical aggregates, population
  estimates). Stable. See [Module: mcp-ibge](modules/ibge.md) and
  [packages/mcp_ibge/](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_ibge).

## Scaffolded (planning)

These packages exist in the workspace, are installable and runnable
(`uv run <command>`), and expose the shared `status` tool — but no data
tool is implemented yet. Each links to a `docs/modules/<slug>.md` page with
the planned tools, data sources, challenges and version-by-version
implementation plan.

- **`mcp-inep`** — education data from INEP: Censo Escolar, Ideb, Saeb,
  Enem, schools by município and education indicators, combined with
  `mcp-ibge` municipality codes for municipal education profiles. See
  [Module: mcp-inep (planned)](modules/inep.md) and
  [`packages/mcp_inep/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_inep).
- **`mcp-dados-gov-br`** — generic access to datasets, organizations and
  resources published on [dados.gov.br](https://dados.gov.br/) (CKAN API).
  See [Module: mcp-dados-gov-br (planned)](modules/dados-gov-br.md) and
  [`packages/mcp_dados_gov_br/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_dados_gov_br).
- **`mcp-bcb`** — economic/financial indicators from the Banco Central do
  Brasil: SGS time series, PTAX exchange rates, Selic. See
  [Module: mcp-bcb (planned)](modules/bcb.md) and
  [`packages/mcp_bcb/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_bcb).
- **`mcp-rio`** — open data from the City of Rio de Janeiro (Data.Rio
  catalog), with planned integration with `mcp-ibge` (município
  `3304557`). See [Module: mcp-rio (planned)](modules/rio.md) and
  [`packages/mcp_rio/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_rio).
- **`mcp-saude`** — health facilities (CNES) and health indicators by
  município/UF from the Ministério da Saúde / DataSUS. See
  [Module: mcp-saude (planned)](modules/saude.md) and
  [`packages/mcp_saude/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_saude).
- **`mcp-transparencia`** — public spending, contracts, convênios and
  sanctions from the Portal da Transparência (CGU). Requires an API key
  (see [Module: mcp-transparencia (planned)](modules/transparencia.md)) —
  the only module expected to need one. See
  [`packages/mcp_transparencia/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_transparencia).
- **`mcp-tesouro`** — fiscal data (RREO, RGF, debt) for União, states and
  municípios from the Tesouro Nacional / SICONFI. See
  [Module: mcp-tesouro (planned)](modules/tesouro.md) and
  [`packages/mcp_tesouro/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_tesouro).

## Planned (no package yet)

- **`mcp-sidra`** — Today, Agregados/SIDRA tools live inside `mcp-ibge`.
  As SIDRA-specific functionality grows (more aggregates, classifications,
  geographic meshes), it may be split into its own `mcp-sidra` package so
  `mcp-ibge` can stay focused on Localidades while SIDRA gets dedicated,
  more specialized tooling. No breaking changes are planned for existing
  `mcp-ibge` tools as part of this — if/when a split happens, it will be
  additive (new package, with `mcp-ibge` either re-exporting or deprecating
  gradually). See [Module: mcp-sidra (planned)](modules/sidra.md).

These are directional, not commitments with dates. The workspace structure
(see [architecture.md](architecture.md#adding-a-new-module)) is designed so
each scaffolded module's data tools can be implemented independently, and
new modules can be added as `packages/mcp_<name>/` without touching existing
ones.

## Cross-cutting

- **`evals/`** — build out a shared evaluation framework (datasets +
  reports) so tool quality and regressions can be tracked across modules as
  they're added. See [Evals](evals.md).
- **`examples/`** — keep client configs (Claude Desktop, Cursor, Open WebUI)
  and prompt recipes up to date as new modules land.
