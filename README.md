# mcp-data-br

**A collection of [Model Context Protocol](https://modelcontextprotocol.io/)
(MCP) servers for Brazilian public data — typed, traceable, and safe to call
from AI agents.**

![Python](https://img.shields.io/badge/python-3.11%2B-3776AB?logo=python&logoColor=white)
![MCP](https://img.shields.io/badge/MCP-Model%20Context%20Protocol-6A5ACD)
[![CI](https://github.com/FilipePessoa30/mcp-data-br/actions/workflows/ci.yml/badge.svg)](https://github.com/FilipePessoa30/mcp-data-br/actions/workflows/ci.yml)
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

## 30-second demo

![Demo: comparing Rio de Janeiro, Niterói and Maricá with mcp-data-br](docs/assets/demo.gif)

> 🎥 Generated from a real `comparar_municipios` call — see
> [Regenerating the demo GIF](#regenerating-the-demo-gif) below.

**Prompt** (typed into Claude Desktop / Cursor / any MCP client):

> "Compare Rio de Janeiro, Niterói and Maricá using official Brazilian public
> data."

**What the agent does** — no API keys, no scraping, just typed tool calls
over `stdio`:

```python
# 1. Resolve each name to an IBGE municipality (fuzzy match, accent/case-insensitive)
buscar_municipio(nome="Rio de Janeiro")
buscar_municipio(nome="Niterói")
buscar_municipio(nome="Maricá")

# 2. Get the 7-digit IBGE codes
obter_codigo_municipio(nome="Rio de Janeiro", uf="RJ")  # -> 3304557
obter_codigo_municipio(nome="Niterói", uf="RJ")          # -> 3303302
obter_codigo_municipio(nome="Maricá", uf="RJ")           # -> 3302700

# 3. Check which indicators are available before asking for them
#    (today: estimated population, agregado SIDRA 6579)

# 4. One call does the rest: resolves + compares + cites sources
comparar_municipios(
    municipios=[
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Niterói", "uf": "RJ"},
        {"nome": "Maricá", "uf": "RJ"},
    ],
    indicadores=["populacao_estimada"],
)
```

**Final answer, straight from `comparar_municipios`**:

| Município | UF | Estimated population (2025) |
| --- | --- | --- |
| Rio de Janeiro | RJ | 6,730,729 |
| Niterói | RJ | 516,787 |
| Maricá | RJ | 212,470 |

> Live data as of when [`docs/assets/demo.gif`](docs/assets/demo.gif) was
> generated — run the tool yourself for the current SIDRA period.

- **Source**: IBGE — Agregados/SIDRA, table `6579` (Estimativas de
  População), period `2025` — every row in `data.fontes` is a direct,
  openable URL on `servicodados.ibge.gov.br`.
- **Warnings**: none for this query — but if a municipality name were
  ambiguous, not found, or an indicator weren't implemented yet, that would
  show up explicitly in `warnings` / `data.municipios_nao_resolvidos` /
  `data.indicadores_nao_implementados` instead of a guessed number. See the
  [`compare_municipalities` recipe](examples/agent_recipes/compare_municipalities/)
  for the full request/response and error cases.

In other words:

- **Local-first** — runs over `stdio` on your machine, no hosted backend.
- **No API keys** — every data source is a free, public government API.
- **Official data sources** — every value is traceable to a
  `servicodados.ibge.gov.br` endpoint via `metadata`/`data.fontes`.
- **Structured responses** — `{"ok", "data", "metadata", "warnings",
  "errors"}` every time, ready for an agent to parse and act on.
- **Safe by default** — no shell access, no arbitrary URLs, outbound
  requests restricted to an allowlist (see [docs/security.md](docs/security.md)).
- **Agent-ready** — typed tools an LLM can call directly, with ready-made
  recipes in [examples/agent_recipes/](examples/agent_recipes/).

### Try it yourself

```bash
git clone https://github.com/FilipePessoa30/mcp-data-br.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
uv run mcp-ibge
```

Minimal MCP client config (e.g. `claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uvx",
      "args": ["mcp-ibge"]
    }
  }
}
```

Then ask the prompt above. More configs (Cursor, Open WebUI, dev/local
checkout) are in [examples/](examples/); more ready-made prompts are in
[examples/agent_recipes/](examples/agent_recipes/).

### Regenerating the demo GIF

`docs/assets/demo.gif` is generated by [`scripts/generate_demo_gif.py`](scripts/generate_demo_gif.py),
which:

1. Connects to the local `mcp-ibge` over `stdio` and calls
   `comparar_municipios` for Rio de Janeiro, Niterói and Maricá
   ([`scripts/demo_compare_municipios.py`](scripts/demo_compare_municipios.py)) —
   so the numbers in the GIF are **live data from the IBGE API**, not
   hand-typed values.
2. Renders a terminal-style animation (typing effect + the resulting table)
   with [Pillow](https://python-pillow.org/) and saves it as a GIF.

To regenerate it:

```bash
uv run --with pillow python scripts/generate_demo_gif.py
```

No extra system dependencies (ffmpeg, ttyd, VHS, asciinema) are required —
everything runs through `uv`. If you'd rather record a real terminal/MCP
client session instead, [VHS](https://github.com/charmbracelet/vhs) or
[asciinema](https://asciinema.org/) + [agg](https://github.com/asciinema/agg)
both work too; just save the result to `docs/assets/demo.gif` and keep it
under ~30 seconds so it stays small enough for the README to load quickly.

## Available modules

| Module | Status | Data | Docs |
| --- | --- | --- | --- |
| [`mcp-ibge`](packages/mcp_ibge/) | **Stable** | IBGE — geographic locations (regions, states, municipalities, districts) and Agregados/SIDRA statistical aggregates | [README](packages/mcp_ibge/README.md) · [docs](packages/mcp_ibge/docs/) |
| [`mcp-dados-gov-br`](packages/mcp_dados_gov_br/) | **Beta** | dados.gov.br — Portal Brasileiro de Dados Abertos: dataset, organization, group and tag catalog search (CKAN API) | [README](packages/mcp_dados_gov_br/README.md) · [docs](docs/modules/dados-gov-br.md) |
| [`mcp-inep`](packages/mcp_inep/) | **Planning** (scaffold, only `status` tool) | INEP — Censo Escolar, Ideb, Saeb, Enem, schools by município, education indicators | [README](packages/mcp_inep/README.md) · [roadmap](docs/modules/inep.md) |
| [`mcp-bcb`](packages/mcp_bcb/) | **Planning** (scaffold, only `status` tool) | Banco Central do Brasil — SGS time series, exchange rates (PTAX), Selic | [README](packages/mcp_bcb/README.md) · [roadmap](docs/modules/bcb.md) |
| [`mcp-rio`](packages/mcp_rio/) | **Planning** (scaffold, only `status` tool) | Data.Rio — open data from the City of Rio de Janeiro | [README](packages/mcp_rio/README.md) · [roadmap](docs/modules/rio.md) |
| [`mcp-saude`](packages/mcp_saude/) | **Planning** (scaffold, only `status` tool) | DataSUS / Ministério da Saúde — health facilities (CNES) and indicators by município/UF | [README](packages/mcp_saude/README.md) · [roadmap](docs/modules/saude.md) |
| [`mcp-transparencia`](packages/mcp_transparencia/) | **Planning** (scaffold, only `status` tool) | Portal da Transparência (CGU) — public spending, contracts and sanctions | [README](packages/mcp_transparencia/README.md) · [roadmap](docs/modules/transparencia.md) |
| [`mcp-tesouro`](packages/mcp_tesouro/) | **Planning** (scaffold, only `status` tool) | Tesouro Nacional (SICONFI) — fiscal data for União, states and municípios | [README](packages/mcp_tesouro/README.md) · [roadmap](docs/modules/tesouro.md) |

## Secure by default

Every module in `mcp-data-br` follows the same security baseline — see
[docs/security.md](docs/security.md) for the full model and
[packages/mcp_ibge/docs/security.md](packages/mcp_ibge/docs/security.md) for
the `mcp-ibge` implementation details:

1. **No shell execution** — pure Python + `httpx`, no `subprocess`/`os.system`.
2. **No local file access** — tools never read or write user files; the only
   file I/O is loading `.env` config at startup.
3. **No arbitrary URLs** — tools take structured identifiers (codes, names,
   periods), never a full URL.
4. **Allowlisted domains only** — outbound requests are restricted to a fixed
   set of official hosts per module (e.g. `https://servicodados.ibge.gov.br`
   for `mcp-ibge`, `https://dados.gov.br` for `mcp-dados-gov-br`), checked
   both at startup and before every request.
5. **Timeouts** on every outbound HTTP call.
6. **Response size limits** — oversized responses are aborted, not buffered.
7. **Input validation** before any network call — invalid parameters return a
   structured error instead of reaching the upstream API.
8. **No stack traces in errors** — the MCP client gets a short error message;
   full tracebacks stay in `stderr` logs.
9. **stdio-safe logging** — all logs go to `stderr`, never `stdout`.
10. **No required API keys** — every data source works unauthenticated for
    read access. `mcp-dados-gov-br` accepts an *optional* consumer token
    (`DADOS_GOV_BR_API_TOKEN`) for the few resources that require it; if
    unset, those tools return a clear error instead of failing silently.

This is implemented by a small, centralized
[`mcp_ibge.security`](packages/mcp_ibge/src/mcp_ibge/security.py) module
(`assert_allowed_url`, `response_size_guard`, `safe_error_response`), covered
by [`tests/test_security.py`](packages/mcp_ibge/tests/test_security.py)
(external URL attempts, oversized responses, malicious inputs) — future
modules follow the same pattern.

## Planned modules

mcp-data-br is designed to grow. Beyond `mcp-ibge` (stable) and
`mcp-dados-gov-br` (beta), six modules already exist as **scaffolds** —
installable packages exposing only the shared `status` tool, with their data
tools, sources and challenges documented in
[docs/modules/](docs/modules/): [`mcp-inep`](docs/modules/inep.md) (education
— Censo Escolar, Ideb, Saeb, Enem), [`mcp-bcb`](docs/modules/bcb.md) (Banco
Central indicators), [`mcp-rio`](docs/modules/rio.md) (Rio de Janeiro open
data), [`mcp-saude`](docs/modules/saude.md) (DataSUS health data),
[`mcp-transparencia`](docs/modules/transparencia.md) (Portal da
Transparência) and [`mcp-tesouro`](docs/modules/tesouro.md) (Tesouro
Nacional / SICONFI). `mcp-sidra` (a dedicated SIDRA module, split out of
`mcp-ibge`) remains a documentation-only proposal — see
[docs/modules/sidra.md](docs/modules/sidra.md). See
[docs/roadmap.md](docs/roadmap.md) for details — the workspace is
structured so each scaffold's data tools can be implemented independently,
without touching other modules.

## Quick start

Requires **Python 3.11+** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/FilipePessoa30/mcp-data-br.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
uv run mcp-ibge
```

This starts the `mcp-ibge` server over `stdio`. For ready-to-use MCP client
configs (Claude Desktop, Cursor, Open WebUI) and example prompts, see
[examples/](examples/) and
[packages/mcp_ibge/docs/client_setup.md](packages/mcp_ibge/docs/client_setup.md).

### Try it without an MCP client

The `mcp-data-br` CLI calls the same tools directly from the terminal and
prints JSON — handy for testing without configuring Claude Desktop or
another MCP client:

```bash
uv run mcp-data-br ibge estados
uv run mcp-data-br ibge municipios --uf RJ
uv run mcp-data-br sidra metadados --agregado 6579 --pretty
```

See [packages/mcp_ibge/README.md#cli-mcp-data-br](packages/mcp_ibge/README.md#cli-mcp-data-br)
for the full command reference.

### Run it in Docker

A `Dockerfile` and `docker-compose.yml` are provided at the repository root,
so the server can run in an isolated container without installing Python or
`uv` on the host:

```bash
docker build -t mcp-ibge .
docker run -i --rm mcp-ibge                  # stdio (default)
docker compose up -d                         # streamable-http
```

See [docs/docker.md](docs/docker.md) for the full guide (environment
variables, healthcheck, MCP client config for `docker run`).

For the full feature list, available tools, configuration options and
roadmap of the IBGE module, see
**[packages/mcp_ibge/README.md](packages/mcp_ibge/README.md)**.

## Project layout

```
mcp-data-br/
├── pyproject.toml          # uv workspace root (virtual project)
├── packages/
│   ├── mcp_ibge/             # mcp-ibge: IBGE Localidades + Agregados/SIDRA (stable)
│   │   ├── src/mcp_ibge/
│   │   ├── tests/
│   │   ├── docs/
│   │   └── README.md
│   ├── mcp_dados_gov_br/     # mcp-dados-gov-br: dados.gov.br catalog (beta)
│   ├── mcp_inep/             # mcp-inep: INEP education data (scaffold, only `status`)
│   ├── mcp_bcb/              # mcp-bcb: Banco Central indicators (scaffold, only `status`)
│   ├── mcp_rio/              # mcp-rio: Data.Rio open data (scaffold, only `status`)
│   ├── mcp_saude/            # mcp-saude: DataSUS health data (scaffold, only `status`)
│   ├── mcp_transparencia/    # mcp-transparencia: Portal da Transparência (scaffold, only `status`)
│   └── mcp_tesouro/          # mcp-tesouro: Tesouro Nacional / SICONFI (scaffold, only `status`)
├── docs/                    # Monorepo-level docs (architecture, roadmap, security, data sources)
├── examples/                # MCP client configs (Claude Desktop, Cursor, Open WebUI) and prompts
└── evals/                   # Evaluation datasets and reports (placeholder)
```

Every scaffold package (`mcp_inep` and newer) follows the same internal
layout: `src/<pkg>/{server.py, config.py, schemas/, clients/, services/,
tools/, utils/}` plus `tests/` — see
[docs/architecture.md#adding-a-new-module](docs/architecture.md#adding-a-new-module).

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
[`packages/`](packages/). A entrega estável é o **mcp-ibge**, com dados de
localidades e agregados do SIDRA do IBGE — veja
[packages/mcp_ibge/README.md](packages/mcp_ibge/README.md). O
**mcp-dados-gov-br**, em beta, expõe busca e detalhamento de datasets,
organizações, grupos e tags do Portal Brasileiro de Dados Abertos (CKAN) —
veja [packages/mcp_dados_gov_br/README.md](packages/mcp_dados_gov_br/README.md).
Além desses, o workspace já inclui seis módulos em estágio de **scaffold**
(pacote instalável, apenas com a tool `status`, documentação e roadmap
prontos): **mcp-inep** (educação/INEP), **mcp-bcb** (Banco Central),
**mcp-rio** (dados abertos do Rio de Janeiro), **mcp-saude** (DataSUS),
**mcp-transparencia** (Portal da Transparência) e **mcp-tesouro** (Tesouro
Nacional/SICONFI). Todos seguem as mesmas convenções de respostas tipadas,
rastreáveis e seguras — veja [docs/roadmap.md](docs/roadmap.md) e
[docs/modules/](docs/modules/).

## License

[MIT](LICENSE)
