# mcp-data-br

**A collection of [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) servers for Brazilian public data — typed, traceable, and safe to call
from AI agents.**

> 🇧🇷 **Nota**: esta documentação é majoritariamente em inglês, com notas em
> português onde for útil. Os módulos cobrem dados públicos brasileiros
> (IBGE, SIDRA), então os nomes das *tools* e parâmetros permanecem em
> português (ex.: `listar_municipios`, `consultar_agregado`), seguindo a
> convenção do projeto.

## What is mcp-data-br?

Brazilian public institutions (IBGE, INEP, Banco Central, dados.gov.br,
state and city open data portals, ...) publish a huge amount of free,
no-API-key data — but spread across many APIs, with inconsistent shapes,
encodings and documentation that are hard for an LLM to use safely.

**mcp-data-br** turns those public APIs into **typed, traceable tools** that
an agent (Claude Desktop, Cursor, Open WebUI, or any MCP-compatible client)
can call directly. Every tool, across every module, follows the same
conventions:

- **Typed, validated responses** — every tool is backed by Pydantic models.
- **Traceable by design** — every response is
  `{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`,
  with `metadata` (`source_name`, `source_url`, `official_source`, `endpoint`,
  `params`, `retrieved_at`, `period`, `territorial_level`, `license_note`,
  `version`, `cache_hit`) so any number can be checked against its official
  source.
- **Safe by default** — no shell execution, no arbitrary file/URL access,
  outbound requests restricted to an allowlist of official domains, input
  validation before any network call. See [Security](security.md).
- **Local-first** — runs over `stdio`, no API keys, no external services
  beyond the public data source itself.

The project is organized as a single **uv workspace (monorepo)**: each data
source gets its own installable package under
[`packages/`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages),
all sharing the same conventions and tooling.

## 30-second demo

**Prompt** (typed into Claude Desktop / Cursor / any MCP client):

> "Compare Rio de Janeiro, Niterói and Maricá using official Brazilian public
> data."

The agent resolves each municipality to its IBGE code, then calls
`comparar_municipios` once to get a typed, source-cited comparison:

```python
comparar_municipios(
    municipios=[
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Niterói", "uf": "RJ"},
        {"nome": "Maricá", "uf": "RJ"},
    ],
    indicadores=["populacao_estimada"],
)
```

| Município | UF | Estimated population (2024) |
| --- | --- | --- |
| Rio de Janeiro | RJ | 6,211,423 |
| Niterói | RJ | 516,981 |
| Maricá | RJ | 187,051 |

Every row is traceable to a `servicodados.ibge.gov.br` endpoint via
`data.fontes` / `metadata`. See the
[Compare Municipalities example](examples/compare-municipalities.md) for the
full request/response, and [Getting Started](getting-started.md) to run it
yourself.

## Where to go next

- **[Getting Started](getting-started.md)** — clone, sync, and run your
  first query in a few minutes.
- **[Installation](installation.md)** — `uvx`, development mode, and
  configuration via environment variables.
- **Clients** — connect [Claude Desktop](clients/claude-desktop.md),
  [Cursor](clients/cursor.md) or [Open WebUI](clients/open-webui.md).
- **Modules** — what [`mcp-ibge`](modules/ibge.md) exposes today, and what's
  planned for [SIDRA](modules/sidra.md).
- **Tools reference** — [Localidades](tools/localidades.md),
  [Agregados/SIDRA](tools/agregados.md) and [Geospatial](tools/geospatial.md)
  tools, with parameters and JSON examples.
- **Examples** — ready-to-use agent recipes:
  [Municipal Profile](examples/municipal-profile.md),
  [Compare Municipalities](examples/compare-municipalities.md),
  [Education Activity](examples/education-activity.md).

## Current modules

| Module | Status | Data source | Docs |
| --- | --- | --- | --- |
| [`mcp-ibge`](https://github.com/FilipePessoa30/mcp-data-br/tree/main/packages/mcp_ibge) | Stable | IBGE (Localidades, Agregados/SIDRA, geospatial meshes) | [Module docs](modules/ibge.md) |

See [Roadmap](roadmap.md) for planned modules (`mcp-sidra`, `mcp-inep`,
`mcp-dados-gov-br`, `mcp-bcb`, `mcp-rio`).

## Other resources

- [Evals](evals.md) — evaluation methodology for measuring tool quality over
  time.
- [Contributing](contributing.md) — how to set up the workspace and
  contribute.
- [Architecture](architecture.md) — how the workspace and packages are
  organized.
- [Data Sources & Response Format](data_sources.md) — the shared response
  envelope used by every module.
