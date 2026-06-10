"""Testes de contrato das tools MCP de Agregados/SIDRA: existência e formato JSON."""

from __future__ import annotations

import json

import httpx
import pytest
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.server import mcp

AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"
LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"

AGREGADOS_TOOLS = {
    "listar_agregados",
    "obter_metadados_agregado",
    "listar_variaveis_agregado",
    "listar_periodos_agregado",
    "listar_localidades_agregado",
    "consultar_agregado",
    "consultar_populacao_municipio",
}

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
            "id": "9324",
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


def _municipio(municipio_id: int, nome: str, uf_sigla: str = "SC") -> dict:
    return {
        "id": municipio_id,
        "nome": nome,
        "microrregiao": {
            "id": 1,
            "nome": "Microrregião",
            "mesorregiao": {
                "id": 1,
                "nome": "Mesorregião",
                "UF": {
                    "id": 42,
                    "sigla": uf_sigla,
                    "nome": "Santa Catarina",
                    "regiao": {"id": 4, "sigla": "S", "nome": "Sul"},
                },
            },
        },
    }


async def test_todas_as_tools_de_agregados_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert AGREGADOS_TOOLS.issubset(nomes)


def _assert_contrato_json(structured: dict) -> None:
    """Garante que a resposta é um dict JSON-serializável com `metadata` e `data`/`error`."""
    assert isinstance(structured, dict)
    assert "metadata" in structured
    assert ("data" in structured) ^ ("error" in structured)
    json.dumps(structured)


@respx.mock
@pytest.mark.parametrize(
    ("nome_tool", "argumentos", "endpoint_mock", "resposta_mock"),
    [
        ("listar_agregados", {}, AGREGADOS_BASE_URL, LISTA_AGREGADOS),
        (
            "obter_metadados_agregado",
            {"agregado_id": "6579"},
            f"{AGREGADOS_BASE_URL}/6579/metadados",
            METADADOS,
        ),
        (
            "listar_variaveis_agregado",
            {"agregado_id": "6579"},
            f"{AGREGADOS_BASE_URL}/6579/variaveis",
            VARIAVEIS,
        ),
        (
            "listar_periodos_agregado",
            {"agregado_id": "6579"},
            f"{AGREGADOS_BASE_URL}/6579/periodos",
            PERIODOS,
        ),
        (
            "listar_localidades_agregado",
            {"agregado_id": "6579", "niveis": "N6"},
            f"{AGREGADOS_BASE_URL}/6579/localidades/N6",
            LOCALIDADES,
        ),
        (
            "consultar_agregado",
            {"agregado_id": "6579", "variaveis": "9324", "localidades": "N1[all]"},
            f"{AGREGADOS_BASE_URL}/6579/periodos/-6/variaveis/9324",
            _dados_populacao("1", "Brasil", "2024", "203080756"),
        ),
    ],
)
async def test_tool_retorna_contrato_json_em_caso_de_sucesso(
    nome_tool, argumentos, endpoint_mock, resposta_mock
):
    respx.get(endpoint_mock).mock(return_value=httpx.Response(200, json=resposta_mock))

    _, structured = await mcp.call_tool(nome_tool, argumentos)

    _assert_contrato_json(structured)
    assert "data" in structured


@respx.mock
async def test_consultar_populacao_municipio_resolve_codigo_e_consulta_agregado():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SC/municipios").mock(
        return_value=httpx.Response(200, json=[_municipio(4205407, "Florianópolis")])
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("4205407", "Florianópolis", "2024", "537000")
        )
    )

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "Florianópolis", "uf": "SC"}
    )

    _assert_contrato_json(structured)
    assert structured["data"][0]["localidade_nome"] == "Florianópolis"
    assert structured["data"][0]["valor"] == 537000.0
    assert structured["metadata"]["params"]["nome"] == "Florianópolis"
    assert structured["metadata"]["params"]["uf"] == "SC"
    assert structured["metadata"]["params"]["codigo_municipio"] == 4205407
    assert "warnings" in structured


@respx.mock
async def test_consultar_populacao_municipio_com_ano_nao_avisa_sobre_periodo():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SC/municipios").mock(
        return_value=httpx.Response(200, json=[_municipio(4205407, "Florianópolis")])
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/2010/variaveis/9324").mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("4205407", "Florianópolis", "2010", "421000")
        )
    )

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "Florianópolis", "uf": "SC", "ano": 2010}
    )

    _assert_contrato_json(structured)
    assert structured["data"][0]["periodo"] == "2010"
    assert "warnings" not in structured


@respx.mock
async def test_consultar_populacao_municipio_dado_ausente_inclui_warning():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SC/municipios").mock(
        return_value=httpx.Response(200, json=[_municipio(4205407, "Florianópolis")])
    )
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("4205407", "Florianópolis", "2024", "...")
        )
    )

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "Florianópolis", "uf": "SC"}
    )

    _assert_contrato_json(structured)
    assert structured["data"][0]["valor"] is None
    assert any("não está disponível" in aviso for aviso in structured["warnings"])


@respx.mock
async def test_consultar_populacao_municipio_nome_ambiguo_retorna_erro_com_candidatos():
    municipios_sao_jose = [
        _municipio(3548807, "São José dos Campos"),
        _municipio(3549904, "São José do Rio Preto"),
    ]
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose)
    )

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "São José", "uf": "SP"}
    )

    _assert_contrato_json(structured)
    assert "error" in structured
    assert "São José dos Campos" in structured["error"]


@respx.mock
async def test_consultar_populacao_municipio_nome_inexistente_retorna_erro():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SC/municipios").mock(
        return_value=httpx.Response(200, json=[_municipio(4205407, "Florianópolis")])
    )

    _, structured = await mcp.call_tool(
        "consultar_populacao_municipio", {"nome": "Cidade Inexistente", "uf": "SC"}
    )

    _assert_contrato_json(structured)
    assert "error" in structured


@respx.mock
async def test_tool_retorna_contrato_json_em_caso_de_erro():
    respx.get(f"{AGREGADOS_BASE_URL}/9999999/metadados").mock(return_value=httpx.Response(404))

    _, structured = await mcp.call_tool("obter_metadados_agregado", {"agregado_id": "9999999"})

    _assert_contrato_json(structured)
    assert "error" in structured
