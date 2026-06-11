# Contributing to mcp-data-br

Thanks for your interest in contributing — bug reports, new tools, new
modules, documentation and tests are all welcome.

## Setup

`mcp-data-br` is a [uv workspace](https://docs.astral.sh/uv/concepts/projects/workspaces/)
(monorepo). Requires **Python 3.11+** and [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git mcp-data-br
cd mcp-data-br
uv sync --all-extras
```

This installs every package under `packages/` (currently `mcp-ibge`) and all
dev dependencies into a single shared `.venv` at the repository root.

Run the `mcp-ibge` server locally:

```bash
uv run mcp-ibge
# or, equivalent:
uv run python -m mcp_ibge.server
```

## Checks before opening a PR

Checks run against the package(s) you changed. For `mcp-ibge`:

```bash
# Lint
uv run ruff check packages/mcp_ibge

# Format
uv run ruff format packages/mcp_ibge

# Tests (no network required — IBGE responses are mocked with respx)
uv run --directory packages/mcp_ibge pytest

# Optional type checking
uv run --directory packages/mcp_ibge mypy
```

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs `uv sync`,
`ruff check`, `ruff format --check` and `pytest` on every push/PR; `mypy`
runs as an optional, non-blocking step.

## Project layout

```
mcp-data-br/
├── pyproject.toml          # uv workspace root (virtual project)
├── packages/
│   └── mcp_ibge/
│       ├── pyproject.toml
│       ├── src/mcp_ibge/
│       │   ├── server.py        # FastMCP wiring, tool registration, `main()` entrypoint
│       │   ├── config.py         # Settings (pydantic-settings): URLs, timeouts, cache
│       │   ├── logging_config.py # stderr logging (stdio-safe)
│       │   ├── clients/           # Thin HTTP layer (base, localidades, agregados)
│       │   ├── schemas/           # Pydantic models and the response envelope
│       │   ├── services/          # Business logic (filters, aliases, indicators)
│       │   ├── tools/              # FastMCP tools (`@mcp.tool()`)
│       │   └── utils/              # cache, text normalization, exceptions
│       ├── tests/                  # Unit tests (pytest + respx)
│       ├── docs/                   # Module docs: tools reference, architecture, security, data sources
│       └── README.md
├── docs/                    # Monorepo-level docs (architecture, roadmap, security, data sources)
├── examples/                # Example MCP client configs and prompts
└── evals/                   # Evaluation datasets and reports (placeholder)
```

See [docs/architecture.md](docs/architecture.md) for the workspace-level
architecture and module conventions, and
[packages/mcp_ibge/docs/architecture.md](packages/mcp_ibge/docs/architecture.md)
for a detailed description of `mcp-ibge`'s internal layers and request flow.

## Guidelines

- **Response envelope**: every tool must return
  `{"metadata": {...}, "data": ...}` on success or
  `{"metadata": {...}, "error": "..."}` on failure — see
  [docs/data_sources.md](docs/data_sources.md).
- **Validate inputs**: validate parameters before any network call (see
  [docs/security.md](docs/security.md) and
  [packages/mcp_ibge/docs/security.md](packages/mcp_ibge/docs/security.md)).
- **Tests with `respx`**: any new client/endpoint needs mocked HTTP tests —
  no real network access in the test suite.
- **Tool naming**: tool names follow the existing Portuguese verb prefixes
  (`listar_`, `obter_`, `buscar_`, `consultar_`), matching the data domain.
- **Docs**: when you add or change a tool, update the relevant module's
  `docs/tools.md`, its `README.md` and the root `CHANGELOG.md`.

### Adding a new module

If you're proposing a new MCP server (e.g. for another data source), see
[docs/architecture.md#adding-a-new-module](docs/architecture.md#adding-a-new-module)
and [docs/roadmap.md](docs/roadmap.md) for the expected structure and
conventions. Open an issue first to discuss scope before starting a large
new module.

## Reporting bugs / requesting features

Please use the issue templates (Bug report / Feature request) so we have the
context needed to help.

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
