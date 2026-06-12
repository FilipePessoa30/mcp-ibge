"""Configuração de logging do servidor.

Importante: nunca usar `print()` no projeto. Em modo stdio, stdout é
reservado para o protocolo MCP — todo log deve ir para stderr via `logging`.

Os logs são emitidos em `stderr` como uma linha JSON por registro
(`JSONFormatter`), facilitando análise por ferramentas de observabilidade
(ex.: `jq`, agregadores de log) sem misturar com o protocolo MCP no `stdout`.
"""

from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime

from .config import get_settings


class JSONFormatter(logging.Formatter):
    """Formata cada registro de log como uma linha JSON única."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "timestamp": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def configure_logging() -> None:
    """Configura o logging raiz para emitir JSON em stderr no nível configurado."""
    settings = get_settings()
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    handler = logging.StreamHandler(stream=sys.stderr)
    handler.setFormatter(JSONFormatter())
    logging.basicConfig(level=level, handlers=[handler], force=True)
