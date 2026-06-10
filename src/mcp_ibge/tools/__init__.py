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

from ..schemas.common import TypedToolResult, build_error_response, build_response

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
    o resultado no envelope padrão de resposta.

    Em caso de sucesso (`ok=True`) retorna `{"metadata": ..., "data": ...}`,
    incluindo `"warnings"` quando houver. Em caso de falha (`ok=False` ou
    exceção inesperada) retorna `{"metadata": ..., "error": "..."}`.
    """
    try:
        result = await call
    except Exception as exc:  # pragma: no cover - rede de segurança
        logger.exception("Erro inesperado ao executar tool tipada")
        return build_error_response(
            source_url="", endpoint="", params={}, error=f"Erro inesperado: {exc}"
        )

    metadata = result.metadata

    if not result.ok:
        error = "; ".join(result.errors or result.warnings) or "Erro desconhecido"
        logger.warning("Erro ao consultar %s: %s", metadata.endpoint, error)
        return build_error_response(
            source_url=metadata.source_url,
            endpoint=metadata.endpoint,
            params=metadata.params,
            error=error,
        )

    response = build_response(
        source_url=metadata.source_url,
        endpoint=metadata.endpoint,
        params=metadata.params,
        data=_dump(result.data),
    )
    if result.warnings:
        response["warnings"] = result.warnings
    return response
