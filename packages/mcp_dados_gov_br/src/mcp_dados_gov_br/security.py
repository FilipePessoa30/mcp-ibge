"""Camada central de segurança do `mcp-dados-gov-br`.

Este módulo consolida, em um único lugar, as primitivas de segurança
reaproveitadas pelo client HTTP (`clients/base.py`) e pela camada de tools
(`tools/__init__.py`):

- `assert_allowed_url` / `is_allowed_url`: nenhuma requisição é feita para uma
  URL que não seja HTTPS para um domínio da allowlist `ALLOWED_HOSTS`
  (`config.ALLOWED_API_HOSTS`).
- `response_size_guard`: aborta o processamento de uma resposta cujo corpo
  excede `Settings.max_response_size_bytes`.
- `safe_error_response`: converte qualquer exceção em uma mensagem curta, sem
  stack trace, segura para devolver ao cliente MCP.

Ver [docs/security.md](../../../../docs/security.md) para o modelo de ameaças
geral do `mcp-data-br`.
"""

from __future__ import annotations

from urllib.parse import urlparse

from .config import ALLOWED_API_HOSTS, get_settings

__all__ = [
    "ALLOWED_HOSTS",
    "ResponseTooLargeError",
    "SecurityError",
    "URLNotAllowedError",
    "assert_allowed_url",
    "is_allowed_url",
    "response_size_guard",
    "safe_error_response",
]

# Domínios oficiais para os quais este servidor pode enviar requisições HTTP.
# Reexporta `config.ALLOWED_API_HOSTS` (única fonte de verdade) sob um nome
# mais descritivo para uso fora de `config`.
ALLOWED_HOSTS: frozenset[str] = ALLOWED_API_HOSTS


class SecurityError(Exception):
    """Erro base para violações da política de segurança do servidor."""


class URLNotAllowedError(SecurityError):
    """A URL de destino não usa HTTPS para um domínio em `ALLOWED_HOSTS`.

    Em operação normal isto nunca deve ocorrer: `Settings.api_base_url` já é
    validada na inicialização (`config.Settings._validar_api_base_url`) contra
    a mesma allowlist. `assert_allowed_url` é uma segunda verificação, em
    profundidade, imediatamente antes de cada requisição.
    """


class ResponseTooLargeError(SecurityError):
    """O corpo de uma resposta excedeu `Settings.max_response_size_bytes`."""


def is_allowed_url(url: str) -> bool:
    """Retorna `True` se `url` for HTTPS para um host em `ALLOWED_HOSTS`.

    Qualquer outro esquema (`http`, `file`, `ftp`, ...), host ausente, host
    fora da allowlist (incluindo subdomínios/domínios parecidos, ex.:
    `dados.gov.br.evil.com`) ou URL malformada retorna `False`.
    """
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme == "https" and parsed.hostname in ALLOWED_HOSTS


def assert_allowed_url(url: str) -> None:
    """Levanta `URLNotAllowedError` se `url` não for HTTPS para a allowlist.

    Chamado por `AsyncCkanClient.call_action` imediatamente antes de cada
    requisição, como segunda verificação (em profundidade) além da validação
    de `Settings.api_base_url` feita na inicialização do servidor.
    """
    if not is_allowed_url(url):
        hosts = ", ".join(sorted(ALLOWED_HOSTS))
        raise URLNotAllowedError(
            f'URL não permitida: "{url}". Apenas HTTPS para domínios oficiais '
            f"configurados ({hosts}) é permitido."
        )


def response_size_guard(current_size: int, *, max_size: int | None = None, url: str = "") -> None:
    """Levanta `ResponseTooLargeError` se `current_size` exceder o limite.

    `max_size`, se informado, sobrepõe `Settings.max_response_size_bytes`
    (usado por `AsyncCkanClient.call_action` enquanto consome a resposta em
    streaming, para abortar antes de acumular o corpo inteiro em memória).
    """
    limit = get_settings().max_response_size_bytes if max_size is None else max_size
    if current_size > limit:
        local = f" de {url}" if url else ""
        raise ResponseTooLargeError(f"Resposta{local} excede o limite de {limit} bytes.")


def safe_error_response(exc: Exception) -> str:
    """Converte `exc` em uma mensagem curta e segura para o cliente MCP.

    Usa apenas `str(exc)` (a mensagem da exceção) — nunca o traceback, nomes
    de arquivo/caminhos do sistema, ou `repr()` de objetos internos. Se a
    exceção não tiver mensagem, usa o nome da classe da exceção.
    """
    message = str(exc).strip()
    return message or type(exc).__name__
