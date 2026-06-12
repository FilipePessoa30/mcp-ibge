"""Configuração central do servidor `mcp-dados-gov-br`.

Segue o mesmo padrão do `mcp-ibge` (`pydantic-settings`, allowlist de
domínios em `ALLOWED_API_HOSTS`, cache TTL compartilhado). A maioria das
variáveis de ambiente usa o prefixo `MCP_DADOS_GOV_BR_`, mas algumas seguem
convenções próprias:

- `DADOS_GOV_BR_API_BASE_URL` / `DADOS_GOV_BR_API_TOKEN`: nomes específicos
  do Portal Brasileiro de Dados Abertos (sem prefixo `MCP_`), com fallback
  para `MCP_DADOS_GOV_BR_API_BASE_URL` / `MCP_DADOS_GOV_BR_API_TOKEN`.
- `MCP_DATA_BR_REQUEST_TIMEOUT`, `MCP_DATA_BR_ENABLE_CACHE`,
  `MCP_DATA_BR_CACHE_TTL_SECONDS`: compartilhadas entre módulos do
  mcp-data-br (mesma convenção usada pelo `mcp-ibge`).
"""

from __future__ import annotations

from functools import lru_cache
from urllib.parse import urlparse

from pydantic import AliasChoices, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Domínio oficial do Portal Brasileiro de Dados Abertos (API CKAN).
# `api_base_url` é validado contra esta lista — qualquer outro domínio (ou
# esquema diferente de "https") é rejeitado na inicialização.
ALLOWED_API_HOSTS: frozenset[str] = frozenset({"dados.gov.br"})


class Settings(BaseSettings):
    """Configurações do servidor, lidas de variáveis de ambiente / `.env`."""

    model_config = SettingsConfigDict(
        env_prefix="MCP_DADOS_GOV_BR_", env_file=".env", extra="ignore"
    )

    # URL base da API CKAN do dados.gov.br. Cada tool acrescenta a ação CKAN
    # (ex.: "/package_search", "/package_show") a esta URL. Restrita a
    # `ALLOWED_API_HOSTS`.
    api_base_url: str = Field(
        default="https://dados.gov.br/api/3/action",
        validation_alias=AliasChoices(
            "DADOS_GOV_BR_API_BASE_URL", "MCP_DADOS_GOV_BR_API_BASE_URL"
        ),
    )

    # Token de consumidor (API key) do dados.gov.br, enviado no header
    # `Authorization` quando configurado. A maioria das consultas de leitura
    # (busca de datasets, organizações, grupos, tags) funciona sem token;
    # algumas organizações/datasets podem exigi-lo.
    api_token: SecretStr | None = Field(
        default=None,
        validation_alias=AliasChoices("DADOS_GOV_BR_API_TOKEN", "MCP_DADOS_GOV_BR_API_TOKEN"),
    )

    # Timeout (em segundos) aplicado a cada requisição HTTP à API do
    # dados.gov.br. Compartilhado entre módulos via `MCP_DATA_BR_REQUEST_TIMEOUT`.
    timeout: float = Field(
        default=30.0,
        validation_alias=AliasChoices(
            "MCP_DATA_BR_REQUEST_TIMEOUT", "MCP_DADOS_GOV_BR_REQUEST_TIMEOUT"
        ),
    )

    # Tamanho máximo (em bytes) aceito para o corpo de uma resposta da API.
    # Respostas maiores são abortadas e tratadas como erro de servidor.
    max_response_size_bytes: int = 5_000_000

    # Cache simples em memória (TTL) para reduzir chamadas repetidas à API.
    # Aceita tanto os nomes compartilhados entre módulos do mcp-data-br
    # (`MCP_DATA_BR_ENABLE_CACHE`, `MCP_DATA_BR_CACHE_TTL_SECONDS`) quanto os
    # nomes específicos deste módulo. Quando ambos são definidos, o prefixo
    # `MCP_DATA_BR_` tem precedência.
    cache_enabled: bool = Field(
        default=True,
        validation_alias=AliasChoices(
            "MCP_DATA_BR_ENABLE_CACHE", "MCP_DADOS_GOV_BR_CACHE_ENABLED"
        ),
    )
    cache_ttl_seconds: float = Field(
        default=3600.0,
        validation_alias=AliasChoices(
            "MCP_DATA_BR_CACHE_TTL_SECONDS", "MCP_DADOS_GOV_BR_CACHE_TTL_SECONDS"
        ),
    )
    cache_max_size: int = 256

    # Logging e transporte do servidor MCP (mesma convenção do mcp-ibge).
    log_level: str = Field(
        default="INFO",
        validation_alias=AliasChoices("MCP_DATA_BR_LOG_LEVEL", "MCP_DADOS_GOV_BR_LOG_LEVEL"),
    )
    transport: str = "stdio"

    # Host/porta usados quando `transport` é "streamable-http" (ignorados em
    # "stdio").
    host: str = "127.0.0.1"
    port: int = 8000

    # Fonte oficial referenciada por `metadata` de toda tool deste módulo.
    source_name: str = "dados.gov.br - Portal Brasileiro de Dados Abertos"
    source_url: str = "https://dados.gov.br/"

    @field_validator("api_base_url")
    @classmethod
    def _validar_api_base_url(cls, value: str) -> str:
        """Garante que `api_base_url` aponta para o domínio oficial via HTTPS."""
        parsed = urlparse(value)
        if parsed.scheme != "https" or parsed.hostname not in ALLOWED_API_HOSTS:
            dominios = ", ".join(sorted(ALLOWED_API_HOSTS))
            raise ValueError(
                f'DADOS_GOV_BR_API_BASE_URL inválida: "{value}". Deve ser uma URL '
                f"https para um domínio oficial do Portal de Dados Abertos ({dominios})."
            )
        return value


@lru_cache
def get_settings() -> Settings:
    """Retorna a instância (cacheada) de `Settings`."""
    return Settings()
