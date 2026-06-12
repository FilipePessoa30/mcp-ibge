"""Métricas usadas por `runner.py` para avaliar resultados de agentes.

Não depende de nenhum serviço externo (nem de modelo de linguagem): cada
métrica é uma comparação simples entre o `expected_*` de um caso do dataset e
o `tool_calls`/`final_answer` produzidos por um agente para esse caso (ver
`README.md` para o formato esperado do arquivo de resultados).
"""

from __future__ import annotations

from typing import Any

# Os 11 campos de `SourceMetadata` (ver `packages/mcp_ibge/src/mcp_ibge/schemas/common.py`).
METADATA_KEYS = {
    "source_name",
    "source_url",
    "official_source",
    "endpoint",
    "params",
    "retrieved_at",
    "period",
    "territorial_level",
    "license_note",
    "version",
    "cache_hit",
}

# Chaves do envelope padrão `{ok, data, metadata, warnings, errors}`.
ENVELOPE_KEYS = {"ok", "data", "metadata", "warnings", "errors"}


class _Missing:
    """Sentinela para "caminho não encontrado", distinto de um valor `None` real."""

    def __repr__(self) -> str:
        return "MISSING"


MISSING = _Missing()


def get_path(obj: Any, path: str) -> Any:
    """Resolve um caminho `"a.b.0.c"` em um dict/list aninhado.

    Segmentos puramente numéricos indexam listas (ex.: `"data.0.valor"`).
    Um caminho vazio (`""`) retorna o próprio `obj`. Retorna `MISSING` se
    qualquer segmento não existir ou o tipo não permitir o acesso.
    """
    if path == "":
        return obj

    current = obj
    for segment in path.split("."):
        if isinstance(current, dict):
            if segment not in current:
                return MISSING
            current = current[segment]
        elif isinstance(current, list):
            if not segment.lstrip("-").isdigit():
                return MISSING
            index = int(segment)
            if index < 0 or index >= len(current):
                return MISSING
            current = current[index]
        else:
            return MISSING
    return current


def check_field(envelope: Any, field_check: dict[str, Any]) -> bool:
    """Avalia uma única verificação de `expected_fields` contra um envelope de resposta.

    `field_check` tem um campo `"path"` e exatamente um dos seguintes:
    `"equals"`, `"contains"`, `"min_length"`, `"not_null"` ou `"in"`.
    """
    if envelope is MISSING:
        return False

    value = get_path(envelope, field_check["path"])

    if "equals" in field_check:
        return value is not MISSING and value == field_check["equals"]

    if "contains" in field_check:
        if value is MISSING:
            return False
        try:
            return field_check["contains"] in value
        except TypeError:
            return False

    if "min_length" in field_check:
        if value is MISSING:
            return False
        try:
            return len(value) >= field_check["min_length"]
        except TypeError:
            return False

    if "not_null" in field_check:
        is_present = value is not MISSING and value is not None
        return is_present == bool(field_check["not_null"])

    if "in" in field_check:
        return value is not MISSING and value in field_check["in"]

    return False


def is_valid_envelope(envelope: Any) -> bool:
    """Confere se `envelope` segue o contrato `{ok, data, metadata, warnings, errors}`.

    Verifica as chaves do envelope, os 11 campos de `metadata`, e que
    `warnings`/`errors` são listas de objetos `{"message": ..., "code": ...}`.
    """
    if not isinstance(envelope, dict):
        return False
    if set(envelope) != ENVELOPE_KEYS:
        return False
    if not isinstance(envelope["ok"], bool):
        return False

    metadata = envelope["metadata"]
    if not isinstance(metadata, dict) or set(metadata) != METADATA_KEYS:
        return False

    for key in ("warnings", "errors"):
        items = envelope[key]
        if not isinstance(items, list):
            return False
        for item in items:
            if not isinstance(item, dict) or set(item) != {"message", "code"}:
                return False

    return True


def find_primary_result(case: dict[str, Any], tool_calls: list[dict[str, Any]]) -> Any:
    """Retorna o `result` (envelope) da primeira chamada ao tool primário do caso.

    O tool primário é `expected_tools[0]`. Retorna `MISSING` se o caso não
    tiver `expected_tools` ou se essa tool não tiver sido chamada.
    """
    expected_tools = case.get("expected_tools") or []
    if not expected_tools:
        return MISSING

    primary_tool = expected_tools[0]
    for call in tool_calls:
        if call.get("name") == primary_tool:
            return call.get("result", MISSING)
    return MISSING


