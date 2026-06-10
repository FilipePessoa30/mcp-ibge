"""Cliente para a API de Localidades do IBGE.

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/localidades
"""

from __future__ import annotations

import unicodedata
from typing import Any

from ..config import LOCALIDADES_BASE_URL
from ..http_client import get_json
from .base import IBGEResult


def _normalizar(texto: str) -> str:
    """Remove acentos e normaliza para minúsculas, para busca textual simples."""
    sem_acento = unicodedata.normalize("NFKD", texto)
    sem_acento = "".join(c for c in sem_acento if not unicodedata.combining(c))
    return sem_acento.lower().strip()


async def listar_regioes() -> IBGEResult:
    """Lista as 5 grandes regiões geográficas do Brasil."""
    endpoint = f"{LOCALIDADES_BASE_URL}/regioes"
    data = await get_json(endpoint)
    return IBGEResult(data=data, endpoint=endpoint, params={})


async def listar_estados(regiao: str | None = None) -> IBGEResult:
    """Lista os 26 estados e o Distrito Federal.

    Args:
        regiao: Filtro opcional pela sigla (N, NE, CO, SE, S) ou ID numérico
            da grande região. A filtragem é feita localmente sobre a lista
            completa retornada pelo IBGE.
    """
    endpoint = f"{LOCALIDADES_BASE_URL}/estados"
    data = await get_json(endpoint)

    params: dict[str, Any] = {}
    if regiao:
        regiao_norm = regiao.strip().upper()
        data = [
            estado
            for estado in data
            if estado.get("regiao", {}).get("sigla", "").upper() == regiao_norm
            or str(estado.get("regiao", {}).get("id")) == regiao_norm
        ]
        params["regiao"] = regiao

    return IBGEResult(data=data, endpoint=endpoint, params=params)


async def obter_estado(uf: str) -> IBGEResult:
    """Obtém os detalhes de um estado.

    Args:
        uf: Sigla (ex.: "SP") ou ID IBGE (ex.: "35") do estado.
    """
    endpoint = f"{LOCALIDADES_BASE_URL}/estados/{uf}"
    data = await get_json(endpoint)
    return IBGEResult(data=data, endpoint=endpoint, params={"uf": uf})


async def listar_municipios(uf: str | None = None) -> IBGEResult:
    """Lista municípios brasileiros, opcionalmente filtrados por estado.

    Args:
        uf: Sigla (ex.: "SP") ou ID IBGE do estado. Se omitido, retorna os
            ~5570 municípios do Brasil inteiro.
    """
    if uf:
        endpoint = f"{LOCALIDADES_BASE_URL}/estados/{uf}/municipios"
        params: dict[str, Any] = {"uf": uf}
    else:
        endpoint = f"{LOCALIDADES_BASE_URL}/municipios"
        params = {}

    data = await get_json(endpoint)
    return IBGEResult(data=data, endpoint=endpoint, params=params)


async def obter_municipio(codigo: str) -> IBGEResult:
    """Obtém os detalhes completos de um município pelo código IBGE de 7 dígitos.

    Args:
        codigo: Código IBGE do município (ex.: "3550308" para São Paulo/SP).
    """
    endpoint = f"{LOCALIDADES_BASE_URL}/municipios/{codigo}"
    data = await get_json(endpoint)
    return IBGEResult(data=data, endpoint=endpoint, params={"codigo": codigo})


async def buscar_municipios_por_nome(
    nome: str, uf: str | None = None, limit: int = 20
) -> IBGEResult:
    """Busca municípios cujo nome contenha o termo informado (case/acento-insensível).

    Args:
        nome: Termo de busca (ex.: "Sao Jose" encontra "São José dos Campos").
        uf: Restringe a busca aos municípios de um estado (sigla ou ID).
        limit: Número máximo de resultados retornados.
    """
    listagem = await listar_municipios(uf=uf)
    termo = _normalizar(nome)

    encontrados = [
        municipio for municipio in listagem.data if termo in _normalizar(municipio.get("nome", ""))
    ]
    encontrados = encontrados[: max(limit, 0)]

    params: dict[str, Any] = {"nome": nome, "limit": limit}
    if uf:
        params["uf"] = uf

    return IBGEResult(data=encontrados, endpoint=listagem.endpoint, params=params)
