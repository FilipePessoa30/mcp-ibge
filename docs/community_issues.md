# Community Issues

A curated list of 25 starter tasks for `mcp-data-br`, split into three
difficulty tiers. Each entry has enough context to open as a GitHub issue
directly (see the
[good first issue template](https://github.com/FilipePessoa30/mcp-data-br/blob/main/.github/ISSUE_TEMPLATE/good_first_issue.yml)).

If you'd like to work on one of these:

1. Open an issue using the **good first issue** template, link back to the
   relevant entry below (e.g. `docs/community_issues.md#1-improve-the-readme-quick-start-example`),
   and mention that you're picking it up.
2. Read [CONTRIBUTING.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/CONTRIBUTING.md)
   for setup and the checks that run before a PR.
3. Keep the [response envelope](data_sources.md) and Portuguese tool-naming
   convention (`listar_`, `obter_`, `buscar_`, `consultar_`) in mind for any
   tool changes.

## Good first issues

### 1. Improve the README Quick Start example

**Context**: The README has a basic Quick Start / usage section, but the
example tool call could be more illustrative. Showing a slightly richer,
multi-step request — e.g. resolving a municipality and then querying its
population — with a trimmed example response would help newcomers
understand the response envelope faster.

**Tasks**

- [ ] Review the current Quick Start / usage section in `README.md`.
- [ ] Add a second, richer example (e.g. `consultar_populacao_municipio` or
  `gerar_perfil_municipal`) including a trimmed example response.
- [ ] Cross-link to [Municipal Profile](examples/municipal-profile.md) for
  the full version.

**Acceptance criteria**

- [ ] README renders correctly on GitHub (Markdown formatting, code fences).
- [ ] The example matches an actual tool name/parameters (cross-check with
  `packages/mcp_ibge/docs/tools.md`).
- [ ] No broken links.

**Difficulty**: Good first issue

### 2. Add tests for invalid UF values

**Context**: Many tools accept a `uf` parameter (2-letter Brazilian state
code). Test coverage for invalid `uf` inputs (lowercase, wrong length,
non-existent codes like `"ZZ"`) isn't consistent across tools.

**Tasks**

- [ ] Survey existing tests for `uf` validation under
  `packages/mcp_ibge/tests/`.
- [ ] Add parametrized tests for invalid `uf` inputs (lowercase, wrong
  length, non-existent code) for at least two tools that accept `uf`.
- [ ] Assert the response envelope has `ok: false` and a clear Portuguese
  message in `errors`.

**Acceptance criteria**

- [ ] New tests pass with `uv run --directory packages/mcp_ibge pytest`.
- [ ] No real network calls (use `respx` mocks where needed).
- [ ] `ruff check` / `ruff format --check` pass.

**Difficulty**: Good first issue

### 3. Add a reusable municipality fixture

**Context**: Several tests construct the same sample municipality data
inline (e.g. Niterói/RJ, IBGE code `3303302`). A shared `pytest` fixture
would reduce duplication and make it easier to add new tests.

**Tasks**

- [ ] Add a fixture (e.g. in `conftest.py`) returning a sample municipality
  dict (`codigo_ibge`, `nome`, `uf`, etc.).
- [ ] Refactor at least two existing tests to use the new fixture.
- [ ] Add a short docstring explaining what the fixture represents.

**Acceptance criteria**

- [ ] All tests still pass.
- [ ] No duplicated literal municipality data remains in the refactored
  tests.
- [ ] `ruff check` / `ruff format --check` pass.

**Difficulty**: Good first issue

### 4. Improve the ambiguous-municipality error message

**Context**: When a municipality name matches more than one result (e.g.
`"São José"`), the error message lists the matches but could be clearer
about how to disambiguate.

**Tasks**

- [ ] Locate where the ambiguous-match message is built (services layer).
- [ ] Improve the wording — still in Portuguese — to suggest concretely how
  to disambiguate (pass `uf`, use exact accents/spelling, etc.).
- [ ] Update any tests that assert on the exact message text.

**Acceptance criteria**

- [ ] The updated message is clear, actionable, in Portuguese, and matches
  the existing tone.
- [ ] Tests are updated and pass.
- [ ] [Municipal Profile](examples/municipal-profile.md#error-example-ambiguous-municipality)
  still matches the new message (update the example if needed).

**Difficulty**: Good first issue

### 5. Add a Claude Desktop example

**Context**: `examples/` contains agent recipe examples, and
[Claude Desktop](clients/claude-desktop.md) documents setup. A new,
ready-to-use prompt example tailored to Claude Desktop would help new users
get value quickly.

**Tasks**

- [ ] Pick a use case not yet covered (e.g. "which state in the Nordeste
  region has the largest estimated population?").
- [ ] Add a new example file under `examples/`, following the existing
  format.
- [ ] Reference it from [Claude Desktop](clients/claude-desktop.md) and/or
  the Examples section.

**Acceptance criteria**

- [ ] The example includes the prompt, expected tool call(s), and a sample
  response (or a link to one).
- [ ] It follows the [response envelope](data_sources.md) conventions.
- [ ] It is linked from `mkdocs.yml` nav if a new page was added.

**Difficulty**: Good first issue

### 6. Add a Cursor usage example

**Context**: [Cursor](clients/cursor.md) documents how to configure
`mcp-ibge`, but there isn't a worked example showing a realistic
coding-assistant prompt (e.g. "write a function that calls mcp-ibge to
fetch a municipality's population").

**Tasks**

- [ ] Write a short example showing a developer using Cursor + `mcp-ibge` to
  scaffold code that calls a tool.
- [ ] Add it to [Cursor](clients/cursor.md) or the Examples section.
- [ ] Verify the MCP config snippet in `docs/clients/cursor.md` matches
  [Installation](installation.md).

**Acceptance criteria**

- [ ] The example is self-contained and reproducible.
- [ ] `mkdocs build --strict` passes (no broken links).

**Difficulty**: Good first issue

### 7. Review Portuguese-language strings for consistency

**Context**: Response `data`/`warnings`/`errors` are in Portuguese by
convention, and some docs include Portuguese excerpts. A consistency pass
(accents, terminology — e.g. "município" vs. "municipio", "Unidade
Federativa" vs. "UF") would improve quality.

**Tasks**

- [ ] Search for Portuguese strings in `packages/mcp_ibge/src` (warnings,
  errors) and `docs/`.
- [ ] Build a short glossary of preferred terms (e.g. "código IBGE",
  "unidade federativa").
- [ ] Fix at least five inconsistencies found during the review.

**Acceptance criteria**

- [ ] The glossary is added as a short reference (e.g. in
  `packages/mcp_ibge/docs/` or `docs/`).
- [ ] Tests that assert on message text are updated and pass if the text
  changed.

**Difficulty**: Good first issue

### 8. Add more questions to the evals dataset

**Context**: `evals/` contains a dataset of questions used to evaluate
agent behavior with `mcp-ibge` (see [Evals](evals.md)). More coverage across
modules (localidades, agregados, geospatial) and edge cases (ambiguous
names, invalid UF, missing data) would strengthen the benchmark.

**Tasks**

- [ ] Review the current evals dataset structure under `evals/`.
- [ ] Add 5-10 new questions covering tools/edge cases not yet represented
  (e.g. geospatial tools, ambiguous names, invalid `uf`).
- [ ] Run the evals runner locally and confirm the new questions execute
  without errors.

**Acceptance criteria**

- [ ] New questions follow the existing dataset schema.
- [ ] The evals runner completes successfully with the new questions
  included.
- [ ] [Evals](evals.md) is updated if the dataset size/structure changed.

**Difficulty**: Good first issue

### 9. Add a new status badge to the README

**Context**: The README already has CI, license (MIT), Ruff and pytest
badges. A useful addition would be a docs-deploy badge (from
`.github/workflows/docs.yml`) or a "good first issues" badge linking to a
filtered GitHub issue search.

**Tasks**

- [ ] Pick one badge to add (docs deploy status, or a "good first issues"
  shields.io badge).
- [ ] Add the badge Markdown to `README.md` near the existing badges.
- [ ] Verify the badge renders and links correctly on GitHub.

**Acceptance criteria**

- [ ] The badge renders on GitHub.
- [ ] The badge links to a working URL (workflow run page or issue search).

**Difficulty**: Good first issue

### 10. Add a state (UF) comparison example

**Context**: [Compare Municipalities](examples/compare-municipalities.md)
covers comparing municipalities with `comparar_municipios`. A complementary
example comparing two or more **states (UFs)** — e.g. estimated population
by region — using existing localidades/agregados tools would round out the
Examples section.

**Tasks**

- [ ] Design a prompt comparing 2-3 states by an existing indicator (e.g.
  estimated population).
- [ ] Document the expected tool-call sequence and an example response.
- [ ] Add the new example under `docs/examples/` and link it from
  `mkdocs.yml` nav.

**Acceptance criteria**

- [ ] The new page builds with `mkdocs build --strict`.
- [ ] The example only uses tools/indicators that exist today (no invented
  data).
- [ ] It is linked from the Examples section in `mkdocs.yml` nav.

**Difficulty**: Good first issue

## Intermediate

### 1. Implement a new SIDRA aggregate tool

**Context**: `mcp-ibge` already exposes a SIDRA query builder
(`consultar_agregado`) and a population indicator
(`consultar_populacao_municipio`). Adding a focused tool for another
widely-used SIDRA aggregate — e.g. the PNAD Contínua unemployment rate —
would make common queries easier without requiring users to know aggregate
and variable IDs.

**Tasks**

- [ ] Research a suitable SIDRA aggregate (e.g. PNAD Contínua unemployment
  rate) and confirm its aggregate/variable IDs via the public API.
- [ ] Implement a new tool (e.g. `consultar_taxa_desocupacao`) following the
  existing agregados conventions (clients/services/schemas/tools layers).
- [ ] Add `respx`-mocked tests covering success, no-data, and
  invalid-parameter cases.
- [ ] Document the new tool in `packages/mcp_ibge/docs/tools.md` and
  [Tools → Agregados/SIDRA](tools/agregados.md).

**Acceptance criteria**

- [ ] The tool follows the response envelope and the `consultar_` naming
  convention.
- [ ] Tests pass and `ruff` is clean.
- [ ] Docs include limitations (e.g. the aggregate may be discontinued or
  renamed after a new Census).

**Difficulty**: Intermediate

### 2. Improve cache observability and configurability

**Context**: `mcp-ibge` has an in-memory cache (TTL + max size), and a
recent change added server observability metrics. The cache could expose
more useful metrics (hit rate per tool/endpoint) and allow per-tool TTL
overrides.

**Tasks**

- [ ] Review `utils/cache.py` and the existing observability metrics.
- [ ] Add per-tool (or per-endpoint) cache hit/miss counters to the metrics
  output.
- [ ] (Optional) Allow a per-tool TTL override via configuration.
- [ ] Add tests for the new metrics/configuration behavior.

**Acceptance criteria**

- [ ] Existing cache behavior and tests are unchanged unless explicitly
  improved.
- [ ] New metrics are documented (e.g. in [Security](security.md) or a new
  observability section).
- [ ] `ruff` and `pytest` are clean.

**Difficulty**: Intermediate

### 3. Extend geospatial tools to more territorial levels

**Context**: The [geospatial tools](tools/geospatial.md) currently cover
municipality-level meshes, bounding boxes and GeoJSON generation. Extending
this to other territorial levels (e.g. state/UF or micro-region) would
unlock more mapping use cases.

**Tasks**

- [ ] Review [Geospatial](tools/geospatial.md) and the existing
  malha/bbox/GeoJSON tools.
- [ ] Add support for at least one additional territorial level (e.g. UF or
  micro-region) to `gerar_geojson_municipios`/`obter_bbox_municipio`, or new
  equivalent tools.
- [ ] Add `respx`-mocked tests for the new territorial level, including the
  "simplified geometry" warning.
- [ ] Update [Geospatial](tools/geospatial.md) and
  [Education Activity](examples/education-activity.md) if relevant.

**Acceptance criteria**

- [ ] The new territorial level follows the existing
  `*_nao_resolvidos`/warnings conventions.
- [ ] Tests pass and `ruff` is clean.
- [ ] Docs are updated with a usage example.

**Difficulty**: Intermediate

### 4. Improve the evals HTML report

**Context**: The evals runner (`evals/`) already produces a report (see
[Evals](evals.md)). Adding visual summaries — pass rate per tool/module,
latency — would make it easier to spot regressions.

**Tasks**

- [ ] Review `evals/runner.py` and the current report format.
- [ ] Add a per-tool/module breakdown table and a simple chart (lightweight
  templating/plotting, avoiding heavy new dependencies if possible).
- [ ] Regenerate a sample report and check it renders correctly in a
  browser.

**Acceptance criteria**

- [ ] Report generation doesn't require network access beyond what evals
  already uses.
- [ ] [Evals](evals.md) is updated to describe the new report sections.
- [ ] Any new dependency is discussed in the issue/PR before being added.

**Difficulty**: Intermediate

### 5. Add a LangChain integration example

**Context**: `mcp-ibge` speaks the MCP protocol, and LangChain has MCP
adapter support (e.g. `langchain-mcp-adapters`). A runnable example showing
how to use `mcp-ibge` tools from a LangChain agent would broaden the
audience.

**Tasks**

- [ ] Research LangChain's MCP tool-adapter approach.
- [ ] Add a runnable example (script or notebook) under `examples/` that
  loads `mcp-ibge` tools into a LangChain agent and runs a sample query.
- [ ] Document setup/requirements — keep any new dependencies optional/dev
  only, scoped to the example.
- [ ] Add a docs page or section under Clients or Examples.

**Acceptance criteria**

- [ ] The example runs against the local `mcp-ibge` server (`stdio` or
  `streamable-http`).
- [ ] New dependencies are isolated to the example, not added to the core
  package.
- [ ] Docs/nav are updated.

**Difficulty**: Intermediate

### 6. Add a LlamaIndex integration example

**Context**: Similar to the LangChain example — LlamaIndex supports
MCP-based tools, and a runnable example would help users building RAG/agent
apps with LlamaIndex.

**Tasks**

- [ ] Research LlamaIndex's MCP tool integration.
- [ ] Add a runnable example under `examples/` that loads `mcp-ibge` tools
  into a LlamaIndex agent.
- [ ] Document setup/requirements — keep any new dependencies optional/dev
  only, scoped to the example.
- [ ] Add a docs page or section under Clients or Examples.

**Acceptance criteria**

- [ ] The example runs against the local `mcp-ibge` server.
- [ ] New dependencies are isolated to the example.
- [ ] Docs/nav are updated.

**Difficulty**: Intermediate

### 7. Add a Dockerfile

**Context**: `mcp-ibge` currently runs via `uv run`/`uvx`. A Dockerfile
would let users run it — especially with `streamable-http` — without
installing Python/uv locally, useful for [Open WebUI](clients/open-webui.md)
setups.

**Tasks**

- [ ] Add a multi-stage Dockerfile (based on an official Python image) that
  installs the workspace via `uv` and runs `mcp-ibge`.
- [ ] Support both `stdio` and `streamable-http` transports via environment
  variables.
- [ ] Add basic usage instructions to [Installation](installation.md).
- [ ] (Optional) Add a `docker build`/smoke-test step to CI.

**Acceptance criteria**

- [ ] `docker build` succeeds, and the resulting image runs the server with
  `streamable-http`.
- [ ] The image respects the existing `MCP_IBGE_*`/`MCP_DATA_BR_*`
  environment variables.
- [ ] Docs include an example `docker run` command.

**Difficulty**: Intermediate

### 8. Prepare the mcp-ibge package for PyPI

**Context**: [Installation](installation.md) notes that `mcp-ibge` is "not
yet published to PyPI" and recommends development mode. Publishing would
enable the already-documented `uvx mcp-ibge` flow.

**Tasks**

- [ ] Review `packages/mcp_ibge/pyproject.toml` for PyPI readiness
  (metadata, classifiers, README rendering, license file).
- [ ] Add a release workflow (or document a manual release process) under
  `.github/workflows/`.
- [ ] Do a dry-run build (`uv build`) and check the artifact (e.g. with
  `twine check`).
- [ ] Note in [Installation](installation.md) what changes once published
  (the actual publish step requires maintainer-held PyPI credentials).

**Acceptance criteria**

- [ ] `uv build` produces a valid sdist/wheel with correct metadata.
- [ ] The release process is documented (in `CONTRIBUTING.md` or a new docs
  page).
- [ ] The actual PyPI publish is performed by/with a maintainer.

**Difficulty**: Intermediate

### 9. Add a CLI for direct tool calls

**Context**: Today, `mcp-ibge` tools are only reachable via an MCP client. A
thin CLI (e.g. `mcp-ibge-cli consultar-populacao --nome Niteroi --uf RJ`)
would help with debugging and quick lookups without an LLM in the loop.

**Tasks**

- [ ] Design a minimal CLI (e.g. `argparse` or `typer`, as an optional/dev
  dependency) that calls the same service-layer functions used by the
  tools.
- [ ] Implement commands for 2-3 representative tools (one per module:
  localidades, agregados, geospatial).
- [ ] Output the same response envelope as JSON to stdout.
- [ ] Add tests and document usage in the module README.

**Acceptance criteria**

- [ ] CLI commands return the same envelope shape as the MCP tools (verified
  by tests).
- [ ] Any new dependency is optional and documented.
- [ ] `ruff` and `pytest` are clean.

**Difficulty**: Intermediate

### 10. Expand the MkDocs documentation site

**Context**: A MkDocs Material site already exists under `docs/` (Home,
Getting Started, Installation, Clients, Modules, Tools, Examples, Reference,
Contributing) with a GitHub Pages deploy workflow. There's room to expand
it further — a FAQ/troubleshooting page, a glossary of the Portuguese terms
used in `data`/`warnings`/`errors`, or more end-to-end examples.

**Tasks**

- [ ] Identify gaps in the current site (e.g. FAQ/troubleshooting, glossary
  of Portuguese response terms).
- [ ] Add one or two new pages addressing those gaps, linked from
  `mkdocs.yml` nav.
- [ ] Run `mkdocs build --strict` to confirm there are no broken links or
  warnings.

**Acceptance criteria**

- [ ] `mkdocs build --strict` passes.
- [ ] New pages are linked from the nav and cross-referenced from related
  existing pages.

**Difficulty**: Intermediate

## Advanced

### 1. Bootstrap the mcp-inep module

**Context**: [Roadmap](roadmap.md) lists `mcp-inep` (INEP — Censo Escolar,
ENEM, IDEB) as a planned module, following the same workspace/package
conventions as `mcp-ibge` (response envelope, FastMCP, `respx` tests).

**Tasks**

- [ ] Open a discussion issue first (per
  [Architecture → Adding a new module](architecture.md#adding-a-new-module))
  to confirm scope — which INEP datasets/APIs to start with.
- [ ] Scaffold `packages/mcp_inep` mirroring `mcp-ibge`'s structure (config,
  clients, schemas, services, tools, tests, docs, README).
- [ ] Implement 2-3 initial tools (e.g. listing schools by municipality,
  IDEB by school/municipality).
- [ ] Add the new package to the uv workspace and CI.
- [ ] Add module docs under Modules and tool docs under Tools.

**Acceptance criteria**

- [ ] The new package installs via `uv sync --all-extras` and runs
  standalone (`uv run mcp-inep`).
- [ ] Tests pass with `respx` mocks (no real network).
- [ ] It follows the same response envelope, naming convention, and security
  baseline as `mcp-ibge`.
- [ ] [Roadmap](roadmap.md) status is updated, and the module is documented
  under Modules.

**Difficulty**: Advanced

### 2. SIDRA semantic search

**Context**: SIDRA has thousands of aggregates, each with many variables —
`consultar_agregado` requires knowing their IDs. A semantic search tool
(`buscar_agregados_sidra`) that maps natural-language queries (e.g.
"population by municipality") to candidate aggregate/variable IDs would make
SIDRA much more accessible to agents.

**Tasks**

- [ ] Investigate how to obtain/cache the catalog of SIDRA aggregates and
  variables (IBGE metadata endpoints).
- [ ] Build a local index over aggregate/variable names and descriptions
  (e.g. embeddings or a simple keyword/TF-IDF index — avoid heavy runtime
  dependencies if possible).
- [ ] Implement `buscar_agregados_sidra(consulta: str)`, returning ranked
  candidates with IDs, names, and example periods.
- [ ] Add tests with a small fixture catalog (no real network in tests).
- [ ] Document the indexing/refresh strategy (how the catalog stays up to
  date) in `packages/mcp_ibge/docs`.

**Acceptance criteria**

- [ ] The tool follows the response envelope and the `buscar_` naming
  convention.
- [ ] The index build/refresh doesn't run on every request (cached or
  precomputed).
- [ ] Tests pass without real network access.
- [ ] Docs cover limitations (catalog freshness, ranking quality).

**Difficulty**: Advanced

### 3. Geospatial choropleth tool

**Context**: Geospatial tools produce GeoJSON meshes; agregados tools
produce indicators (e.g. population). A new tool combining both — attaching
an indicator value to each feature's properties for a set of
municipalities/states — would enable choropleth maps directly from a single
call.

**Tasks**

- [ ] Design a tool (e.g. `gerar_geojson_coropletico`) that takes a list of
  IBGE codes plus an indicator, fetches the mesh (geospatial) and the
  indicator values (agregados), and merges them into a single
  `FeatureCollection` with `properties.valor`.
- [ ] Reuse existing services — don't duplicate mesh-fetching or
  indicator-fetching logic.
- [ ] Handle partial failures (some codes resolved, others not) using the
  existing `*_nao_resolvidos`/warnings conventions.
- [ ] Add `respx`-mocked tests covering full success, partial resolution,
  and the "simplified geometry" warning.
- [ ] Add a new example under Examples showing the output rendered as a
  choropleth (e.g. with Folium/QGIS instructions).

**Acceptance criteria**

- [ ] The tool follows the response envelope, naming convention, and
  existing limits (e.g. max 10 territories per call).
- [ ] Tests pass and `ruff` is clean.
- [ ] The new example documents how to visualize the result.

**Difficulty**: Advanced

### 4. Agent benchmark suite

**Context**: `evals/` already runs a dataset of questions against the
server (see [Evals](evals.md)). A broader "agent benchmark" would compare
multiple agent configurations (different models/clients) on accuracy,
tool-call efficiency (e.g. using `gerar_perfil_municipal` instead of three
separate calls), and adherence to conventions (response envelope, no
invented data).

**Tasks**

- [ ] Define benchmark dimensions: accuracy vs. ground truth, number of tool
  calls, and handling of ambiguous/error cases.
- [ ] Extend `evals/` (or add a new `benchmarks/` directory) with scoring
  logic for these dimensions, reusing the existing dataset where possible.
- [ ] Add a way to run the benchmark against at least two different
  configurations and compare results.
- [ ] Produce a comparison report (extending or alongside the existing evals
  report).

**Acceptance criteria**

- [ ] The benchmark runs reproducibly, and adding new configurations is
  documented.
- [ ] Results are summarized in a report (HTML/Markdown).
- [ ] [Evals](evals.md) is updated to describe the benchmark and how to run
  it.

**Difficulty**: Advanced

### 5. MCP security scanner

**Context**: A recent change centralized request safeguards (domain
allowlists, response size limits, timeouts, etc. — see
[Security](security.md) and `packages/mcp_ibge/docs/security.md`). A
standalone scanner that checks an `mcp-data-br` server's configuration and
tools against this security baseline would help catch regressions and help
future modules (e.g. `mcp-inep`) start out secure.

**Tasks**

- [ ] Define a checklist from [Security](security.md) /
  `packages/mcp_ibge/docs/security.md` (e.g. allowed domains enforced,
  response size limits, timeouts configured, no secrets in logs, structured
  stderr logging).
- [ ] Implement a scanner (script or small CLI) that inspects a module's
  config/source for these properties (static checks) and/or runs it and
  exercises the safeguards (dynamic checks).
- [ ] Run it against `packages/mcp_ibge` and report a pass/fail summary per
  checklist item.
- [ ] Add it to CI as a non-blocking step initially.
- [ ] Document the checklist and scanner usage in [Security](security.md).

**Acceptance criteria**

- [ ] The scanner runs against `packages/mcp_ibge` and reports a clear
  pass/fail summary.
- [ ] Checklist items are traceable to [Security](security.md).
- [ ] CI integration is documented, even if non-blocking.

**Difficulty**: Advanced
