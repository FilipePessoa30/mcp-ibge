"""Testes da camada de serviço `AgregadosService` (TypedToolResult, fonte e metadata)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.schemas.agregados import AgregadoPeriod
from mcp_ibge.services.agregados_service import (
    AGREGADO_POPULACAO_ESTIMADA,
    VARIAVEL_POPULACAO_ESTIMADA,
    AgregadosService,
)

BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

LISTA_AGREGADOS = [
    {
        "id": "POP",
        "nome": "Estimativas de população",
        "agregados": [{"id": 6579, "nome": "População residente estimada"}],
    },
    {
        "id": "CD",
        "nome": "Censo Demográfico",
        "agregados": [{"id": 9514, "nome": "Outra tabela"}],
    },
]

METADADOS = {
    "id": 6579,
    "nome": "População residente estimada",
    "pesquisa": "Estimativas de População",
    "assunto": "População",
    "periodicidade": {"frequencia": "anual", "inicio": 2001, "fim": 2024},
    "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
}

VARIAVEIS = [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}]

PERIODOS = [{"id": "2024", "literals": ["2024"], "modificacao": "2025-08-29T00:00:00.000-03:00"}]

LOCALIDADES = [{"id": "3550308", "nome": "São Paulo", "nivel": {"id": "N6", "nome": "Município"}}]


def _dados_populacao(localidade_id: str, localidade_nome: str, periodo: str, valor: str) -> list:
    return [
        {
            "id": VARIAVEL_POPULACAO_ESTIMADA,
            "unidade": "Pessoas",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": localidade_id, "nome": localidade_nome},
                            "serie": {periodo: valor},
                        }
                    ]
                }
            ],
        }
    ]


def _assert_tem_fonte_e_metadata(metadata) -> None:
    assert metadata.source_name == get_settings().source_name
    assert metadata.endpoint
    assert metadata.retrieved_at is not None


@respx.mock
async def test_listar_agregados_sem_filtro():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    service = AgregadosService()
    result = await service.listar_agregados()

    assert result.ok is True
    assert [item.id for item in result.data] == ["6579", "9514"]
    _assert_tem_fonte_e_metadata(result.metadata)


@respx.mock
async def test_listar_agregados_filtro_texto_local():
    respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=LISTA_AGREGADOS))

    service = AgregadosService()
    result = await service.listar_agregados(texto="outra")

    assert result.ok is True
    assert [item.id for item in result.data] == ["9514"]
    assert result.metadata.params["texto"] == "outra"


@respx.mock
async def test_listar_agregados_repassa_pesquisa_e_assunto():
    route = respx.get(BASE_URL).mock(return_value=httpx.Response(200, json=[]))

    service = AgregadosService()
    result = await service.listar_agregados(pesquisa="Censo Demográfico", assunto="População")

    assert result.ok is True
    assert result.data == []
    request = route.calls.last.request
    assert request.url.params["pesquisa"] == "Censo Demográfico"
    assert request.url.params["assunto"] == "População"


@respx.mock
async def test_obter_metadados_agregado():
    respx.get(f"{BASE_URL}/6579/metadados").mock(return_value=httpx.Response(200, json=METADADOS))

    service = AgregadosService()
    result = await service.obter_metadados_agregado("6579")

    assert result.ok is True
    assert result.data.id == "6579"
    assert result.data.nome == "População residente estimada"
    assert result.data.pesquisa == "Estimativas de População"
    assert result.data.assunto == "População"
    assert result.data.periodicidade == "anual"
    assert result.data.raw == METADADOS
    _assert_tem_fonte_e_metadata(result.metadata)


@respx.mock
async def test_obter_metadados_agregado_inexistente():
    respx.get(f"{BASE_URL}/9999999/metadados").mock(return_value=httpx.Response(404))

    service = AgregadosService()
    result = await service.obter_metadados_agregado("9999999")

    assert result.ok is False
    assert result.data is None
    assert result.errors
    _assert_tem_fonte_e_metadata(result.metadata)


@respx.mock
async def test_listar_variaveis_agregado():
    respx.get(f"{BASE_URL}/6579/variaveis").mock(return_value=httpx.Response(200, json=VARIAVEIS))

    service = AgregadosService()
    result = await service.listar_variaveis_agregado("6579")

    assert result.ok is True
    assert len(result.data) == 1
    assert result.data[0].id == "9324"
    assert result.data[0].unidade == "Pessoas"
    assert result.data[0].raw == VARIAVEIS[0]


@respx.mock
async def test_listar_periodos_agregado():
    respx.get(f"{BASE_URL}/6579/periodos").mock(return_value=httpx.Response(200, json=PERIODOS))

    service = AgregadosService()
    result = await service.listar_periodos_agregado("6579")

    assert result.ok is True
    assert result.data == [AgregadoPeriod(id="2024", nome="2024")]


@respx.mock
async def test_listar_localidades_agregado():
    respx.get(f"{BASE_URL}/6579/localidades/N6").mock(
        return_value=httpx.Response(200, json=LOCALIDADES)
    )

    service = AgregadosService()
    result = await service.listar_localidades_agregado("6579", "N6")

    assert result.ok is True
    assert result.data == LOCALIDADES
    assert result.metadata.params == {"agregado_id": "6579", "niveis": "N6"}


@respx.mock
async def test_consultar_agregado_resolve_alias_br():
    dados = _dados_populacao("1", "Brasil", "2024", "203080756")
    route = respx.get(f"{BASE_URL}/6579/periodos/-6/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    service = AgregadosService()
    result = await service.consultar_agregado("6579", variaveis="9324", localidades="BR")

    assert result.ok is True
    assert request_localidades(route) == "N1[all]"
    assert result.data[0].localidade_id == "1"
    assert result.data[0].localidade_nome == "Brasil"
    assert result.data[0].periodo == "2024"
    assert result.data[0].valor == 203080756.0
    assert result.data[0].unidade == "Pessoas"
    assert result.metadata.params["localidades"] == "N1[all]"


@respx.mock
async def test_consultar_agregado_com_classificacao_e_view():
    dados = _dados_populacao("3550308", "São Paulo", "2021", "12000000")
    route = respx.get(f"{BASE_URL}/6579/periodos/2021/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    service = AgregadosService()
    result = await service.consultar_agregado(
        "6579",
        variaveis="9324",
        localidades="N6[3550308]",
        periodos="2021",
        classificacao="2[6794]",
        view="flat",
    )

    assert result.ok is True
    request = route.calls.last.request
    assert request.url.params["classificacao"] == "2[6794]"
    assert request.url.params["view"] == "flat"


@respx.mock
async def test_consultar_populacao_municipio_periodo_mais_recente():
    dados = _dados_populacao("4205407", "Florianópolis", "2024", "537000")
    respx.get(f"{BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    service = AgregadosService()
    result = await service.consultar_populacao_municipio(4205407)

    assert result.ok is True
    assert result.data[0].localidade_nome == "Florianópolis"
    assert result.data[0].periodo == "2024"
    assert result.data[0].valor == 537000.0
    assert result.metadata.params["codigo_municipio"] == 4205407
    _assert_tem_fonte_e_metadata(result.metadata)


@respx.mock
async def test_consultar_populacao_municipio_com_ano():
    dados = _dados_populacao("4205407", "Florianópolis", "2010", "421000")
    respx.get(f"{BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}/periodos/2010/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    service = AgregadosService()
    result = await service.consultar_populacao_municipio(4205407, ano=2010)

    assert result.ok is True
    assert result.data[0].periodo == "2010"
    assert result.data[0].valor == 421000.0


@respx.mock
async def test_consultar_populacao_municipio_tabela_indisponivel_orienta_consultar_agregado():
    respx.get(f"{BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=[])
    )

    service = AgregadosService()
    result = await service.consultar_populacao_municipio(4205407)

    assert result.ok is False
    assert result.data == []
    assert result.errors
    assert "consultar_agregado" in result.errors[0]
    _assert_tem_fonte_e_metadata(result.metadata)


def request_localidades(route) -> str:
    return route.calls.last.request.url.params["localidades"]
