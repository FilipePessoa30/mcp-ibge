# mcp-data-br

**A collection of [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) servers for Brazilian public data — typed, traceable, and safe to call
from AI agents.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
[![CI](https://github.com/FilipePessoa30/mcp-ibge/actions/workflows/ci.yml/badge.svg)](https://github.com/FilipePessoa30/mcp-ibge/actions/workflows/ci.yml)
![License](https://img.shields.io/badge/license-MIT-green)
![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)
![pytest](https://img.shields.io/badge/tested%20with-pytest-0A9EDC?logo=pytest&logoColor=white)

## What is mcp-data-br?

Brazilian public institutions (IBGE, INEP, Banco Central, dados.gov.br,
state and city open data portals, ...) publish a huge amount of free,
no-API-key data — but spread across many APIs, with inconsistent shapes,
encodings and documentation that are hard for an LLM to use safely.

**mcp-data-br** is a growing collection of small, focused MCP servers — one
per data source — that turn those public APIs into **typed, traceable
tools** an agent (Claude Desktop, Cursor, or any MCP-compatible client) can
call directly. Every tool across every module follows the same conventions:

- **Typed, validated responses** — every tool is backed by Pydantic models.
- **Traceable by design** — every response is `{"ok": ..., "data": ...,
  "metadata": {...}, "warnings": [...], "errors": [...]}`, with `metadata`
  (`source_name`, `source_url`, `official_source`, `endpoint`, `params`,
  `retrieved_at`, `period`, `territorial_level`, `license_note`, `version`,
  `cache_hit`) so any number can be checked against its official source.
- **Safe by default** — no shell execution, no arbitrary file/URL access,
  outbound requests restricted to an allowlist of official domains, input
  validation before any network call. See [docs/security.md](docs/security.md).
- **Local-first** — runs over `stdio`, no API keys, no external services
  beyond the public data source itself.

The project is organized as a single **uv workspace (monorepo)**: each data
source gets its own installable package under [`packages/`](packages/), all
sharing the same conventions and tooling.

## Available modules

| Module | Status | Data | Docs |
| --- | --- | --- | --- |
| [`mcp-ibge`](packages/mcp_ibge/) | **Stable** | IBGE — geographic locations (regions, states, municipalities, districts) and Agregados/SIDRA statistical aggregates | [README](packages/mcp_ibge/README.md) · [docs](packages/mcp_ibge/docs/) |

## Planned modules

mcp-data-br is designed to grow. Planned/possible future modules include
`mcp-sidra` (a dedicated SIDRA module, split out of `mcp-ibge`), `mcp-inep`
(education data), `mcp-dados-gov-br` (generic dados.gov.br access),
`mcp-bcb` (Banco Central indicators) and `mcp-rio` (Rio de Janeiro open
data). See [docs/roadmap.md](docs/roadmap.md) for details — none of these
are implemented yet, but the workspace is structured so they can be added as
new packages without touching existing ones.

## Quick start

Requires **Python 3.11+** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
uv run mcp-ibge
```

This starts the `mcp-ibge` server over `stdio`. For ready-to-use MCP client
configs (Claude Desktop, Cursor, Open WebUI) and example prompts, see
[examples/](examples/) and
[packages/mcp_ibge/docs/client_setup.md](packages/mcp_ibge/docs/client_setup.md).

For the full feature list, available tools, configuration options and
roadmap of the IBGE module, see
**[packages/mcp_ibge/README.md](packages/mcp_ibge/README.md)**.

## Project layout

```
mcp-data-br/
├── pyproject.toml          # uv workspace root (virtual project)
├── packages/
│   └── mcp_ibge/             # mcp-ibge: IBGE Localidades + Agregados/SIDRA
│       ├── src/mcp_ibge/
│       ├── tests/
│       ├── docs/
│       └── README.md
├── docs/                    # Monorepo-level docs (architecture, roadmap, security, data sources)
├── examples/                # MCP client configs (Claude Desktop, Cursor, Open WebUI) and prompts
└── evals/                   # Evaluation datasets and reports (placeholder)
```

See [docs/architecture.md](docs/architecture.md) for how the workspace and
modules are organized, and [docs/architecture.md#adding-a-new-module](docs/architecture.md#adding-a-new-module)
for what a new module needs.

## Documentation

- [docs/index.md](docs/index.md) — documentation index
- [docs/architecture.md](docs/architecture.md) — workspace structure and
  module conventions
- [docs/data_sources.md](docs/data_sources.md) — shared response envelope
  and data source registry
- [docs/security.md](docs/security.md) — security baseline
- [docs/roadmap.md](docs/roadmap.md) — current and planned modules

## Contributing

Contributions are welcome — bug reports, new tools, new modules,
documentation and tests. See [CONTRIBUTING.md](CONTRIBUTING.md) for the
development setup (uv workspace, lint/format/test commands) and guidelines.

## 🇧🇷 Sobre o projeto (resumo em português)

**mcp-data-br** é uma coleção de servidores [MCP](https://modelcontextprotocol.io/)
para dados públicos brasileiros, organizados como um único workspace
(monorepo) onde cada fonte de dados ganha seu próprio pacote em
[`packages/`](packages/). A primeira entrega é o **mcp-ibge**, com dados de
localidades e agregados do SIDRA do IBGE — veja
[packages/mcp_ibge/README.md](packages/mcp_ibge/README.md). O projeto foi
desenhado para crescer com novos módulos (ex.: SIDRA dedicado, INEP, Banco
Central, dados.gov.br, Rio de Janeiro) seguindo as mesmas convenções de
respostas tipadas, rastreáveis e seguras — veja
[docs/roadmap.md](docs/roadmap.md).

## License

[MIT](LICENSE)
