"""Testes do cliente da API de Agregados (SIDRA)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients import agregados
from mcp_ibge.config import AGREGADOS_BASE_URL

LISTA_AGREGADOS = [
    {
        "id": "POP",
        "nome": "Estimativas de população",
        "agregados": [
            {"id": 6579, "nome": "População residente estimada"},
            {"id": 1234, "nome": "Outro agregado qualquer"},
        ],
    },
    {
        "id": "CENSO",
        "nome": "Censo Demográfico",
        "agregados": [{"id": 9999, "nome": "Domicílios"}],
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
    respx.get(AGREGADOS_BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    result = await agregados.listar_agregados()

    assert result.data == LISTA_AGREGADOS
    assert result.endpoint == AGREGADOS_BASE_URL
    assert result.params == {}


@respx.mock
async def test_listar_agregados_com_filtro_textual():
    respx.get(AGREGADOS_BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    result = await agregados.listar_agregados(texto="população residente")

    assert len(result.data) == 1
    assert result.data[0]["agregados"] == [{"id": 6579, "nome": "População residente estimada"}]
    assert result.params == {"texto": "população residente"}


@respx.mock
async def test_listar_agregados_repassa_query_params():
    route = respx.get(AGREGADOS_BASE_URL).mock(return_value=httpx.Response(200, json=[]))

    await agregados.listar_agregados(pesquisa="Censo Demográfico", assunto="População")

    request = route.calls.last.request
    assert request.url.params["pesquisa"] == "Censo Demográfico"
    assert request.url.params["assunto"] == "População"


@respx.mock
async def test_obter_metadados_agregado():
    respx.get(f"{AGREGADOS_BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=METADADOS)
    )

    result = await agregados.obter_metadados_agregado(6579)

    assert result.data == METADADOS
    assert result.params == {"agregado_id": 6579}


@respx.mock
async def test_consultar_dados_agregado_valores_padrao():
    route = respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/all").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    result = await agregados.consultar_dados_agregado(6579)

    assert result.data == DADOS
    assert route.calls.last.request.url.params["localidades"] == "N1[all]"
    assert result.params["localidades"] == "N1[all]"


@respx.mock
async def test_consultar_dados_agregado_resolve_alias_br():
    route = respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    await agregados.consultar_dados_agregado(6579, variaveis="9324", localidades="BR")

    assert route.calls.last.request.url.params["localidades"] == "N1[all]"


@respx.mock
async def test_consultar_dados_agregado_com_classificacao():
    route = respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/2021/variaveis/9324").mock(
        return_value=httpx.Response(200, json=DADOS)
    )

    result = await agregados.consultar_dados_agregado(
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
