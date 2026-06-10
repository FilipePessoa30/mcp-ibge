"""Cliente HTTP assíncrono compartilhado, com timeout e cache opcional.

Usado por todos os módulos em `mcp_ibge.clients`. Centraliza o tratamento de
erros de rede/HTTP, convertendo-os em `IBGERequestError`.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from .cache import TTLCache
from .config import (
    CACHE_ENABLED,
    CACHE_MAX_SIZE,
    CACHE_TTL_SECONDS,
    DEFAULT_TIMEOUT,
    USER_AGENT,
)
from .errors import IBGERequestError

logger = logging.getLogger(__name__)

_cache = TTLCache(ttl_seconds=CACHE_TTL_SECONDS, max_size=CACHE_MAX_SIZE)


def _cache_key(url: str, params: dict[str, Any] | None) -> tuple[str, tuple[Any, ...]]:
    normalized = tuple(sorted((params or {}).items()))
    return url, normalized


async def get_json(
    url: str,
    params: dict[str, Any] | None = None,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    use_cache: bool = True,
) -> Any:
    """Executa um GET e retorna o corpo JSON decodificado.

    Levanta `IBGERequestError` em caso de timeout, erro de conexão, status
    HTTP de erro ou corpo que não seja JSON válido.
    """
    key = _cache_key(url, params)
    if use_cache and CACHE_ENABLED:
        cached = _cache.get(key)
        if cached is not None:
            logger.debug("cache hit: %s params=%s", url, params)
            return cached

    logger.debug("GET %s params=%s", url, params)
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    try:
        async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
    except httpx.TimeoutException as exc:
        raise IBGERequestError(
            f"Tempo limite excedido ({timeout}s) ao consultar {url}", url=url
        ) from exc
    except httpx.HTTPStatusError as exc:
        raise IBGERequestError(
            f"IBGE retornou HTTP {exc.response.status_code} para {url}",
            url=url,
            status_code=exc.response.status_code,
        ) from exc
    except httpx.RequestError as exc:
        raise IBGERequestError(f"Falha de conexão ao consultar {url}: {exc}", url=url) from exc
    except ValueError as exc:
        raise IBGERequestError(f"Resposta inválida (JSON malformado) de {url}", url=url) from exc

    if use_cache and CACHE_ENABLED:
        _cache.set(key, data)
    return data


def clear_cache() -> None:
    """Limpa o cache em memória. Útil em testes e para depuração."""
    _cache.clear()
