"""Configuração de logging do servidor.

Importante: nunca usar `print()` no projeto. Em modo stdio, stdout é
reservado para o protocolo MCP — todo log deve ir para stderr via `logging`.
"""

from __future__ import annotations

import logging
import sys

from .config import get_settings


def configure_logging() -> None:
    """Configura o logging raiz para emitir em stderr no nível configurado."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        stream=sys.stderr,
        force=True,
    )
