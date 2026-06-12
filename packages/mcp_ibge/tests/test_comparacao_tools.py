"""Testes de contrato da tool MCP `comparar_municipios`."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.server import mcp
from mcp_ibge.services.agregados_service import (
    AGREGADO_POPULACAO_ESTIMADA,
    VARIAVEL_POPULACAO_ESTIMADA,
)

from .conftest import assert_envelope_contract

LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

_POPULACAO_URL = (
    f"{AGREGADOS_BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}"
    f"/periodos/-1/variaveis/{VARIAVEL_POPULACAO_ESTIMADA}"
)


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


def _populacao_side_effect(populacao_por_codigo: dict[str, list]):
    def _handler(request: httpx.Request) -> httpx.Response:
        localidades = request.url.params["localidades"]
        codigo = localidades.removeprefix("N6[").removesuffix("]")
        return httpx.Response(200, json=populacao_por_codigo[codigo])

    return _handler


async def test_comparar_municipios_tool_esta_registrada():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert "comparar_municipios" in nomes


@respx.mock
async def test_comparar_municipios_retorna_contrato(municipio_rio_de_janeiro, municipio_niteroi):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro, municipio_niteroi])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=municipio_niteroi)
    )

    populacao_por_codigo = {
        "3304557": _dados_populacao("3304557", "Rio de Janeiro", "2024", "6211423"),
        "3303302": _dados_populacao("3303302", "Niterói", "2024", "516981"),
    }
    respx.get(_POPULACAO_URL).mock(side_effect=_populacao_side_effect(populacao_por_codigo))

    _, structured = await mcp.call_tool(
        "comparar_municipios",
        {
            "municipios": [
                {"nome": "Rio de Janeiro", "uf": "RJ"},
                {"nome": "Niterói", "uf": "RJ"},
            ]
        },
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["indicadores_consultados"] == ["populacao_estimada"]
    assert structured["data"]["municipios_nao_resolvidos"] == []

    por_nome = {m["nome"]: m for m in structured["data"]["municipios"]}
    assert por_nome["Rio de Janeiro"]["codigo_ibge"] == 3304557
    assert por_nome["Rio de Janeiro"]["indicadores"][0]["valor"] == 6211423.0
    assert por_nome["Niterói"]["indicadores"][0]["valor"] == 516981.0
    assert structured["data"]["fontes"]
    assert structured["data"]["limitacoes"]


@respx.mock
async def test_comparar_municipios_indicador_nao_implementado_retorna_warning(
    municipio_rio_de_janeiro,
):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(_POPULACAO_URL).mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("3304557", "Rio de Janeiro", "2024", "6211423")
        )
    )

    _, structured = await mcp.call_tool(
        "comparar_municipios",
        {
            "municipios": [{"nome": "Rio de Janeiro", "uf": "RJ"}],
            "indicadores": ["populacao", "pib"],
        },
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["indicadores_nao_implementados"] == ["pib"]
    assert any('"pib"' in aviso["message"] for aviso in structured["warnings"])


async def test_comparar_municipios_lista_vazia_retorna_erro():
    _, structured = await mcp.call_tool("comparar_municipios", {"municipios": []})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]
