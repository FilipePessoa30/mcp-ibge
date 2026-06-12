## Description

<!-- What does this PR change, and why? -->

## Related issue

Closes #

## Type of change

- [ ] Bug fix
- [ ] New tool / feature
- [ ] New module
- [ ] Documentation
- [ ] Refactor / internal change
- [ ] Other:

## Checklist

- [ ] `uv run ruff check packages/mcp_ibge` passes
- [ ] `uv run ruff format --check packages/mcp_ibge` passes
- [ ] `uv run --directory packages/mcp_ibge pytest` passes
- [ ] Added/updated tests for the change (mocked with `respx`, no real network access)
- [ ] New/changed tools follow the [response envelope](https://github.com/FilipePessoa30/mcp-data-br/blob/main/docs/data_sources.md) and the `listar_/obter_/buscar_/consultar_` naming convention
- [ ] Updated docs (`packages/mcp_ibge/docs/tools.md`, module `README.md`, and/or `docs/`) if behavior or tools changed
- [ ] Updated `CHANGELOG.md`

## Additional context

<!-- Anything else reviewers should know: design decisions, follow-up work, screenshots, etc. -->
