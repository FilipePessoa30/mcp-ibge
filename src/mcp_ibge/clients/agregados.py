"""Cliente para a API de Agregados (SIDRA) do IBGE.

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/agregados

Conceitos principais:
    - "Agregado": uma tabela/pesquisa estatística (ex.: Censo, PNAD, estimativas
      populacionais), identificada por um ID numérico.
    - "Variável": uma grandeza medida dentro de um agregado (ex.: população,
      PIB), identificada por um ID numérico.
    - "Período": ano ou trimestre de referência dos dados (ex.: "2021",
      "2021-2022", ou "-1" para o período mais recente disponível).
    - "Localidade": unidade territorial consultada, no formato
      ``N<nivel>[<ids>]``, ex.: ``N1[all]`` (Brasil), ``N3[all]`` (todos os
      estados), ``N6[3550308]`` (município de São Paulo).
"""

from __future__ import annotations

from typing import Any

from ..config import AGREGADOS_BASE_URL
from ..http_client import get_json
from .base import IBGEResult

# Alias amigável para o nível territorial "Brasil" (N1).
_LOCALIDADE_ALIASES = {
    "brasil": "N1[all]",
    "br": "N1[all]",
}


def _resolver_localidades(localidades: str) -> str:
    """Resolve aliases simples (ex.: "BR") para a sintaxe N<nivel>[<ids>] do SIDRA."""
    return _LOCALIDADE_ALIASES.get(localidades.strip().lower(), localidades)


async def listar_agregados(
    pesquisa: str | None = None,
    assunto: str | None = None,
    texto: str | None = None,
) -> IBGEResult:
    """Lista os agregados (tabelas) disponíveis no SIDRA.

    Args:
        pesquisa: Filtra pelo nome/sigla da pesquisa de origem (ex.: "Censo
            Demográfico"), conforme aceito pela API do IBGE.
        assunto: Filtra pelo nome do assunto (ex.: "População"), conforme
            aceito pela API do IBGE.
        texto: Filtro textual adicional aplicado localmente sobre o nome dos
            agregados retornados (case-insensitive, substring).
    """
    endpoint = AGREGADOS_BASE_URL
    query: dict[str, Any] = {}
    if pesquisa:
        query["pesquisa"] = pesquisa
    if assunto:
        query["assunto"] = assunto

    data = await get_json(endpoint, params=query or None)

    if texto:
        termo = texto.strip().lower()
        filtrado = []
        for grupo in data:
            agregados_filtrados = [
                agregado
                for agregado in grupo.get("agregados", [])
                if termo in agregado.get("nome", "").lower()
            ]
            if agregados_filtrados:
                filtrado.append({**grupo, "agregados": agregados_filtrados})
        data = filtrado

    request_params = dict(query)
    if texto:
        request_params["texto"] = texto

    return IBGEResult(data=data, endpoint=endpoint, params=request_params)


async def obter_metadados_agregado(agregado_id: int) -> IBGEResult:
    """Obtém os metadados completos de um agregado: variáveis, períodos e níveis territoriais.

    Args:
        agregado_id: ID numérico do agregado (ex.: 6579 = "População residente
            estimada").
    """
    endpoint = f"{AGREGADOS_BASE_URL}/{agregado_id}/metadados"
    data = await get_json(endpoint)
    return IBGEResult(data=data, endpoint=endpoint, params={"agregado_id": agregado_id})


async def consultar_dados_agregado(
    agregado_id: int,
    variaveis: str = "all",
    periodos: str = "-1",
    localidades: str = "N1[all]",
    classificacoes: str | None = None,
) -> IBGEResult:
    """Consulta valores de um agregado do SIDRA para variáveis/períodos/localidades.

    Args:
        agregado_id: ID numérico do agregado (use `obter_metadados_agregado`
            para descobrir IDs de variáveis e níveis territoriais válidos).
        variaveis: ID de uma variável, lista separada por vírgula, ou "all"
            para todas as variáveis do agregado.
        periodos: Período(s) no formato aceito pelo SIDRA: um ano ("2021"),
            um intervalo ("2010-2020"), uma lista ("2019,2021") ou um valor
            relativo ("-1" para o último período disponível, "-3" para os
            últimos 3).
        localidades: Unidade territorial no formato ``N<nivel>[<ids>]``, ex.:
            ``N1[all]`` (Brasil), ``N3[all]`` (todos os estados),
            ``N6[3550308]`` (município de São Paulo). Aceita o alias "BR"
            como atalho para ``N1[all]``.
        classificacoes: Filtro opcional de classificação/categoria no formato
            ``<id_classificacao>[<id_categoria>]``, conforme os metadados do
            agregado.
    """
    localidades_resolvidas = _resolver_localidades(localidades)
    endpoint = f"{AGREGADOS_BASE_URL}/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}"

    query: dict[str, Any] = {"localidades": localidades_resolvidas}
    if classificacoes:
        query["classificacao"] = classificacoes

    data = await get_json(endpoint, params=query)

    request_params = {
        "agregado_id": agregado_id,
        "variaveis": variaveis,
        "periodos": periodos,
        **query,
    }
    return IBGEResult(data=data, endpoint=endpoint, params=request_params)
