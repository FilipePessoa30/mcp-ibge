"""Configuração central do servidor (scaffold).

Segue o mesmo padrão do `mcp-ibge`/`mcp-inep`
(`pydantic-settings`, prefixo de variável de ambiente próprio,
`get_settings()` cacheado). Nenhum cliente HTTP implementado ainda — ver
`docs/modules/tesouro.md` para o roadmap.

Todos os valores são ajustáveis via variáveis de ambiente com prefixo
``MCP_TESOURO_`` (ou um arquivo ``.env`` na raiz do projeto).
"""

from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict

# Domínios oficiais permitidos para requisições do mcp-tesouro. Vazio por
# enquanto: nenhum cliente HTTP foi implementado ainda. Será preenchido
# quando as fontes de dados forem confirmadas — ver "Fontes planejadas" em
# `docs/modules/tesouro.md`.
ALLOWED_API_HOSTS: frozenset[str] = frozenset()


class Settings(BaseSettings):
    """Configurações do servidor, lidas de variáveis de ambiente / `.env`."""

    model_config = SettingsConfigDict(
        env_prefix="MCP_TESOURO_", env_file=".env", extra="ignore"
    )

    # Logging e transporte do servidor MCP (mesma convenção do mcp-ibge).
    log_level: str = "INFO"
    transport: str = "stdio"

    # Host/porta usados quando `transport` é "streamable-http" (ignorados em
    # "stdio").
    host: str = "127.0.0.1"
    port: int = 8000

    # Fonte oficial referenciada por `metadata` da tool `status` (e, no
    # futuro, pelas demais tools deste módulo).
    source_name: str = "Tesouro Nacional - Tesouro Transparente"
    source_url: str = "https://www.tesourotransparente.gov.br/"


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância (cacheada) de `Settings`."""
    return Settings()
