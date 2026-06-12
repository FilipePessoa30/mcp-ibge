"""Servidor MCP `mcp-rio` (scaffold/planejamento).

Status: apenas a tool `status` está registrada — este módulo existe para que
o pacote seja executável e testável desde já (`uv run mcp-rio`), servindo de
base para as tools descritas em `docs/modules/rio.md`.

Quando as primeiras tools de dados forem implementadas, siga o padrão do
`mcp-ibge` (`tools.<dominio>_tools.register_<dominio>_tools(mcp)`).

Execução:
    python -m mcp_rio.server

Por padrão usa o transporte stdio. O transporte pode ser trocado via a
variável de ambiente `MCP_RIO_TRANSPORT` (ex.: "streamable-http"); host
e porta usados nesse modo são configuráveis via
`MCP_RIO_HOST`/`MCP_RIO_PORT`.

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
    "mcp-rio",
    instructions=(
        "Servidor MCP (em planejamento) para dados abertos da Prefeitura do Rio de Janeiro "
        "(Data.Rio): catálogo de datasets municipais (saúde, educação, mobilidade, etc.) e "
        "indicadores locais. Nenhuma tool de dados está disponível nesta versão (apenas `status`) "
        "— veja docs/modules/rio.md para o roadmap."
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
        "Iniciando mcp-rio (transporte=%s, scaffold)",
        _settings.transport,
    )
    transport = cast("Literal['stdio', 'sse', 'streamable-http']", _settings.transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
