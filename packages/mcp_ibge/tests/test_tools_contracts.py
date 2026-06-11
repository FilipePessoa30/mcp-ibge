"""Testes de contrato das tools MCP: nomes registrados e formato do envelope."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.server import mcp

from .conftest import assert_envelope_contract

LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

EXPECTED_TOOLS = {
    "listar_regioes",
    "listar_estados",
    "obter_estado",
    "listar_municipios",
    "buscar_municipio",
    "obter_codigo_municipio",
    "obter_municipio_por_codigo",
    "listar_distritos",
    "listar_agregados",
    "obter_metadados_agregado",
    "listar_variaveis_agregado",
    "listar_periodos_agregado",
    "listar_localidades_agregado",
    "consultar_agregado",
    "consultar_populacao_municipio",
}


async def test_todas_as_tools_esperadas_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert EXPECTED_TOOLS.issubset(nomes)


@respx.mock
async def test_envelope_de_sucesso_contem_metadata_e_data():
    respx.get(f"{LOCALIDADES_BASE_URL}/regioes").mock(
        return_value=httpx.Response(200, json=[{"id": 1, "sigla": "N", "nome": "Norte"}])
    )

    _, structured = await mcp.call_tool("listar_regioes", {})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]
    assert structured["errors"] == []
    assert structured["metadata"]["endpoint"] == f"{LOCALIDADES_BASE_URL}/regioes"


@respx.mock
async def test_envelope_de_erro_contem_metadata_e_errors():
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/9999999").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    _, structured = await mcp.call_tool("obter_municipio_por_codigo", {"codigo_ibge": 9999999})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]


@respx.mock
async def test_consultar_agregado_resolve_alias_br():
    dados = [
        {
            "id": "9324",
            "variavel": "População residente estimada",
            "unidade": "Pessoas",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": "1", "nome": "Brasil"},
                            "serie": {"2024": "203080756"},
                        }
                    ]
                }
            ],
        }
    ]
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-6/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    _, structured = await mcp.call_tool(
        "consultar_agregado",
        {"agregado_id": "6579", "variaveis": "9324", "localidades": "BR"},
    )

    assert structured["data"][0]["localidade_id"] == "1"
    assert structured["data"][0]["valor"] == 203080756.0
    assert structured["metadata"]["params"]["localidades"] == "N1[all]"


@respx.mock
async def test_consultar_populacao_municipio_niteroi(municipio_niteroi, agregado_consulta_resposta):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_niteroi])
    )

    endpoint = f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324"
    respx.get(endpoint).mock(return_value=httpx.Response(200, json=agregado_consulta_resposta))

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "Niterói", "uf": "RJ"}
    )

    assert structured["data"][0]["localidade_nome"] == "Niterói"
    assert structured["data"][0]["valor"] == 516981.0
    assert structured["metadata"]["endpoint"] == endpoint
    assert structured["metadata"]["params"]["codigo_municipio"] == 3303302
    assert structured["metadata"]["params"]["uf"] == "RJ"


@respx.mock
async def test_consultar_populacao_municipio_envelope():
    municipio = {
        "id": 4205407,
        "nome": "Florianópolis",
        "microrregiao": {
            "id": 42017,
            "nome": "Florianópolis",
            "mesorregiao": {
                "id": 4202,
                "nome": "Grande Florianópolis",
                "UF": {
                    "id": 42,
                    "sigla": "SC",
                    "nome": "Santa Catarina",
                    "regiao": {"id": 4, "sigla": "S", "nome": "Sul"},
                },
            },
        },
    }
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SC/municipios").mock(
        return_value=httpx.Response(200, json=[municipio])
    )

    endpoint = f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324"
    dados = [
        {
            "id": "9324",
            "unidade": "Pessoas",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": "4205407", "nome": "Florianópolis"},
                            "serie": {"2024": "537000"},
                        }
                    ]
                }
            ],
        }
    ]
    respx.get(endpoint).mock(return_value=httpx.Response(200, json=dados))

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "Florianópolis", "uf": "SC"}
    )

    assert structured["data"][0]["localidade_nome"] == "Florianópolis"
    assert structured["data"][0]["valor"] == 537000.0
    assert structured["metadata"]["endpoint"] == endpoint
    assert structured["metadata"]["params"]["codigo_municipio"] == 4205407
    assert structured["metadata"]["params"]["nome"] == "Florianópolis"
    assert structured["metadata"]["params"]["uf"] == "SC"


@respx.mock
async def test_todas_as_tools_retornam_envelope_padrao(
    estado_rj, municipio_rio_de_janeiro, municipio_niteroi, agregado_consulta_resposta
):
    """Garante que toda tool registrada responde com o envelope padrão.

    O envelope é `{ok, data, metadata, warnings, errors}` (ver
    `assert_envelope_contract`).
    """
    municipios_rj = [municipio_rio_de_janeiro, municipio_niteroi]
    distrito_rj = {
        "id": 3304557001,
        "nome": "Rio de Janeiro",
        "municipio": {"id": 3304557, "nome": "Rio de Janeiro"},
    }

    lista_agregados = [
        {
            "id": "POP",
            "nome": "Estimativas de população",
            "agregados": [{"id": 6579, "nome": "População residente estimada"}],
        }
    ]
    metadados_agregado = {
        "id": 6579,
        "nome": "População residente estimada",
        "pesquisa": "Estimativas de População",
        "assunto": "População",
        "periodicidade": {"frequencia": "anual", "inicio": 2001, "fim": 2024},
        "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
    }
    variaveis_agregado = [
        {"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}
    ]
    periodos_agregado = [
        {"id": "2024", "literals": ["2024"], "modificacao": "2025-08-29T00:00:00.000-03:00"}
    ]
    localidades_agregado = [
        {"id": "3304557", "nome": "Rio de Janeiro", "nivel": {"id": "N6", "nome": "Município"}}
    ]
    dados_brasil = [
        {
            "id": "9324",
            "variavel": "População residente estimada",
            "unidade": "Pessoas",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": "1", "nome": "Brasil"},
                            "serie": {"2024": "203080756"},
                        }
                    ]
                }
            ],
        }
    ]

    respx.get(f"{LOCALIDADES_BASE_URL}/regioes").mock(
        return_value=httpx.Response(200, json=[{"id": 3, "sigla": "SE", "nome": "Sudeste"}])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[estado_rj])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ").mock(
        return_value=httpx.Response(200, json=estado_rj)
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=municipios_rj)
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557/distritos").mock(
        return_value=httpx.Response(200, json=[distrito_rj])
    )

    respx.get(AGREGADOS_BASE_URL).mock(return_value=httpx.Response(200, json=lista_agregados))
    respx.get(f"{AGREGADOS_BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=metadados_agregado)
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/variaveis").mock(
        return_value=httpx.Response(200, json=variaveis_agregado)
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos").mock(
        return_value=httpx.Response(200, json=periodos_agregado)
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/localidades/N6").mock(
        return_value=httpx.Response(200, json=localidades_agregado)
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-6/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados_brasil)
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=agregado_consulta_resposta)
    )

    chamadas = [
        ("listar_regioes", {}),
        ("listar_estados", {}),
        ("obter_estado", {"uf": "RJ"}),
        ("listar_municipios", {"uf": "RJ"}),
        ("buscar_municipio", {"nome": "Rio de Janeiro", "uf": "RJ"}),
        ("obter_codigo_municipio", {"nome": "Rio de Janeiro", "uf": "RJ"}),
        ("obter_municipio_por_codigo", {"codigo_ibge": 3304557}),
        ("listar_distritos", {"codigo_municipio": 3304557}),
        ("listar_agregados", {}),
        ("obter_metadados_agregado", {"agregado_id": "6579"}),
        ("listar_variaveis_agregado", {"agregado_id": "6579"}),
        ("listar_periodos_agregado", {"agregado_id": "6579"}),
        ("listar_localidades_agregado", {"agregado_id": "6579", "niveis": "N6"}),
        (
            "consultar_agregado",
            {"agregado_id": "6579", "variaveis": "9324", "localidades": "N1[all]"},
        ),
        ("consultar_populacao_municipio", {"nome": "Niterói", "uf": "RJ"}),
    ]

    assert {nome_tool for nome_tool, _ in chamadas} == EXPECTED_TOOLS

    for nome_tool, argumentos in chamadas:
        _, structured = await mcp.call_tool(nome_tool, argumentos)

        assert_envelope_contract(structured)
        assert structured["ok"] is True, f"{nome_tool}: {structured['errors']}"
        assert structured["errors"] == []
