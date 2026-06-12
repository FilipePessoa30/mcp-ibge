"""Servidor MCP `mcp-bcb` (scaffold/planejamento).

Status: apenas a tool `status` está registrada — este módulo existe para que
o pacote seja executável e testável desde já (`uv run mcp-bcb`), servindo de
base para as tools descritas em `docs/modules/bcb.md`.

Quando as primeiras tools de dados forem implementadas, siga o padrão do
`mcp-ibge` (`tools.<dominio>_tools.register_<dominio>_tools(mcp)`).

Execução:
    python -m mcp_bcb.server

Por padrão usa o transporte stdio. O transporte pode ser trocado via a
variável de ambiente `MCP_BCB_TRANSPORT` (ex.: "streamable-http"); host
e porta usados nesse modo são configuráveis via
`MCP_BCB_HOST`/`MCP_BCB_PORT`.

Importante: nunca usar `print()`. Em modo stdio, stdout é reservado para o
protocolo MCP — todo log vai para stderr via `logging`.
"""

from __future__ import annotations

import logging
import sys
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP

from .config import get_settings
from .tools.status_tools import register_status_tools

_settings = get_settings()

mcp = FastMCP(
    "mcp-bcb",
    instructions=(
        "Servidor MCP (em planejamento) para indicadores econômicos e financeiros do Banco Central "
        "do Brasil: séries temporais do SGS, cotações de câmbio (PTAX) e a taxa Selic. Nenhuma "
        "tool de dados está disponível nesta versão (apenas `status`) — veja docs/modules/bcb.md "
        "para o roadmap."
    ),
    host=_settings.host,
    port=_settings.port,
)

register_status_tools(mcp)


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    logging.basicConfig(
        level=_settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger(__name__).info(
        "Iniciando mcp-bcb (transporte=%s, scaffold)",
        _settings.transport,
    )
    transport = cast("Literal['stdio', 'sse', 'streamable-http']", _settings.transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
