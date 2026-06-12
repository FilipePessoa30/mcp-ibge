"""Tool `status`: health-check do servidor mcp-dados-gov-br.

Tool mínima exigida para todo módulo do mcp-data-br (ver
docs/architecture.md#adding-a-new-module): confirma que o servidor está no ar
e devolve o envelope padrão `{"ok", "data", "metadata", "warnings", "errors"}`
mesmo sem nenhuma tool de dados implementada ainda.
"""

from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from .. import __version__
from ..schemas.common import build_metadata, build_tool_response


def register_status_tools(mcp: FastMCP) -> None:
    """Registra a tool `status` na instância `FastMCP`."""

    @mcp.tool()
    async def status() -> dict[str, Any]:
        """Status do servidor: versão e tools de dados disponíveis (nenhuma ainda)."""
        metadata = build_metadata(endpoint="status")
        return build_tool_response(
            ok=True,
            data={
                "module": "mcp-dados-gov-br",
                "version": __version__,
                "status": "ok",
                "tools_implemented": [],
            },
            metadata=metadata,
        )
