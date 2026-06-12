#!/usr/bin/env python3
"""Runner dos evals de `mcp-data-br`: compara resultados de um agente com os datasets.

Uso:
    python evals/runner.py --results path/to/results.json
    python evals/runner.py --results path/to/results.json --output evals/reports/report.html
    python evals/runner.py --results path/to/results.json --datasets evals/datasets

Não depende de nenhum serviço externo nem de modelo de linguagem: apenas lê
os datasets JSON em `--datasets`, o arquivo de resultados produzido por um
agente em `--results` (ver `README.md` para o formato), calcula as métricas
de `metrics.py` e escreve um relatório HTML autocontido em `--output`. Um
resumo também é impresso no terminal.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path
from typing import Any

from metrics import SUMMARY_METRICS, aggregate, evaluate_case

_DEFAULT_DATASETS_DIR = Path(__file__).parent / "datasets"
_DEFAULT_OUTPUT = Path(__file__).parent / "reports" / "report.html"

_METRIC_LABELS = {
    "tool_selection_accuracy": "Tool selection",
    "field_accuracy": "Field accuracy",
    "source_presence": "Source presence",
    "warning_correctness": "Warning correctness",
    "structured_output_validity": "Structured output",
    "answer_contains_accuracy": "Answer contains",
}

# Métricas booleanas (exibidas como ✓/✗); as demais são fração 0..1 (exibidas como %).
_BOOLEAN_METRICS = {"source_presence", "warning_correctness", "structured_output_validity"}


def load_dataset(datasets_dir: Path) -> list[dict[str, Any]]:
    """Carrega e concatena todos os arquivos `*.json` em `datasets_dir`.

    Cada arquivo deve conter uma lista de casos (ver `README.md` para o
    schema de cada caso). Os casos são ordenados por `id` para um relatório
    estável.
    """
    cases: list[dict[str, Any]] = []
    for path in sorted(datasets_dir.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise ValueError(f"{path}: esperada uma lista de casos, recebido {type(data).__name__}")
        for case in data:
            for required in ("id", "user_question", "expected_tools", "category"):
                if required not in case:
                    raise ValueError(f"{path}: caso sem o campo obrigatório {required!r}: {case}")
            cases.append(case)

    cases.sort(key=lambda case: case["id"])
    return cases


def load_results(results_path: Path) -> dict[str, dict[str, Any]]:
    """Carrega o arquivo de resultados de um agente, indexado por `id` do caso."""
    data = json.loads(results_path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError(
            f"{results_path}: esperada uma lista de resultados, recebido {type(data).__name__}"
        )

    results: dict[str, dict[str, Any]] = {}
    for item in data:
        if "id" not in item:
            raise ValueError(f"{results_path}: resultado sem o campo 'id': {item}")
        results[item["id"]] = item
    return results


def run_eval(cases: list[dict[str, Any]], results: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Avalia cada caso do dataset contra o resultado correspondente do agente."""
    evaluations = []
    for case in cases:
        agent_result = results.get(case["id"])
        evaluation = evaluate_case(case, agent_result)
        evaluation["category"] = case["category"]
        evaluation["difficulty"] = case.get("difficulty", "")
        evaluation["user_question"] = case["user_question"]
        evaluation["expected_tools"] = case.get("expected_tools", [])
        evaluations.append(evaluation)
    return evaluations


def _format_metric(metric: str, value: Any) -> str:
    if metric in _BOOLEAN_METRICS:
        return "✓" if value else "✗"
    return f"{value * 100:.0f}%"


def _metric_css_class(metric: str, value: Any) -> str:
    if metric in _BOOLEAN_METRICS:
        return "pass" if value else "fail"
    if value >= 1.0:
        return "pass"
    if value <= 0.0:
        return "fail"
    return "partial"


