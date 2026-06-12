# Evals

The [`evals/`](https://github.com/FilipePessoa30/mcp-ibge/tree/main/evals)
directory contains an evaluation framework to check whether an agent (e.g. an
LLM with access to `mcp-data-br` tools) uses the MCP tools exposed by
`mcp_ibge` correctly — picking the right tool, reading the right response
fields, citing the source, and reacting appropriately to `warnings`/`errors`.

Everything here is **stdlib-only** (`json`, `argparse`, `html`, `pathlib`,
`typing`): running the evals requires no paid API and no language model.
Producing the agent's responses (which may involve an LLM) is the
responsibility of whoever generates the `--results` file — the runner only
compares that file against the datasets.

> 🇧🇷 **Nota**: o framework e os datasets estão documentados em português em
> [`evals/README.md`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/evals/README.md);
> esta página é um resumo em inglês.

## Layout

```text
evals/
  README.md
  datasets/
    localidades_basic.json   # Localidades tools (municipalities, regions, districts)
    ambiguity_cases.json     # Ambiguous names (e.g. "São José") and how the agent should handle them
    sidra_basic.json         # Agregados/SIDRA tools
  metrics.py                  # Metric implementations
  runner.py                   # CLI that runs the evals and generates the HTML report
  example_results.json        # Example results file (runner input format)
  reports/
    example_report.html       # Report generated from example_results.json
```

## Dataset: case schema

Each file in `datasets/*.json` contains a list of cases. The runner loads and
concatenates all files (sorted by `id`), so the file name is just an
organizational grouping by topic.

Each case has the following fields:

| Field | Type | Description |
| --- | --- | --- |
| `id` | `string` | Unique case identifier (e.g. `"loc_001"`). |
| `user_question` | `string` | Natural-language question that would be asked of the agent. |
| `expected_tools` | `list[string]` | MCP tools the agent should call. The **first** item is the "primary tool" — its `result` is used by the field, source, warning and envelope-validity metrics. |
| `expected_fields` | `list[object]` | Checks against the primary tool's response envelope (syntax below). |
| `expected_answer_contains` | `list[string]` | Substrings expected in the agent's final answer (`final_answer`), case-insensitive. |
| `should_warn` | `boolean` | Whether the primary tool's response should contain `warnings` (e.g. ambiguous name, year not given). |
| `difficulty` | `string` | `"easy"`, `"medium"` or `"hard"` — informational only, doesn't affect metrics. |
| `category` | `string` | Case category (e.g. `"localidades"`, `"ambiguity"`, `"sidra"`) — used to group metrics in the report. |

### `expected_fields` syntax

Each item in `expected_fields` has a `"path"` and **exactly one** of the
following operators:

| Operator | Meaning |
| --- | --- |
| `"equals": <value>` | The value at `path` must equal `<value>`. |
| `"contains": <value>` | `<value>` must be contained in the value at `path` (string, list, etc.). |
| `"min_length": <n>` | `len(value)` must be `>= n`. |
| `"not_null": true/false` | `path` must exist and be (or not be) `None`. |
| `"in": [<values>]` | The value at `path` must be one of `<values>`. |

`path` is a `.`-separated string, resolved against the primary tool's
response envelope (`{ok, data, metadata, warnings, errors}`). Purely numeric
segments index into lists. Examples:

- `"data"` → the envelope's `data` field.
- `"data.0.localidade_nome"` → `localidade_nome` of the first item in `data`.
- `"metadata.params.uf"` → `metadata["params"]["uf"]`.
- `"errors"` with `"min_length": 1` → at least one error was returned.

### Example case

```json
{
  "id": "loc_001",
  "user_question": "Qual é o código IBGE de Niterói, RJ?",
  "expected_tools": ["obter_codigo_municipio"],
  "expected_fields": [
    { "path": "data", "equals": 3303302 }
  ],
  "expected_answer_contains": ["3303302"],
  "should_warn": false,
  "difficulty": "easy",
  "category": "localidades"
}
```

## Results file (`--results`)

The runner **does not call the agent** — it reads a JSON file with results
already produced by running an agent against the dataset cases. The file is
a list of objects, one per evaluated case:

```json
[
  {
    "id": "loc_001",
    "tool_calls": [
      {
        "name": "obter_codigo_municipio",
        "arguments": { "nome": "Niterói", "uf": "RJ" },
        "result": { "ok": true, "data": 3303302, "metadata": { "...": "..." }, "warnings": [], "errors": [] }
      }
    ],
    "final_answer": "O código IBGE de Niterói (RJ) é 3303302."
  }
]
```

- `id`: must match the `id` of a dataset case.
- `tool_calls`: the tools called by the agent to answer `user_question`, in
  call order. Each item has `name` (tool name), `arguments` (arguments used)
  and `result` (the response envelope returned by the tool, in `{ok, data,
  metadata, warnings, errors}` format).
- `final_answer`: the final natural-language response given to the user.

Dataset cases with no corresponding entry in the results file are treated as
**not attempted** (`attempted=False`) and score `0`/`✗` on every metric —
this penalizes coverage gaps in the agent.

See
[`example_results.json`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/evals/example_results.json)
for a full example (including a case with the wrong tool and three
not-attempted cases).

## Metrics

For each case, the primary tool is `expected_tools[0]`; its `result` (if the
tool was called) is the "primary result" used by the metrics below.

| Metric | Type | What it measures |
| --- | --- | --- |
| `tool_selection_accuracy` | fraction 0–1 | How many of `expected_tools` were called by the agent (in any order). |
| `field_accuracy` | fraction 0–1 | How many `expected_fields` checks passed against the primary result. |
| `source_presence` | boolean | Whether `metadata.source_url` is present and `metadata.source_name` mentions "IBGE" in the primary result. |
| `warning_correctness` | boolean | Whether the presence of `warnings` in the primary result matches `should_warn`. |
| `structured_output_validity` | boolean | Whether the primary result follows the `{ok, data, metadata, warnings, errors}` envelope contract, with all 11 `metadata` fields and `warnings`/`errors` as lists of `{message, code}`. |
| `answer_contains_accuracy` | fraction 0–1 | How many `expected_answer_contains` strings appear in `final_answer` (case-insensitive). Extra metric, beyond the 5 originally requested. |

Not-attempted cases score `0`/`false` on every metric. The report shows the
overall average, per-`category` averages, and per-case detail.

## Running the evals

```bash
python evals/runner.py --results path/to/results.json
```

Options:

- `--results PATH` (required): JSON file with the agent's results.
- `--datasets DIR` (default: `evals/datasets`): directory with `*.json` datasets.
- `--output PATH` (default: `evals/reports/report.html`): path of the generated HTML report.

Example, using the sample results bundled in the repository:

```bash
cd evals
python runner.py --results example_results.json --output reports/example_report.html
```

This prints a summary to the terminal (overall and per-category) and writes a
self-contained HTML report (no external dependencies, inline CSS) to
`reports/example_report.html`, with a table per case showing expected vs.
called tools and the result of each metric.

## Status and roadmap

This is a **placeholder** framework — datasets are small and illustrative.
See [Roadmap](roadmap.md#cross-cutting) for plans to grow the evaluation
framework as new modules and tools are added.
