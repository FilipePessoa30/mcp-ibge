"""Cliente HTTP assíncrono base, compartilhado por todos os clientes IBGE.

Centraliza timeout, headers, cache opcional e tradução de erros de
rede/HTTP para `IBGERequestError`.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import get_settings
from ..utils.cache import get_cache
from ..utils.errors import IBGERequestError

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class IBGEResult:
    """Resultado de uma chamada a uma API do IBGE, com dados para rastreabilidade.

    Attributes:
        data: Corpo da resposta já decodificado (lista ou dicionário JSON).
        endpoint: URL completa do endpoint consultado (sem query string).
        params: Parâmetros relevantes da consulta, usados nos metadados de
            rastreabilidade da resposta da tool.
    """

    data: Any
    endpoint: str
    params: dict[str, Any] = field(default_factory=dict)


def _cache_key(url: str, params: dict[str, Any] | None) -> tuple[str, tuple[Any, ...]]:
    normalized = tuple(sorted((params or {}).items()))
    return url, normalized


class BaseIBGEClient:
    """Cliente HTTP assíncrono com timeout e cache, parametrizado por uma URL base."""

    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    async def get_json(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        use_cache: bool = True,
    ) -> Any:
        """Executa um GET em `base_url + path` e retorna o corpo JSON decodificado.

        Levanta `IBGERequestError` em caso de timeout, erro de conexão, status
        HTTP de erro ou corpo que não seja JSON válido.
        """
        settings = get_settings()
        url = f"{self.base_url}{path}"

        cache = get_cache() if use_cache else None
        key = _cache_key(url, params)
        if cache is not None:
            cached = cache.get(key)
            if cached is not None:
                logger.debug("cache hit: %s params=%s", url, params)
                return cached

        logger.debug("GET %s params=%s", url, params)
        headers = {"User-Agent": settings.user_agent, "Accept": "application/json"}

        try:
            async with httpx.AsyncClient(timeout=settings.timeout, headers=headers) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
        except httpx.TimeoutException as exc:
            raise IBGERequestError(
                f"Tempo limite excedido ({settings.timeout}s) ao consultar {url}", url=url
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
            raise IBGERequestError(
                f"Resposta inválida (JSON malformado) de {url}", url=url
            ) from exc

        if cache is not None:
            cache.set(key, data)
        return data
