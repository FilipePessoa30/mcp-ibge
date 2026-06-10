"""Testes da camada de serviço `LocalidadesService` (filtros, busca, validação)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.config import get_settings
from mcp_ibge.services.localidades_service import LocalidadesService

BASE_URL = get_settings().localidades_base_url

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
async def test_listar_estados_sem_filtro_preserva_todos():
    respx.get(f"{BASE_URL}/estados").mock(return_value=httpx.Response(200, json=ESTADOS))

    result = await LocalidadesService().listar_estados()

    assert [e["sigla"] for e in result.data] == ["SP", "CE"]
    assert result.params == {}


@respx.mock
async def test_listar_estados_filtra_por_sigla_de_regiao():
    respx.get(f"{BASE_URL}/estados").mock(return_value=httpx.Response(200, json=ESTADOS))

    result = await LocalidadesService().listar_estados(regiao="ne")

    assert [e["sigla"] for e in result.data] == ["CE"]
    assert result.params == {"regiao": "ne"}


@respx.mock
async def test_listar_estados_filtra_por_id_de_regiao():
    respx.get(f"{BASE_URL}/estados").mock(return_value=httpx.Response(200, json=ESTADOS))

    result = await LocalidadesService().listar_estados(regiao="3")

    assert [e["sigla"] for e in result.data] == ["SP"]


@respx.mock
async def test_buscar_municipios_por_nome_ignora_acentos_e_caixa():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().buscar_municipios_por_nome("sao jose", uf="SP")

    assert [m["nome"] for m in result.data] == ["São José dos Campos"]
    assert result.params == {"nome": "sao jose", "limit": 20, "uf": "SP"}


@respx.mock
async def test_buscar_municipios_por_nome_aplica_limit():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().buscar_municipios_por_nome("sao", uf="SP", limit=1)

    assert len(result.data) == 1
    assert result.data[0]["nome"] == "São Paulo"


@respx.mock
async def test_buscar_municipios_sem_correspondencia_retorna_lista_vazia():
    respx.get(f"{BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=MUNICIPIOS_SP)
    )

    result = await LocalidadesService().buscar_municipios_por_nome("Curitiba", uf="SP")

    assert result.data == []
