# Contributing to mcp-ibge

Thanks for your interest in contributing — bug reports, new tools,
documentation and tests are all welcome.

## Setup

Requires **Python 3.11+**. [uv](https://docs.astral.sh/uv/) is recommended.

```bash
git clone https://github.com/FilipePessoa30/mcp-ibge.git
cd mcp-ibge
uv sync --all-extras
```

Run the server locally:

```bash
uv run mcp-ibge
# or, equivalent:
uv run python -m mcp_ibge.server
```

## Checks before opening a PR

```bash
# Lint
uv run ruff check .

# Format
uv run ruff format .

# Tests (no network required — IBGE responses are mocked with respx)
uv run pytest

# Optional type checking
uv run mypy
```

CI ([.github/workflows/ci.yml](.github/workflows/ci.yml)) runs `uv sync`,
`ruff check`, `ruff format --check` and `pytest` on every push/PR; `mypy`
runs as an optional, non-blocking step.

## Project layout

```
mcp-ibge/
├── src/mcp_ibge/
│   ├── server.py        # FastMCP wiring, tool registration, `main()` entrypoint
│   ├── config.py         # Settings (pydantic-settings): URLs, timeouts, cache
│   ├── logging_config.py # stderr logging (stdio-safe)
│   ├── clients/           # Thin HTTP layer (base, localidades, agregados)
│   ├── schemas/           # Pydantic models and the response envelope
│   ├── services/          # Business logic (filters, aliases, indicators)
│   ├── tools/              # FastMCP tools (`@mcp.tool()`)
│   └── utils/              # cache, text normalization, exceptions
├── tests/                  # Unit tests (pytest + respx)
├── examples/               # Example MCP client configs and queries
└── docs/                   # Architecture, tools reference, data sources, security
```

See [docs/architecture.md](docs/architecture.md) for a detailed description
of each layer and the request flow.

## Guidelines

- **Response envelope**: every tool must return
  `{"metadata": {...}, "data": ...}` on success or
  `{"metadata": {...}, "error": "..."}` on failure — see
  [docs/data_sources.md](docs/data_sources.md).
- **Validate inputs**: validate parameters in `utils/validation.py` before
  any network call (see [docs/security.md](docs/security.md)).
- **Tests with `respx`**: any new client/endpoint needs mocked HTTP tests —
  no real network access in the test suite.
- **Tool naming**: tool names follow the existing Portuguese verb prefixes
  (`listar_`, `obter_`, `buscar_`, `consultar_`), matching the IBGE domain.
- **Docs**: when you add or change a tool, update `docs/tools.md`,
  `README.md` and `CHANGELOG.md` accordingly.

## Reporting bugs / requesting features

Please use the issue templates (Bug report / Feature request) so we have the
context needed to help.

## Code of Conduct

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).