def render_html(
    evaluations: list[dict[str, Any]],
    overall: dict[str, float],
    by_category: dict[str, dict[str, float]],
    results_path: Path,
) -> str:
    """Monta um relatório HTML autocontido (sem dependências externas)."""
    rows = []
    for evaluation in evaluations:
        cells = "".join(
            f'<td class="{_metric_css_class(metric, evaluation[metric])}">'
            f"{_format_metric(metric, evaluation[metric])}</td>"
            for metric in SUMMARY_METRICS
        )
        attempted = "✓" if evaluation["attempted"] else "✗ (sem resultado)"
        attempted_class = "pass" if evaluation["attempted"] else "fail"
        rows.append(
            "<tr>"
            f'<td>{html.escape(evaluation["id"])}</td>'
            f'<td>{html.escape(evaluation["user_question"])}</td>'
            f'<td>{html.escape(evaluation["category"])}</td>'
            f'<td>{html.escape(evaluation["difficulty"])}</td>'
            f'<td>{html.escape(", ".join(evaluation["expected_tools"]))}</td>'
            f'<td>{html.escape(", ".join(t for t in evaluation["tool_names"] if t))}</td>'
            f'<td class="{attempted_class}">{attempted}</td>'
            f"{cells}"
            "</tr>"
        )

    overall_cells = "".join(
        f"<td>{_format_metric(metric, overall[metric])}</td>" for metric in SUMMARY_METRICS
    )

    category_rows = []
    for category, metrics in sorted(by_category.items()):
        cells = "".join(
            f"<td>{_format_metric(metric, metrics[metric])}</td>" for metric in SUMMARY_METRICS
        )
        category_rows.append(f"<tr><td>{html.escape(category)}</td>{cells}</tr>")

    header_cells = "".join(f"<th>{label}</th>" for label in _METRIC_LABELS.values())

    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>mcp-data-br — relatório de evals</title>
<style>
  body {{ font-family: system-ui, sans-serif; margin: 2rem; color: #1a1a1a; }}
  h1 {{ margin-bottom: 0.25rem; }}
  .subtitle {{ color: #555; margin-top: 0; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1.5rem 0; font-size: 0.9rem; }}
  th, td {{ border: 1px solid #ddd; padding: 0.4rem 0.6rem; text-align: left; }}
  th {{ background: #f5f5f5; }}
  td.pass {{ background: #e6f4ea; color: #1e7d34; font-weight: 600; }}
  td.fail {{ background: #fbe9e7; color: #c0392b; font-weight: 600; }}
  td.partial {{ background: #fff8e1; color: #8a6d00; font-weight: 600; }}
  h2 {{ margin-top: 2rem; }}
</style>
</head>
<body>
<h1>mcp-data-br — relatório de evals</h1>
<p class="subtitle">Resultados de: <code>{html.escape(str(results_path))}</code> &middot;
{len(evaluations)} caso(s)</p>

<h2>Resumo geral</h2>
<table>
  <tr>{header_cells}</tr>
  <tr>{overall_cells}</tr>
</table>

<h2>Resumo por categoria</h2>
<table>
  <tr><th>Categoria</th>{header_cells}</tr>
  {"".join(category_rows)}
</table>

<h2>Casos</h2>
<table>
  <tr>
    <th>ID</th>
    <th>Pergunta</th>
    <th>Categoria</th>
    <th>Dificuldade</th>
    <th>Tools esperadas</th>
    <th>Tools chamadas</th>
    <th>Tentado</th>
    {header_cells}
  </tr>
  {"".join(rows)}
</table>
</body>
</html>
"""


def print_summary(overall: dict[str, float], by_category: dict[str, dict[str, float]]) -> None:
    print("Resumo geral:")
    for metric in SUMMARY_METRICS:
        print(f"  {_METRIC_LABELS[metric]:<20} {overall[metric] * 100:5.1f}%")

    print("\nPor categoria:")
    for category, metrics in sorted(by_category.items()):
        print(f"  {category}:")
        for metric in SUMMARY_METRICS:
            print(f"    {_METRIC_LABELS[metric]:<20} {metrics[metric] * 100:5.1f}%")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--results",
        type=Path,
        required=True,
        help="Caminho para o arquivo JSON de resultados produzido por um agente.",
    )
    parser.add_argument(
        "--datasets",
        type=Path,
        default=_DEFAULT_DATASETS_DIR,
        help=f"Diretório com os datasets JSON (padrão: {_DEFAULT_DATASETS_DIR}).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=_DEFAULT_OUTPUT,
        help=f"Caminho do relatório HTML a gerar (padrão: {_DEFAULT_OUTPUT}).",
    )
    args = parser.parse_args(argv)

    cases = load_dataset(args.datasets)
    results = load_results(args.results)

    evaluations = run_eval(cases, results)
    overall = aggregate(evaluations)

    categories = {evaluation["category"] for evaluation in evaluations}
    by_category = {
        category: aggregate([e for e in evaluations if e["category"] == category])
        for category in categories
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        render_html(evaluations, overall, by_category, args.results), encoding="utf-8"
    )

    print_summary(overall, by_category)
    print(f"\nRelatório HTML escrito em: {args.output}")

    unattempted = [e["id"] for e in evaluations if not e["attempted"]]
    if unattempted:
        print(f"\nCasos sem resultado no agente: {', '.join(unattempted)}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
