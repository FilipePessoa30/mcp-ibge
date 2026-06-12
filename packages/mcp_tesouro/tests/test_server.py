"""Testes do scaffold do `mcp-tesouro`.

Cobre o que existe nesta versão: o servidor inicializa com a instância
`FastMCP` e apenas a tool `status` registrada. Os testes das tools de dados
planejadas (ver `docs/modules/tesouro.md`) serão adicionados junto com cada
implementação.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from mcp_tesouro.server import mcp


def test_mcp_instance() -> None:
    assert isinstance(mcp, FastMCP)
    assert mcp.name == "mcp-tesouro"


async def test_only_status_tool_registered() -> None:
    tools = await mcp.list_tools()
    assert [tool.name for tool in tools] == ["status"]
