"""Exceções específicas dos clientes das APIs do IBGE."""

from __future__ import annotations


class IBGERequestError(Exception):
    """Erro ao consultar uma API do IBGE (rede, timeout, HTTP ou JSON inválido)."""

    def __init__(self, message: str, *, url: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = status_code
