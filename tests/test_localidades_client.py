"""Testes do cliente "fino" `LocalidadesClient` (sem regras de negócio)."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.localidades import LOCALIDADES_PATH, LocalidadesClient
from mcp_ibge.config import get_settings
from mcp_ibge.utils.errors import IBGENotFoundError

BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"

REGIOES = [
    {"id": 1, "sigla": "N", "nome": "Norte"},
    {"id": 2, "sigla": "NE", "nome": "Nordeste"},
]

ESTADOS = [
    {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    },
]

MUNICIPIOS_SP = [
    {"id": 3550308, "nome": "São Paulo"},
    {"id": 3548807, "nome": "São José dos Campos"},
]


@respx.mock
async def test_listar_regioes():
    respx.get(f"{BASE_URL}/regioes").mock(return_value=httpx.Response(200, json=REGIOES))

    client = LocalidadesClient()
    result = await client.listar_regioes()

    assert result.data == REGIOES
    assert result.endpoint == f"{BASE_URL}/regioes"
    assert result.params == {}


@respx.mock
async def test_listar_estados():
    respx.get(f"{BASE_URL}/estados").mock(return_value=httpx.Response(200, json=ESTADOS))

    client = LocalidadesClient()
    result = await client.listar_estados()

    assert result.data == ESTADOS
    assert result.endpoint == f"{BASE_URL}/estados"


@respx.mock
async def test_obter_estado():
    respx.get(f"{BASE_URL}/estados/SP").mock(return_value=httpx.Response(200, json=ESTADOS[0]))

    client = LocalidadesClient()
    result = await client.obter_estado("SP")

    assert result.data == ESTADOS[0]
    assert result.params == {"uf": "SP"}


@respx.mock
async def test_listar_municipios_por_uf():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    client = LocalidadesClient()
    result = await client.listar_municipios(uf="SP")

    assert result.data == MUNICIPIOS_SP
    assert result.params == {"uf": "SP"}


@respx.mock
async def test_listar_municipios_brasil_inteiro():
    respx.get(f"{BASE_URL}/municipios").mock(return_value=httpx.Response(200, json=MUNICIPIOS_SP))

    client = LocalidadesClient()
    result = await client.listar_municipios()

    assert result.data == MUNICIPIOS_SP
    assert result.endpoint == f"{BASE_URL}/municipios"
    assert result.params == {}


@respx.mock
async def test_obter_municipio():
    municipio = {"id": 3550308, "nome": "São Paulo"}
    respx.get(f"{BASE_URL}/municipios/3550308").mock(
        return_value=httpx.Response(200, json=municipio)
    )

    client = LocalidadesClient()
    result = await client.obter_municipio("3550308")

    assert result.data == municipio
    assert result.params == {"codigo": "3550308"}


@respx.mock
async def test_obter_municipio_404_levanta_erro():
    respx.get(f"{BASE_URL}/municipios/0000000").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    client = LocalidadesClient()
    with pytest.raises(IBGENotFoundError) as exc_info:
        await client.obter_municipio("0000000")

    assert exc_info.value.status_code == 404


@respx.mock
async def test_get_json_usa_cache():
    route = respx.get(f"{BASE_URL}/regioes").mock(return_value=httpx.Response(200, json=REGIOES))

    client = LocalidadesClient()
    await client.listar_regioes()
    await client.listar_regioes()

    assert route.call_count == 1
