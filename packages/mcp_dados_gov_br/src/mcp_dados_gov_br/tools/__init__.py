"""Registro das *tools* MCP do mcp-dados-gov-br.

Cada arquivo deste pacote expõe uma função `register_<dominio>_tools(mcp:
FastMCP)` chamada por `mcp_dados_gov_br.server`, seguindo `mcp_ibge.tools`:

- `status_tools.register_status_tools` — tool `status` (exigida para todo
  módulo do mcp-data-br).
- `dataset_tools.register_dataset_tools` — `buscar_datasets`,
  `obter_dataset`, `listar_recursos_dataset`,
  `sugerir_datasets_para_pergunta`.
- `organizacao_tools.register_organizacao_tools` — `buscar_organizacoes`,
  `obter_organizacao`.
- `catalogo_tools.register_catalogo_tools` — `listar_grupos`, `buscar_tags`.

`run_typed_tool`, abaixo, converte o `TypedToolResult` retornado pela camada
de serviço (`services/catalog_service.py`) no envelope público
`{ok, data, metadata, warnings, errors}`.
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
            metadata=build_metadata(endpoint=""),
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
