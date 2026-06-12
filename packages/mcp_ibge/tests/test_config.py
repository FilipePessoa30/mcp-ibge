"""Testes da validação de configuração (`mcp_ibge.config.Settings`)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from mcp_ibge.config import Settings


def test_api_base_url_aceita_dominio_oficial():
    settings = Settings(api_base_url="https://servicodados.ibge.gov.br/api")
    assert settings.api_base_url == "https://servicodados.ibge.gov.br/api"


@pytest.mark.parametrize(
    "url",
    [
        "http://servicodados.ibge.gov.br/api",
        "https://evil.example.com/api",
        "https://servicodados.ibge.gov.br.evil.com/api",
        "ftp://servicodados.ibge.gov.br/api",
        "https://localhost/api",
        "not-a-url",
        "",
    ],
)
def test_api_base_url_rejeita_dominios_ou_esquemas_nao_oficiais(url: str):
    with pytest.raises(ValidationError):
        Settings(api_base_url=url)


@pytest.mark.parametrize(
    ("env_var", "valor", "campo", "esperado"),
    [
        ("MCP_DATA_BR_ENABLE_CACHE", "false", "cache_enabled", False),
        ("MCP_DATA_BR_CACHE_TTL_SECONDS", "120", "cache_ttl_seconds", 120.0),
        ("MCP_DATA_BR_LOG_LEVEL", "DEBUG", "log_level", "DEBUG"),
        # Nomes legados (`MCP_IBGE_*`), mantidos por compatibilidade.
        ("MCP_IBGE_CACHE_ENABLED", "false", "cache_enabled", False),
        ("MCP_IBGE_CACHE_TTL_SECONDS", "120", "cache_ttl_seconds", 120.0),
        ("MCP_IBGE_LOG_LEVEL", "DEBUG", "log_level", "DEBUG"),
    ],
)
def test_settings_aceita_variaveis_de_cache_e_log(monkeypatch, env_var, valor, campo, esperado):
    monkeypatch.setenv(env_var, valor)
    settings = Settings()
    assert getattr(settings, campo) == esperado


def test_mcp_data_br_prefixo_tem_precedencia_sobre_mcp_ibge(monkeypatch):
    monkeypatch.setenv("MCP_IBGE_CACHE_TTL_SECONDS", "111")
    monkeypatch.setenv("MCP_DATA_BR_CACHE_TTL_SECONDS", "222")

    assert Settings().cache_ttl_seconds == 222.0
