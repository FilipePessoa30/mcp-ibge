"""Exceções específicas dos clientes das APIs do IBGE."""

from __future__ import annotations


class IBGEClientError(Exception):
    """Erro base ao consultar uma API do IBGE."""

    def __init__(self, message: str, *, url: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class IBGENotFoundError(IBGEClientError):
    """O recurso solicitado não foi encontrado (HTTP 404)."""


class IBGEValidationError(IBGEClientError):
    """A API rejeitou os parâmetros da requisição (HTTP 400/422)."""


class IBGERateLimitError(IBGEClientError):
    """O limite de requisições à API foi excedido (HTTP 429)."""


class IBGEServerError(IBGEClientError):
    """A API do IBGE falhou internamente (HTTP 5xx) ou retornou dados inválidos."""
