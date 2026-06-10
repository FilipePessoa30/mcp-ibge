"""Servidor MCP `mcp-ibge`.

Wireup: cria a instância `FastMCP` e registra as tools de cada domínio
(`tools.localidades_tools`, `tools.agregados_tools`, ...).

Execução:
    python -m mcp_ibge.server

Por padrão usa o transporte stdio (recomendado para Claude Desktop, Cursor e
demais clientes MCP locais). O transporte pode ser trocado via a variável de
ambiente `MCP_IBGE_TRANSPORT` (ex.: "streamable-http").

Importante: nunca usar `print()`. Em modo stdio, stdout é reservado para o
protocolo MCP — todo log vai para stderr via `logging`.
"""

from __future__ import annotations

import logging

from mcp.server.fastmcp import FastMCP

from .config import get_settings
from .logging_config import configure_logging
from .tools import agregados_tools, localidades_tools

mcp = FastMCP(
    "mcp-ibge",
    instructions=(
        "Servidor MCP para consultar dados públicos e oficiais do IBGE: "
        "localidades (regiões, estados, municípios e seus códigos), agregados "
        "estatísticos do SIDRA (com metadados de variáveis e períodos) e "
        "indicadores de população. Toda resposta inclui metadados de fonte "
        "(source_name, source_url, retrieved_at, endpoint, params) para "
        "rastreabilidade."
    ),
)

localidades_tools.register_localidades_tools(mcp)
agregados_tools.register(mcp)


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    configure_logging()
    settings = get_settings()
    logging.getLogger(__name__).info("Iniciando mcp-ibge (transporte=%s)", settings.transport)
    mcp.run(transport=settings.transport)


if __name__ == "__main__":
    main()
