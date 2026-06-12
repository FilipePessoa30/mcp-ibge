"""Tools FastMCP: convertem chamadas de serviço no envelope padrão de resposta.

Cada submódulo (`localidades_tools`, `agregados_tools`, ...) expõe uma função
de registro (ex.: `register_localidades_tools(mcp)`, `register_agregados_tools(mcp)`)
que registra suas tools na instância `FastMCP` do servidor.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable
from typing import Any

from pydantic import BaseModel

from ..schemas.common import TypedToolResult, build_metadata, build_tool_response
from ..security import safe_error_response

logger = logging.getLogger(__name__)


def _dump(value: Any) -> Any:
    """Converte (recursivamente) modelos Pydantic em estruturas JSON simples."""
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, list):
        return [_dump(item) for item in value]
    return value


async def run_typed_tool(call: Awaitable[TypedToolResult[Any]]) -> dict[str, Any]:
    """Executa uma chamada de serviço que retorna `TypedToolResult` e converte
    o resultado no envelope padrão `{ok, data, metadata, warnings, errors}`.

    Em caso de exceção inesperada (rede de segurança), monta uma resposta
    `ok=False` com uma mensagem de erro genérica, sem expor stack trace.
    Quando `ok=False` e o serviço não informou `errors`, os `warnings`
    (preservados em `warnings`) também são usados para preencher `errors`,
    garantindo que toda resposta de falha explique o motivo.
    """
    try:
        result = await call
    except Exception as exc:  # pragma: no cover - rede de segurança
        logger.exception("Erro inesperado ao executar tool tipada")
        return build_tool_response(
            ok=False,
            data=None,
            metadata=build_metadata(source_url="", endpoint=""),
            errors=[f"Erro inesperado: {safe_error_response(exc)}"],
        )

    metadata = result.metadata
    errors = list(result.errors)

    if not result.ok:
        logger.warning(
            "Erro ao consultar %s: %s",
            metadata.endpoint,
            "; ".join(errors or result.warnings) or "Erro desconhecido",
        )
        if not errors:
            errors = list(result.warnings) or ["Erro desconhecido"]

    return build_tool_response(
        ok=result.ok,
        data=_dump(result.data),
        metadata=metadata,
        warnings=result.warnings,
        errors=errors,
    )
