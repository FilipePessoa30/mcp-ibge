"""Testes de contrato das tools MCP de organizações: existência e formato JSON."""

from __future__ import annotations

import httpx
import respx

from mcp_dados_gov_br.config import get_settings
from mcp_dados_gov_br.server import mcp

from .conftest import assert_envelope_contract

BASE_URL = get_settings().api_base_url

ORGANIZACAO_TOOLS = {"buscar_organizacoes", "obter_organizacao"}

ORGANIZATION_RAW = {
    "id": "org-mec",
    "name": "mec",
    "title": "Ministério da Educação",
    "description": "Órgão responsável pela política educacional.",
    "image_url": "https://dados.gov.br/images/mec.png",
    "package_count": 42,
}


def _ckan_ok(result: object) -> httpx.Response:
    return httpx.Response(200, json={"success": True, "result": result})


async def test_todas_as_tools_de_organizacoes_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert ORGANIZACAO_TOOLS.issubset(nomes)


@respx.mock
async def test_buscar_organizacoes_com_query_retorna_contrato_json():
    respx.get(f"{BASE_URL}/organization_autocomplete").mock(
        return_value=_ckan_ok([{"id": "org-mec", "name": "mec", "title": "Ministério da Educação"}])
    )

    _, structured = await mcp.call_tool(
        "buscar_organizacoes", {"query": "educação", "limite": 10}
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"][0]["name"] == "mec"


@respx.mock
async def test_buscar_organizacoes_sem_query_retorna_contrato_json():
    respx.get(f"{BASE_URL}/organization_list").mock(return_value=_ckan_ok([ORGANIZATION_RAW]))

    _, structured = await mcp.call_tool("buscar_organizacoes", {})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"][0]["id"] == "org-mec"


@respx.mock
async def test_obter_organizacao_retorna_contrato_json():
    respx.get(f"{BASE_URL}/organization_show").mock(return_value=_ckan_ok(ORGANIZATION_RAW))

    _, structured = await mcp.call_tool("obter_organizacao", {"organization_id": "org-mec"})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["title"] == "Ministério da Educação"
    assert structured["data"]["package_count"] == 42


@respx.mock
async def test_obter_organizacao_exige_token_retorna_erro_no_contrato():
    respx.get(f"{BASE_URL}/organization_show").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": False,
                "error": {"__type": "Authorization Error", "message": "Access denied"},
            },
        )
    )

    _, structured = await mcp.call_tool("obter_organizacao", {"organization_id": "org-privada"})

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert "DADOS_GOV_BR_API_TOKEN" in structured["errors"][0]["message"]
