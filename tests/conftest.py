"""Fixtures compartilhadas pelos testes."""

from __future__ import annotations

import pytest

from mcp_ibge.http_client import clear_cache


@pytest.fixture(autouse=True)
def _isolar_cache():
    """Garante que o cache em memória não vaze entre testes."""
    clear_cache()
    yield
    clear_cache()
