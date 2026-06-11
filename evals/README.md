# Evals

This directory is the home for evaluation datasets and reports for
`mcp-data-br` modules: structured sets of prompts/queries with expected tool
calls and/or expected results, used to check that tools behave correctly and
to catch regressions as modules evolve.

This is a **placeholder for an upcoming evaluation framework** — no
automated runner exists yet. The structure below is reserved so datasets and
reports have a stable home as they're added.

## Layout

- [`datasets/`](datasets/) — eval cases, organized per module (e.g.
  `datasets/mcp_ibge/`). Each case typically pairs a natural-language prompt
  or direct tool call with the expected tool, arguments, and/or expected
  shape of the response.
- [`reports/`](reports/) — output of eval runs (e.g. pass/fail summaries,
  comparisons across versions).

## Why

The [response envelope](../docs/data_sources.md) used by every tool
(`metadata` + `data`/`error`) makes responses traceable to their source,
which is also what makes them useful as eval fixtures: a dataset entry can
assert on `data` shape while `metadata.source_url` documents where the
expected values came from.

As modules are added (see [docs/roadmap.md](../docs/roadmap.md)), their eval
datasets should live under `datasets/mcp_<name>/`.
