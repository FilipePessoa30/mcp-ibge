"""Validadores de formato para parâmetros de entrada das tools/clients/services.

Centraliza a validação de UF, código de município, ID de agregado, variáveis,
períodos, níveis territoriais e limites de paginação usados pelas APIs de
Localidades e Agregados/SIDRA do IBGE. Cada validador recebe o valor bruto
informado pelo usuário/agente e, se o formato for inválido, levanta a exceção
customizada `IBGEValidationError` (HTTP 422) **antes** de qualquer requisição
de rede — falhando rápido, com mensagens claras e sem expor detalhes internos.

O parâmetro opcional `url`, quando informado, é usado apenas para preencher
`IBGEClientError.url` (rastreabilidade do erro); a validação não depende de
rede nem de configuração.
"""

from __future__ import annotations

import re

from .errors import IBGEValidationError

# Sigla <-> código numérico IBGE das 26 unidades federativas + Distrito Federal.
UF_SIGLA_POR_CODIGO: dict[str, str] = {
    "11": "RO",
    "12": "AC",
    "13": "AM",
    "14": "RR",
    "15": "PA",
    "16": "AP",
    "17": "TO",
    "21": "MA",
    "22": "PI",
    "23": "CE",
    "24": "RN",
    "25": "PB",
    "26": "PE",
    "27": "AL",
    "28": "SE",
    "29": "BA",
    "31": "MG",
    "32": "ES",
    "33": "RJ",
    "35": "SP",
    "41": "PR",
    "42": "SC",
    "43": "RS",
    "50": "MS",
    "51": "MT",
    "52": "GO",
    "53": "DF",
}
UF_CODIGO_POR_SIGLA: dict[str, str] = {
    sigla: codigo for codigo, sigla in UF_SIGLA_POR_CODIGO.items()
}

# Código IBGE de município: sempre 7 dígitos (ex.: 3550308 = São Paulo/SP).
_MUNICIPIO_CODE = re.compile(r"^\d{7}$")

# ID de agregado SIDRA: número inteiro positivo (ex.: "6579").
_AGREGADO_ID = re.compile(r"^\d+$")

# Variável(is) SIDRA: "all" ou um ou mais IDs numéricos separados por "|"
# (ex.: "93", "93|1000093").
_VARIAVEL_TOKEN = re.compile(r"^(all|\d+(\|\d+)*)$")

# Período SIDRA: relativo ("-1", "-6"), ano ou ano/mês ("2021", "202101"),
# intervalo ("2010-2020") ou "all". Múltiplos períodos podem ser separados
# por "," ou "|" (ex.: "2010,2015-2020,-1", "2020|2021|2022").
_PERIODO_TOKEN = re.compile(r"^(-\d{1,3}|\d{4,6}(-\d{4,6})?|all)$")
_PERIODO_SEPARADOR = re.compile(r"[,|]")

# Nível territorial SIDRA: "N" + 1-3 dígitos (ex.: "N1", "N6", "N105"),
# opcionalmente com a composição "[<ids>]" (ex.: "N3[33]", "N3[33,35]",
# "N6[all]"). Múltiplos níveis são separados por "|".
_NIVEL_TOKEN = re.compile(r"^N\d{1,3}(\[(all|\d+(,\d+)*)\])?$")

# Limites de paginação aceitos por `validate_limit`.
_LIMITE_MINIMO = 1
_LIMITE_MAXIMO = 100


def validate_uf(uf_or_id: str, *, url: str = "") -> str:
    """Valida uma UF, aceitando sigla (ex.: "RJ") ou código IBGE (ex.: "33").

    Retorna o valor normalizado (maiúsculas, sem espaços nas pontas) — o
    formato original (sigla ou código) é preservado. Levanta
    `IBGEValidationError` se o valor não corresponder a uma UF válida.
    """
    valor = str(uf_or_id).strip().upper()
    if valor in UF_CODIGO_POR_SIGLA or valor in UF_SIGLA_POR_CODIGO:
        return valor

    raise IBGEValidationError(
        f'UF inválida: "{uf_or_id}". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").',
        url=url,
        status_code=422,
    )


def validate_municipality_code(codigo: int | str, *, url: str = "") -> int:
    """Valida um código IBGE de município (7 dígitos, ex.: 3550308).

    Retorna o código como `int`. Levanta `IBGEValidationError` se o valor
    não for um inteiro de exatamente 7 dígitos.
    """
    texto = str(codigo).strip()
    if not _MUNICIPIO_CODE.match(texto):
        raise IBGEValidationError(
            f'Código de município inválido: "{codigo}". '
            "Deve ser o código IBGE de 7 dígitos (ex.: 3550308).",
            url=url,
            status_code=422,
        )
    return int(texto)


