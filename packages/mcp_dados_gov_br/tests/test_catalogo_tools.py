"""Testes de contrato das tools MCP de grupos e tags: existência e formato JSON."""

from __future__ import annotations

import httpx
import respx

from mcp_dados_gov_br.config import get_settings
from mcp_dados_gov_br.server import mcp

from .conftest import assert_envelope_contract

BASE_URL = get_settings().api_base_url

CATALOGO_TOOLS = {"listar_grupos", "buscar_tags"}

GROUP_RAW = {
    "id": "grupo-educacao",
    "name": "educacao",
    "title": "Educação",
    "description": "Datasets sobre educação.",
    "package_count": 10,
}


def _ckan_ok(result: object) -> httpx.Response:
    return httpx.Response(200, json={"success": True, "result": result})


async def test_todas_as_tools_de_catalogo_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert CATALOGO_TOOLS.issubset(nomes)


@respx.mock
async def test_listar_grupos_retorna_contrato_json():
    respx.get(f"{BASE_URL}/group_list").mock(return_value=_ckan_ok([GROUP_RAW]))

    _, structured = await mcp.call_tool("listar_grupos", {"limite": 20})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"][0]["name"] == "educacao"


@respx.mock
async def test_buscar_tags_retorna_contrato_json():
    tag_result = {"count": 2, "results": ["saude", {"id": "tag-1", "name": "educacao"}]}
    respx.get(f"{BASE_URL}/tag_search").mock(return_value=_ckan_ok(tag_result))

    _, structured = await mcp.call_tool("buscar_tags", {"query": "edu", "limite": 20})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert [tag["name"] for tag in structured["data"]] == ["saude", "educacao"]
