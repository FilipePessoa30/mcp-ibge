"""Configuração central do servidor: URLs base, timeouts e cache.

Todos os valores ajustáveis podem ser sobrescritos por variáveis de ambiente,
o que permite customizar o comportamento sem alterar código (ex.: ao rodar
via Claude Desktop ou Docker).
"""

from __future__ import annotations

import os

# URLs base das APIs públicas do IBGE (sem necessidade de chave de API).
LOCALIDADES_BASE_URL = "https://servicodados.ibge.gov.br/api/v1/localidades"
AGREGADOS_BASE_URL = "https://servicodados.ibge.gov.br/api/v3/agregados"
PROJECOES_BASE_URL = "https://servicodados.ibge.gov.br/api/v1/projecoes"

# Identificação da fonte usada nos metadados de rastreabilidade das respostas.
SOURCE_NAME = "IBGE - Instituto Brasileiro de Geografia e Estatística"

USER_AGENT = "mcp-ibge/0.1 (+https://github.com/your-username/mcp-ibge)"


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _env_bool(name: str, default: bool) -> bool:
    raw = os.environ.get(name)
    if raw is None:
        return default
    return raw.strip().lower() not in {"0", "false", "no", "off"}


# Timeout (em segundos) aplicado a cada requisição HTTP feita às APIs do IBGE.
DEFAULT_TIMEOUT = _env_float("MCP_IBGE_TIMEOUT", 15.0)

# Cache simples em memória (TTL) para reduzir chamadas repetidas às APIs.
CACHE_ENABLED = _env_bool("MCP_IBGE_CACHE_ENABLED", True)
CACHE_TTL_SECONDS = _env_float("MCP_IBGE_CACHE_TTL", 3600.0)
CACHE_MAX_SIZE = _env_int("MCP_IBGE_CACHE_MAX_SIZE", 256)

# Nível de log e transporte do servidor MCP.
LOG_LEVEL = os.environ.get("MCP_IBGE_LOG_LEVEL", "INFO").upper()
TRANSPORT = os.environ.get("MCP_IBGE_TRANSPORT", "stdio")
