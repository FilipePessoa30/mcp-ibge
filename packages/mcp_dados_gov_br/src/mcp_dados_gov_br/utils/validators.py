"""Validadores de entrada para as tools/clients/services deste módulo.

Cada validador recebe o valor bruto informado pelo usuário/agente e, se o
formato for inválido, levanta `CkanValidationError` (HTTP 422) **antes** de
qualquer requisição de rede — falhando rápido, com mensagens claras e sem
expor detalhes internos.

O parâmetro opcional `url`, quando informado, é usado apenas para preencher
`CkanClientError.url` (rastreabilidade do erro); a validação não depende de
rede nem de configuração.
"""

from __future__ import annotations

from .errors import CkanValidationError

# Limites de paginação aceitos por `validate_limit`.
_LIMITE_MINIMO = 1
_LIMITE_MAXIMO = 100


def validate_limit(limit: int, *, url: str = "") -> int:
    """Valida um limite de itens retornados por uma busca/listagem.

    Exige um `int` entre `_LIMITE_MINIMO` (1) e `_LIMITE_MAXIMO` (100),
    inclusive. Levanta `CkanValidationError` se o valor não for um inteiro ou
    estiver fora desse intervalo.
    """
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise CkanValidationError(
            f'Limite inválido: "{limit}". Deve ser um número inteiro entre '
            f"{_LIMITE_MINIMO} e {_LIMITE_MAXIMO}.",
            url=url,
            status_code=422,
        )

    if not (_LIMITE_MINIMO <= limit <= _LIMITE_MAXIMO):
        raise CkanValidationError(
            f"Limite inválido: {limit}. Deve estar entre {_LIMITE_MINIMO} e {_LIMITE_MAXIMO}.",
            url=url,
            status_code=422,
        )
    return limit


def validate_non_empty(value: str, *, field_name: str, url: str = "") -> str:
    """Valida que `value` é uma string não vazia (após remover espaços nas pontas).

    Retorna o valor normalizado (sem espaços nas pontas). Levanta
    `CkanValidationError` se `value` for vazio ou contiver apenas espaços.
    """
    texto = str(value).strip()
    if not texto:
        raise CkanValidationError(
            f'Parâmetro "{field_name}" não pode ser vazio.', url=url, status_code=422
        )
    return texto
