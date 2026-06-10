"""Testes do cliente da API de Localidades."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients import localidades
from mcp_ibge.config import LOCALIDADES_BASE_URL

REGIOES = [
    {"id": 1, "sigla": "N", "nome": "Norte"},
    {"id": 2, "sigla": "NE", "nome": "Nordeste"},
    {"id": 3, "sigla": "SE", "nome": "Sudeste"},
]

ESTADOS = [
    {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    },
    {
        "id": 23,
        "sigla": "CE",
        "nome": "Ceará",
        "regiao": {"id": 2, "sigla": "NE", "nome": "Nordeste"},
    },
]

MUNICIPIOS_SP = [
    {"id": 3550308, "nome": "São Paulo"},
    {"id": 3548807, "nome": "São José dos Campos"},
    {"id": 3509502, "nome": "Campinas"},
]


@respx.mock
async def test_listar_regioes():
    respx.get(f"{LOCALIDADES_BASE_URL}/regioes").mock(
        return_value=httpx.Response(200, json=REGIOES)
    )

    result = await localidades.listar_regioes()

    assert result.data == REGIOES
    assert result.endpoint == f"{LOCALIDADES_BASE_URL}/regioes"
    assert result.params == {}


@respx.mock
async def test_listar_estados_sem_filtro():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=ESTADOS)
    )

    result = await localidades.listar_estados()

    assert result.data == ESTADOS
    assert result.params == {}


@respx.mock
async def test_listar_estados_filtra_por_regiao():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=ESTADOS)
    )

    result = await localidades.listar_estados(regiao="NE")

    assert result.data == [ESTADOS[1]]
    assert result.params == {"regiao": "NE"}


@respx.mock
async def test_obter_estado():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP").mock(
        return_value=httpx.Response(200, json=ESTADOS[0])
    )

    result = await localidades.obter_estado("SP")

    assert result.data == ESTADOS[0]
    assert result.endpoint == f"{LOCALIDADES_BASE_URL}/estados/SP"
    assert result.params == {"uf": "SP"}


@respx.mock
async def test_listar_municipios_por_uf():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await localidades.listar_municipios(uf="SP")

    assert result.data == MUNICIPIOS_SP
    assert result.params == {"uf": "SP"}


@respx.mock
async def test_obter_municipio():
    municipio = {"id": 3550308, "nome": "São Paulo"}
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3550308").mock(
        return_value=httpx.Response(200, json=municipio)
    )

    result = await localidades.obter_municipio("3550308")

    assert result.data == municipio
    assert result.params == {"codigo": "3550308"}


@respx.mock
async def test_buscar_municipios_por_nome_ignora_acentos_e_caixa():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await localidades.buscar_municipios_por_nome("sao jose", uf="SP")

    assert result.data == [MUNICIPIOS_SP[1]]
    assert result.params == {"nome": "sao jose", "limit": 20, "uf": "SP"}


@respx.mock
async def test_buscar_municipios_por_nome_aplica_limit():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await localidades.buscar_municipios_por_nome("sao", uf="SP", limit=1)

    assert len(result.data) == 1
    assert result.data[0] == MUNICIPIOS_SP[0]
