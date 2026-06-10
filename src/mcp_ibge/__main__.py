"""Ponto de entrada do servidor MCP `mcp-ibge`.

Por padrão usa o transporte stdio (recomendado para Claude Desktop, Cursor e
demais clientes MCP locais). O transporte pode ser trocado via a variável de
ambiente `MCP_IBGE_TRANSPORT` (ex.: "streamable-http"), preparando o servidor
para uso remoto no futuro.

Importante: nunca usar `print()` aqui. Em modo stdio, stdout é reservado para
o protocolo MCP — qualquer log deve ir para stderr via `logging`.
"""

from __future__ import annotations

import logging
import sys

from .config import LOG_LEVEL, TRANSPORT
from .server import mcp


def _configure_logging() -> None:
    level = getattr(logging, LOG_LEVEL, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
    )


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    _configure_logging()
    logging.getLogger(__name__).info("Iniciando mcp-ibge (transporte=%s)", TRANSPORT)
    mcp.run(transport=TRANSPORT)


if __name__ == "__main__":
    main()
