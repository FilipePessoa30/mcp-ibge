"""Tools FastMCP: convertem chamadas de serviço no envelope padrão de resposta.

Cada submódulo (`localidades_tools`, `agregados_tools`, ...) expõe uma função
`register(mcp)` que registra suas tools na instância `FastMCP` do servidor.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable
from typing import Any

from ..clients.base import IBGEResult
from ..schemas.common import build_error_response, build_response
from ..utils.errors import IBGERequestError

logger = logging.getLogger(__name__)


async def run_tool(
    call: Awaitable[IBGEResult],
    *,
    endpoint: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Executa uma chamada de serviço e converte o resultado no envelope padrão.

    Em caso de sucesso retorna `{"metadata": {...}, "data": ...}`; em caso de
    erro (de rede/HTTP ou inesperado) retorna `{"metadata": {...}, "error": "..."}`.
    """
    try:
        result = await call
    except IBGERequestError as exc:
        logger.warning("Erro ao consultar %s: %s", exc.url, exc)
        return build_error_response(
            source_url=exc.url, endpoint=exc.url, params=params, error=str(exc)
        )
    except Exception as exc:  # pragma: no cover - rede de segurança
        logger.exception("Erro inesperado ao consultar %s", endpoint)
        return build_error_response(
            source_url=endpoint,
            endpoint=endpoint,
            params=params,
            error=f"Erro inesperado: {exc}",
        )

    return build_response(
        source_url=result.endpoint,
        endpoint=result.endpoint,
        params=result.params,
        data=result.data,
    )
