"""Cliente HTTP assíncrono base para a API CKAN do dados.gov.br.

Centraliza timeout, headers (incluindo o token de consumidor opcional), cache
TTL e tradução de erros de rede/HTTP/CKAN para as exceções de
`mcp_dados_gov_br.utils.errors`.

A API CKAN responde a `GET <api_base_url>/<action>?<params>` sempre com HTTP
200 e um corpo `{"success": bool, "result": ..., "error": {...}}` — mesmo em
caso de erro lógico (dataset não encontrado, parâmetros inválidos, ação que
exige autenticação, ...). `call_action` trata tanto erros HTTP quanto
`success: false` no corpo da resposta.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from typing import Any

import httpx

from ..config import get_settings
from ..security import (
    ResponseTooLargeError,
    URLNotAllowedError,
    assert_allowed_url,
    response_size_guard,
)
from ..utils.cache import get_cache
from ..utils.errors import (
    CkanAuthRequiredError,
    CkanClientError,
    CkanNotFoundError,
    CkanRateLimitError,
    CkanServerError,
    CkanValidationError,
)

logger = logging.getLogger(__name__)

# `__type` retornados pela API CKAN no corpo `error` de respostas com
# `"success": false`, mapeados para as exceções de `utils.errors`.
_NOT_FOUND_TYPES = {"Not Found Error"}
_VALIDATION_TYPES = {"Validation Error", "Search Query Error"}
_AUTH_TYPES = {"Authorization Error"}


@dataclass(frozen=True, slots=True)
class CkanResult:
    """Resultado de uma chamada a uma ação CKAN, com dados para rastreabilidade.

    Attributes:
        data: Valor de `result` na resposta CKAN (lista ou dicionário JSON).
        endpoint: URL completa da ação consultada (sem query string).
        params: Parâmetros enviados na consulta, usados nos metadados de
            rastreabilidade da resposta da tool.
        raw: Corpo bruto da resposta CKAN (`{"success", "result", ...}`).
            `None` quando o valor veio do cache.
        cache_hit: `True` se `data` veio do cache em memória, sem fazer uma
            nova requisição HTTP.
    """

    data: Any
    endpoint: str
    params: dict[str, Any] = field(default_factory=dict)
    raw: Any = None
    cache_hit: bool = False


def _cache_key(url: str, params: dict[str, Any] | None) -> tuple[str, tuple[Any, ...]]:
    normalized = tuple(sorted((params or {}).items()))
    return url, normalized


def _token_value(settings: Any) -> str | None:
    if settings.api_token is None:
        return None
    valor = settings.api_token.get_secret_value().strip()
    return valor or None


def _error_for_status(
    exc: httpx.HTTPStatusError, url: str, *, token_configured: bool
) -> CkanClientError:
    status = exc.response.status_code
    message = f"dados.gov.br retornou HTTP {status} para {url}"

    if status == 404:
        return CkanNotFoundError(message, url=url, status_code=status)
    if status in (400, 409, 422):
        return CkanValidationError(message, url=url, status_code=status)
    if status in (401, 403):
        return CkanAuthRequiredError(
            f"{message} {_auth_hint(token_configured)}", url=url, status_code=status
        )
    if status == 429:
        return CkanRateLimitError(message, url=url, status_code=status)
    if status >= 500:
        return CkanServerError(message, url=url, status_code=status)
    return CkanClientError(message, url=url, status_code=status)


def _auth_hint(token_configured: bool) -> str:
    if token_configured:
        return (
            "O token configurado em DADOS_GOV_BR_API_TOKEN pode estar inválido "
            "ou sem permissão para este recurso."
        )
    return (
        "Configure a variável de ambiente DADOS_GOV_BR_API_TOKEN com um token "
        "de consumidor válido do dados.gov.br para acessar este recurso."
    )


def _error_for_body(
    payload: dict[str, Any], url: str, *, token_configured: bool
) -> CkanClientError:
    error = payload.get("error") or {}
    tipo = error.get("__type", "")
    detalhe = error.get("message") or (json.dumps(error, ensure_ascii=False) if error else "")
    message = f"dados.gov.br retornou um erro para {url}"
    if detalhe:
        message += f": {detalhe}"

    if tipo in _NOT_FOUND_TYPES:
        return CkanNotFoundError(message, url=url, status_code=404)
    if tipo in _VALIDATION_TYPES:
        return CkanValidationError(message, url=url, status_code=422)
    if tipo in _AUTH_TYPES:
        return CkanAuthRequiredError(
            f"{message} {_auth_hint(token_configured)}", url=url, status_code=403
        )
    return CkanServerError(message, url=url)


class AsyncCkanClient:
    """Cliente HTTP assíncrono para ações da API CKAN (`<api_base_url>/<action>`)."""

    def __init__(self) -> None:
        settings = get_settings()
        self.base_url = settings.api_base_url.rstrip("/")

    async def call_action(
        self,
        action: str,
        params: dict[str, Any] | None = None,
        *,
        use_cache: bool = True,
    ) -> CkanResult:
        """Executa `GET <base_url>/<action>` e retorna o campo `result` da resposta CKAN.

        Levanta uma subclasse de `CkanClientError` em caso de timeout, erro de
        conexão, status HTTP de erro, corpo que não seja JSON válido, ou
        resposta CKAN com `"success": false`.
        """
        settings = get_settings()
        url = f"{self.base_url}/{action}"

        cache = get_cache() if use_cache else None
        key = _cache_key(url, params)
        if cache is not None:
            cached = cache.get(key)
            if cached is not None:
                logger.debug("cache hit: %s params=%s", url, params)
                return CkanResult(data=cached, endpoint=url, params=params or {}, cache_hit=True)

        logger.debug("GET %s params=%s", url, params)
        token = _token_value(settings)
        headers = {"Accept": "application/json"}
        if token:
            headers["Authorization"] = token

        max_size = settings.max_response_size_bytes
        try:
            assert_allowed_url(url)
            async with httpx.AsyncClient(timeout=settings.timeout, headers=headers) as client:
                async with client.stream("GET", url, params=params) as response:
                    response.raise_for_status()
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        response_size_guard(len(body), max_size=max_size, url=url)
                payload = json.loads(body)
        except URLNotAllowedError as exc:
            raise CkanClientError(str(exc), url=url) from exc
        except ResponseTooLargeError as exc:
            raise CkanServerError(str(exc), url=url) from exc
        except httpx.TimeoutException as exc:
            raise CkanClientError(
                f"Tempo limite excedido ({settings.timeout}s) ao consultar {url}", url=url
            ) from exc
        except httpx.HTTPStatusError as exc:
            raise _error_for_status(exc, url, token_configured=token is not None) from exc
        except httpx.RequestError as exc:
            raise CkanClientError(f"Falha de conexão ao consultar {url}: {exc}", url=url) from exc
        except ValueError as exc:
            raise CkanServerError(f"Resposta inválida (JSON malformado) de {url}", url=url) from exc

        if not isinstance(payload, dict) or not payload.get("success", False):
            error_body = payload if isinstance(payload, dict) else {}
            raise _error_for_body(error_body, url, token_configured=token is not None)

        data = payload.get("result")
        if cache is not None:
            cache.set(key, data)
        return CkanResult(
            data=data, endpoint=url, params=params or {}, raw=payload, cache_hit=False
        )
