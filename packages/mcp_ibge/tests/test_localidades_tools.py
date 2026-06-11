"""Testes de contrato das tools MCP de Localidades: existência e formato JSON."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.server import mcp

from .conftest import assert_envelope_contract

BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"

LOCALIDADES_TOOLS = {
    "listar_regioes",
    "listar_estados",
    "obter_estado",
    "listar_municipios",
    "buscar_municipio",
    "obter_codigo_municipio",
    "obter_municipio_por_codigo",
    "listar_distritos",
}

REGIOES = [{"id": 1, "sigla": "N", "nome": "Norte"}]

ESTADOS = [
    {
        "id": 35,
        "sigla": "SP",
        "nome": "São Paulo",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    }
]


def _municipio(municipio_id: int, nome: str) -> dict:
    return {
        "id": municipio_id,
        "nome": nome,
        "microrregiao": {
            "id": 35061,
            "nome": "São Paulo",
            "mesorregiao": {
                "id": 3515,
                "nome": "Metropolitana de São Paulo",
                "UF": {
                    "id": 35,
                    "sigla": "SP",
                    "nome": "São Paulo",
                    "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
                },
            },
        },
    }


MUNICIPIOS_SP = [_municipio(3550308, "São Paulo"), _municipio(3509502, "Campinas")]

DISTRITOS_SP = [{"id": 355030801, "nome": "Sé", "municipio": {"id": 3550308, "nome": "São Paulo"}}]


async def test_todas_as_tools_de_localidades_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert LOCALIDADES_TOOLS.issubset(nomes)


@respx.mock
@pytest.mark.parametrize(
    ("nome_tool", "argumentos", "endpoint_mock", "resposta_mock"),
    [
        ("listar_regioes", {}, f"{BASE_URL}/regioes", REGIOES),
        ("listar_estados", {}, f"{BASE_URL}/estados", ESTADOS),
        ("obter_estado", {"uf": "SP"}, f"{BASE_URL}/estados/SP", ESTADOS[0]),
        ("listar_municipios", {"uf": "SP"}, f"{BASE_URL}/estados/SP/municipios", MUNICIPIOS_SP),
        (
            "buscar_municipio",
            {"nome": "Campinas", "uf": "SP"},
            f"{BASE_URL}/estados/SP/municipios",
            MUNICIPIOS_SP,
        ),
        (
            "obter_codigo_municipio",
            {"nome": "Campinas", "uf": "SP"},
            f"{BASE_URL}/estados/SP/municipios",
            MUNICIPIOS_SP,
        ),
        (
            "obter_municipio_por_codigo",
            {"codigo_ibge": 3550308},
            f"{BASE_URL}/municipios/3550308",
            MUNICIPIOS_SP[0],
        ),
        (
            "listar_distritos",
            {"codigo_municipio": 3550308},
            f"{BASE_URL}/municipios/3550308/distritos",
            DISTRITOS_SP,
        ),
    ],
)
async def test_tool_retorna_contrato_json_em_caso_de_sucesso(
    nome_tool, argumentos, endpoint_mock, resposta_mock
):
    respx.get(endpoint_mock).mock(return_value=httpx.Response(200, json=resposta_mock))

    _, structured = await mcp.call_tool(nome_tool, argumentos)

    assert_envelope_contract(structured)
    assert "data" in structured


@respx.mock
async def test_buscar_municipio_ambiguo_inclui_warnings_no_contrato():
    municipios_sao_jose = [
        _municipio(3548807, "São José dos Campos"),
        _municipio(3549904, "São José do Rio Preto"),
    ]
    respx.get(f"{BASE_URL}/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose)
    )

    _, structured = await mcp.call_tool("buscar_municipio", {"nome": "São José"})

    assert_envelope_contract(structured)
    assert "data" in structured
    assert "warnings" in structured
    assert structured["warnings"]


@respx.mock
async def test_tool_retorna_contrato_json_em_caso_de_erro():
    respx.get(f"{BASE_URL}/municipios/9999999").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    _, structured = await mcp.call_tool("obter_municipio_por_codigo", {"codigo_ibge": 9999999})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]
