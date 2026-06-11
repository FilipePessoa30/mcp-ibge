"""Modelos Pydantic para a API de Agregados (SIDRA) do IBGE.

Diferentes agregados (tabelas) do SIDRA têm estruturas de variáveis,
classificações e localidades muito variadas. Os modelos abaixo tipam apenas os
campos comuns e mais usados, preservando o JSON bruto da API em `raw` para o
restante.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict

# Valores usados pelo SIDRA para indicar dados ausentes, não disponíveis ou
# sigilosos em uma série: "-" (zero absoluto), ".." (não se aplica), "..."
# (dado não disponível) e "X" (valor sigiloso).
_VALORES_AUSENTES = {"-", "..", "...", "X", ""}


class AgregadoSummary(BaseModel):
    """Resumo de um agregado (tabela) do SIDRA, como listado em `/agregados`."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str


class AgregadoMetadata(BaseModel):
    """Metadados de um agregado: pesquisa, assunto, periodicidade etc.

    `raw` preserva o JSON completo de `/agregados/{id}/metadados`, incluindo
    `variaveis`, `classificacoes` e `nivelTerritorial`.
    """

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str
    pesquisa: str | None = None
    assunto: str | None = None
    periodicidade: str | None = None
    raw: dict[str, Any]


class AgregadoVariable(BaseModel):
    """Variável disponível em um agregado (ex.: "População residente estimada")."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str
    unidade: str | None = None
    raw: dict[str, Any]


class AgregadoPeriod(BaseModel):
    """Período disponível para consulta em um agregado (ex.: "2024")."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str | None = None


class AgregadoQueryResult(BaseModel):
    """Um valor individual do resultado de `consultar_agregado`.

    Cada item representa uma combinação (variável, localidade, período) — o
    resultado "achatado" da estrutura aninhada `variaveis -> resultados ->
    series -> serie` retornada pela API do SIDRA.
    """

    model_config = ConfigDict(extra="allow")

    agregado_id: str
    variavel_id: str | None = None
    localidade_id: str | None = None
    localidade_nome: str | None = None
    periodo: str | None = None
    valor: float | str | None = None
    unidade: str | None = None
    raw: dict[str, Any] | None = None


def _parse_valor(valor: Any) -> float | str | None:
    """Converte um valor de série do SIDRA, tratando marcadores de dado ausente.

    Strings numéricas (ex.: "12345678" ou "12.5") viram `float`. Marcadores
    como "-", "..", "..." e "X" (ver `_VALORES_AUSENTES`) viram `None`.
    Qualquer outro valor não numérico é preservado como string.
    """
    if valor is None:
        return None
    if isinstance(valor, int | float):
        return float(valor)

    texto = str(valor).strip()
    if texto in _VALORES_AUSENTES:
        return None
    try:
        return float(texto)
    except ValueError:
        return texto


def agregado_summary_from_raw(data: dict[str, Any]) -> AgregadoSummary:
    """Converte um item de `agregados[]` (de um grupo de `/agregados`) em `AgregadoSummary`."""
    return AgregadoSummary(id=str(data["id"]), nome=data["nome"])


def agregados_summary_from_lista(data: list[dict[str, Any]]) -> list[AgregadoSummary]:
    """Achata a resposta de `/agregados` (agrupada por pesquisa) em uma lista de agregados.

    A API retorna `[{"id": ..., "nome": <pesquisa>, "agregados": [...]}]`; esta
    função extrai apenas os itens de `agregados[]` de cada grupo.
    """
    resumo: list[AgregadoSummary] = []
    for grupo in data:
        for item in grupo.get("agregados", []):
            resumo.append(agregado_summary_from_raw(item))
    return resumo


def agregado_metadata_from_raw(data: dict[str, Any]) -> AgregadoMetadata:
    """Converte a resposta de `/agregados/{id}/metadados` em `AgregadoMetadata`."""
    periodicidade_raw = data.get("periodicidade")
    if isinstance(periodicidade_raw, dict):
        periodicidade = periodicidade_raw.get("frequencia")
    else:
        periodicidade = periodicidade_raw

    return AgregadoMetadata(
        id=str(data["id"]),
        nome=data["nome"],
        pesquisa=data.get("pesquisa"),
        assunto=data.get("assunto"),
        periodicidade=periodicidade,
        raw=data,
    )


def agregado_variable_from_raw(data: dict[str, Any]) -> AgregadoVariable:
    """Converte um item de `/agregados/{id}/variaveis` em `AgregadoVariable`."""
    return AgregadoVariable(
        id=str(data["id"]),
        nome=data["nome"],
        unidade=data.get("unidade"),
        raw=data,
    )


def agregado_period_from_raw(data: dict[str, Any]) -> AgregadoPeriod:
    """Converte um item de `/agregados/{id}/periodos` em `AgregadoPeriod`."""
    literals = data.get("literals") or []
    nome = literals[0] if literals else None
    return AgregadoPeriod(id=str(data["id"]), nome=nome)


def agregado_query_results_from_raw(
    agregado_id: str, data: list[dict[str, Any]]
) -> list[AgregadoQueryResult]:
    """Achata a resposta de `query_agregado` em uma lista de `AgregadoQueryResult`.

    A resposta do SIDRA é uma lista de variáveis, cada uma com `resultados`
    (agrupados por classificação/localidade) contendo `series`, cada uma com
    `localidade` e `serie` (um dict `{periodo: valor}`). Esta função produz um
    item por combinação (variável, localidade, período).
    """
    resultados: list[AgregadoQueryResult] = []
    for variavel in data:
        variavel_id = str(variavel["id"]) if variavel.get("id") is not None else None
        unidade = variavel.get("unidade")

        for resultado in variavel.get("resultados", []):
            for serie_entry in resultado.get("series", []):
                localidade = serie_entry.get("localidade") or {}
                for periodo, valor in (serie_entry.get("serie") or {}).items():
                    resultados.append(
                        AgregadoQueryResult(
                            agregado_id=agregado_id,
                            variavel_id=variavel_id,
                            localidade_id=localidade.get("id"),
                            localidade_nome=localidade.get("nome"),
                            periodo=periodo,
                            valor=_parse_valor(valor),
                            unidade=unidade,
                            raw=serie_entry,
                        )
                    )
    return resultados
