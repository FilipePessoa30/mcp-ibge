"""Testes de inicialização do servidor `mcp-dados-gov-br`."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_dados_gov_br.server import mcp

EXPECTED_TOOLS = {
    "status",
    "buscar_datasets",
    "obter_dataset",
    "listar_recursos_dataset",
    "sugerir_datasets_para_pergunta",
    "buscar_organizacoes",
    "obter_organizacao",
    "listar_grupos",
    "buscar_tags",
}


def test_mcp_instance() -> None:
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "mcp-dados-gov-br"


async def test_todas_as_tools_estao_registradas() -> None:
    tools = await mcp.list_tools()
    assert {tool.name for tool in tools} == EXPECTED_TOOLS
