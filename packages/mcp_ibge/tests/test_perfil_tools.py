"""Testes de contrato da tool MCP `gerar_perfil_municipal`."""

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


def _municipio_sp(municipio_id: int, nome: str) -> dict:
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
                    "id": 35,
                    "sigla": "SP",
                    "nome": "São Paulo",
                    "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
                },
            },
        },
    }


async def test_perfil_municipal_tool_esta_registrada():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert "gerar_perfil_municipal" in nomes


@respx.mock
async def test_gerar_perfil_municipal_niteroi_retorna_contrato(
    municipio_niteroi, agregado_consulta_resposta
):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_niteroi])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=municipio_niteroi)
    )
    respx.get(_POPULACAO_URL).mock(
        return_value=httpx.Response(200, json=agregado_consulta_resposta)
    )

    _, structured = await mcp.call_tool("gerar_perfil_municipal", {"nome": "Niterói", "uf": "RJ"})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["municipio"]["codigo_ibge"] == 3303302
    assert structured["data"]["municipio"]["nome"] == "Niterói"
    assert structured["data"]["indicadores"][0]["indicador"] == "populacao_estimada"
    assert structured["data"]["proximos_indicadores_sugeridos"]
    assert structured["data"]["limitacoes"]


@respx.mock
async def test_gerar_perfil_municipal_nome_ambiguo_retorna_erro_com_candidatos():
    municipios_sao_jose = [
        _municipio_sp(3548807, "São José dos Campos"),
        _municipio_sp(3549904, "São José do Rio Preto"),
    ]
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose)
    )

    _, structured = await mcp.call_tool("gerar_perfil_municipal", {"nome": "São José", "uf": "SP"})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert any("São José dos Campos" in erro["message"] for erro in structured["errors"])
