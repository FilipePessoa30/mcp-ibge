"""Exceções específicas do cliente da API CKAN do dados.gov.br."""

from __future__ import annotations


class CkanClientError(Exception):
    """Erro base ao consultar a API CKAN do dados.gov.br."""

    def __init__(self, message: str, *, url: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.url = url
        self.status_code = status_code


class CkanNotFoundError(CkanClientError):
    """Dataset, organização, grupo ou recurso não encontrado.

    Corresponde a um HTTP 404 ou a um corpo CKAN `{"success": false, "error":
    {"__type": "Not Found Error", ...}}`.
    """


class CkanValidationError(CkanClientError):
    """A API rejeitou os parâmetros da requisição.

    Corresponde a um HTTP 400/409/422 ou a um corpo CKAN com `__type`
    `"Validation Error"`/`"Search Query Error"`.
    """


class CkanRateLimitError(CkanClientError):
    """O limite de requisições à API foi excedido (HTTP 429)."""


class CkanServerError(CkanClientError):
    """A API do dados.gov.br falhou internamente (HTTP 5xx) ou retornou dados inválidos."""


class CkanAuthRequiredError(CkanClientError):
    """A API exige autenticação (token de consumidor) para este recurso.

    Corresponde a um HTTP 401/403 ou a um corpo CKAN com `__type`
    `"Authorization Error"`. A mensagem orienta a configurar
    `DADOS_GOV_BR_API_TOKEN` (se ausente) ou revisar o token configurado (se
    presente mas inválido/sem permissão).
    """