def tool_selection_accuracy(case: dict[str, Any], tool_names: list[str]) -> float:
    """Fração das `expected_tools` do caso que foram efetivamente chamadas."""
    expected_tools = case.get("expected_tools") or []
    if not expected_tools:
        return 1.0
    called = set(tool_names)
    matched = sum(1 for tool in expected_tools if tool in called)
    return matched / len(expected_tools)


def field_accuracy(case: dict[str, Any], primary_result: Any) -> float:
    """Fração das verificações de `expected_fields` que passaram."""
    checks = case.get("expected_fields") or []
    if not checks:
        return 1.0
    passed = sum(1 for check in checks if check_field(primary_result, check))
    return passed / len(checks)


def source_presence(primary_result: Any) -> bool:
    """`True` se `metadata.source_url`/`source_name` estão presentes e citam o IBGE."""
    if primary_result is MISSING or not isinstance(primary_result, dict):
        return False
    metadata = primary_result.get("metadata")
    if not isinstance(metadata, dict):
        return False
    source_url = metadata.get("source_url")
    source_name = metadata.get("source_name")
    return bool(source_url) and isinstance(source_name, str) and "IBGE" in source_name


def warning_correctness(case: dict[str, Any], primary_result: Any) -> bool:
    """`True` se a presença de `warnings` corresponde ao `should_warn` do caso."""
    if primary_result is MISSING or not isinstance(primary_result, dict):
        return False
    has_warnings = bool(primary_result.get("warnings"))
    return has_warnings == bool(case.get("should_warn", False))


def structured_output_validity(primary_result: Any) -> bool:
    """`True` se o envelope retornado pela tool primária segue o contrato padrão."""
    return is_valid_envelope(primary_result)


def answer_contains_accuracy(case: dict[str, Any], final_answer: str) -> float:
    """Fração das strings de `expected_answer_contains` presentes em `final_answer`.

    Comparação *case-insensitive*. Retorna `1.0` se o caso não definir
    `expected_answer_contains`.
    """
    expected = case.get("expected_answer_contains") or []
    if not expected:
        return 1.0
    haystack = (final_answer or "").lower()
    matched = sum(1 for needle in expected if needle.lower() in haystack)
    return matched / len(expected)


def evaluate_case(case: dict[str, Any], agent_result: dict[str, Any] | None) -> dict[str, Any]:
    """Avalia um caso do dataset contra o resultado de um agente.

    `agent_result` é o item de `results.json` com o mesmo `id` do caso (ou
    `None` se o agente não produziu nenhum resultado para ele). Retorna um
    dict com cada métrica e alguns detalhes úteis para o relatório.
    """
    tool_calls = (agent_result or {}).get("tool_calls", [])
    tool_names = [call.get("name") for call in tool_calls]
    final_answer = (agent_result or {}).get("final_answer", "")

    primary_result = find_primary_result(case, tool_calls)

    return {
        "id": case["id"],
        "attempted": agent_result is not None,
        "tool_names": tool_names,
        "tool_selection_accuracy": tool_selection_accuracy(case, tool_names),
        "field_accuracy": field_accuracy(case, primary_result),
        "source_presence": source_presence(primary_result),
        "warning_correctness": warning_correctness(case, primary_result),
        "structured_output_validity": structured_output_validity(primary_result),
        "answer_contains_accuracy": answer_contains_accuracy(case, final_answer),
        "primary_result_found": primary_result is not MISSING,
    }


# Métricas booleanas/numéricas agregadas no relatório (ver `runner.py`).
SUMMARY_METRICS = (
    "tool_selection_accuracy",
    "field_accuracy",
    "source_presence",
    "warning_correctness",
    "structured_output_validity",
    "answer_contains_accuracy",
)


def aggregate(evaluations: list[dict[str, Any]]) -> dict[str, float]:
    """Calcula a média de cada métrica de `SUMMARY_METRICS` sobre todos os casos.

    Métricas booleanas (`source_presence`, `warning_correctness`,
    `structured_output_validity`) são tratadas como `1.0`/`0.0`. Casos não
    tentados (`attempted=False`) contam como `0.0` em todas as métricas, para
    penalizar lacunas de cobertura.
    """
    if not evaluations:
        return {metric: 0.0 for metric in SUMMARY_METRICS}

    totals = {metric: 0.0 for metric in SUMMARY_METRICS}
    for evaluation in evaluations:
        for metric in SUMMARY_METRICS:
            value = evaluation[metric]
            totals[metric] += float(value)

    return {metric: totals[metric] / len(evaluations) for metric in SUMMARY_METRICS}
