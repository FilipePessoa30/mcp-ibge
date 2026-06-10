"""Testes do cliente "fino" `AgregadosClient` (sem regras de negócio)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH, AgregadosClient
from mcp_ibge.config import get_settings

BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

LISTA_AGREGADOS = [
    {
        "id": "POP",
        "nome": "Estimativas de população",
        "agregados": [{"id": 6579, "nome": "População residente estimada"}],
    },
]

METADADOS = {
    "id": 6579,
    "nome": "População residente estimada",
    "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
}

DADOS = [
    {
        "id": "9324",
        "variavel": "População residente estimada",
        "resultados": [
            {
                "series": [
                    {
                        "localidade": {"id": "3550308", "nome": "São Paulo"},
                        "serie": {"2024": "12345678"},
                    }
                ]
            }
        ],
    }
]


@respx.mock
async def test_listar_agregados_sem_filtro():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    client = AgregadosClient()
    result = await client.listar_agregados()

    assert result.data == LISTA_AGREGADOS
    assert result.endpoint == BASE_URL
    assert result.params == {}


@respx.mock
async def test_listar_agregados_repassa_query_params():
    route = respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=[]))

    client = AgregadosClient()
    await client.listar_agregados(pesquisa="Censo Demográfico", assunto="População")

    request = route.calls.last.request
    assert request.url.params["pesquisa"] == "Censo Demográfico"
    assert request.url.params["assunto"] == "População"


@respx.mock
async def test_obter_metadados():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    client = AgregadosClient()
    result = await client.obter_metadados(6579)

    assert result.data == METADADOS
    assert result.params == {"agregado_id": 6579}


@respx.mock
async def test_consultar_dados_valores_padrao():
    route = respx.get(f"{BASE_URL}/6579/periodos/-1/variaveis/all").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    client = AgregadosClient()
    result = await client.consultar_dados(6579)

    assert result.data == DADOS
    assert route.calls.last.request.url.params["localidades"] == "N1[all]"
    assert result.params["localidades"] == "N1[all]"


@respx.mock
async def test_consultar_dados_com_classificacao():
    route = respx.get(f"{BASE_URL}/6579/periodos/2021/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    client = AgregadosClient()
    result = await client.consultar_dados(
        6579,
        variaveis="9324",
        periodos="2021",
        localidades="N6[3550308]",
        classificacoes="2[6794]",
    )

    request = route.calls.last.request
    assert request.url.params["localidades"] == "N6[3550308]"
    assert request.url.params["classificacao"] == "2[6794]"
    assert result.params["classificacao"] == "2[6794]"