def validate_agregado_id(agregado_id: str, *, url: str = "") -> str:
    """Valida um ID de agregado SIDRA (número inteiro positivo, ex.: "6579").

    Retorna o valor normalizado (sem espaços nas pontas). Levanta
    `IBGEValidationError` se vazio, negativo ou se contiver caracteres não
    numéricos.
    """
    texto = str(agregado_id).strip()
    if not _AGREGADO_ID.match(texto):
        raise IBGEValidationError(
            f'ID de agregado inválido: "{agregado_id}". '
            'Deve ser um número inteiro positivo (ex.: "6579").',
            url=url,
            status_code=422,
        )
    return texto


def validate_variaveis(variaveis: str, *, url: str = "") -> str:
    """Valida a expressão de variáveis da API de Agregados (SIDRA).

    Aceita "all" ou um ou mais IDs numéricos separados por "|" (ex.: "93",
    "93|1000093"). Levanta `IBGEValidationError` se vazio ou se algum dos
    valores não corresponder a esse formato.
    """
    texto = str(variaveis).strip()
    if not texto or not _VARIAVEL_TOKEN.match(texto):
        raise IBGEValidationError(
            f'Variável(is) inválida(s): "{variaveis}". Use "all", um ID numérico '
            '(ex.: "93") ou uma lista separada por "|" (ex.: "93|1000093").',
            url=url,
            status_code=422,
        )
    return texto


def validate_periodos(periodos: str, *, url: str = "") -> str:
    """Valida a expressão de períodos da API de Agregados (SIDRA).

    Aceita "all", um período relativo ("-1", "-6"), um ano ou ano/mês
    ("2021", "202101"), um intervalo ("2010-2020"), ou uma lista desses
    valores separados por "," ou "|" (ex.: "2010,2015-2020,-1",
    "2020|2021|2022"). Levanta `IBGEValidationError` se vazio ou se algum dos
    valores não corresponder a esse formato.
    """
    texto = str(periodos).strip()
    if not texto:
        raise IBGEValidationError(
            'Parâmetro "periodos" não pode ser vazio.', url=url, status_code=422
        )

    tokens = [token.strip() for token in _PERIODO_SEPARADOR.split(texto)]
    if not all(_PERIODO_TOKEN.match(token) for token in tokens):
        raise IBGEValidationError(
            f'Períodos inválidos: "{periodos}". Use "all", um ano (ex.: "2021"), '
            'um período relativo (ex.: "-6"), um intervalo (ex.: "2010-2020") '
            'ou uma lista separada por "," ou "|" desses valores.',
            url=url,
            status_code=422,
        )
    return texto


def validate_niveis(niveis: str, *, url: str = "") -> str:
    """Valida a expressão de níveis territoriais da API de Agregados (SIDRA).

    Aceita um nível no formato "N<número>" (ex.: "N6"), opcionalmente com a
    composição "[<ids>]" (ex.: "N3[33]", "N3[33,35]", "N6[all]"), ou múltiplos
    níveis separados por "|" (ex.: "N1|N3", "N3[33]|N6[3550308]"). Levanta
    `IBGEValidationError` se vazio ou se algum dos níveis não corresponder a
    esse formato.
    """
    texto = str(niveis).strip()
    if not texto:
        raise IBGEValidationError(
            'Parâmetro "niveis" não pode ser vazio.', url=url, status_code=422
        )

    tokens = [token.strip() for token in texto.split("|")]
    if not all(_NIVEL_TOKEN.match(token) for token in tokens):
        raise IBGEValidationError(
            f'Níveis territoriais inválidos: "{niveis}". Use o formato "N<número>" '
            '(ex.: "N6"), opcionalmente com uma composição "[<ids>]" (ex.: '
            '"N3[33]"), com múltiplos níveis separados por "|" (ex.: "N1|N3").',
            url=url,
            status_code=422,
        )
    return texto


def validate_limit(limit: int, *, url: str = "") -> int:
    """Valida um limite de itens retornados (ex.: número de candidatos na busca).

    Exige um `int` entre `_LIMITE_MINIMO` (1) e `_LIMITE_MAXIMO` (100),
    inclusive. Levanta `IBGEValidationError` se o valor não for um inteiro ou
    estiver fora desse intervalo.
    """
    if not isinstance(limit, int) or isinstance(limit, bool):
        raise IBGEValidationError(
            f'Limite inválido: "{limit}". Deve ser um número inteiro entre '
            f"{_LIMITE_MINIMO} e {_LIMITE_MAXIMO}.",
            url=url,
            status_code=422,
        )

    if not (_LIMITE_MINIMO <= limit <= _LIMITE_MAXIMO):
        raise IBGEValidationError(
            f"Limite inválido: {limit}. Deve estar entre {_LIMITE_MINIMO} e {_LIMITE_MAXIMO}.",
            url=url,
            status_code=422,
        )
    return limit
