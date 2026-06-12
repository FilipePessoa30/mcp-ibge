"""Fixtures compartilhadas pelos testes do `mcp-dados-gov-br`."""

from __future__ import annotations

import json
from typing import Any

import pytest

from mcp_dados_gov_br.utils.cache import clear_cache

ENVELOPE_KEYS = {"ok", "data", "metadata", "warnings", "errors"}
METADATA_KEYS = {"source_name", "source_url", "endpoint", "params", "retrieved_at", "cache_hit"}


@pytest.fixture(autouse=True)
def _isolar_cache():
    """Garante que o cache em memória não vaze entre testes."""
    clear_cache()
    yield
    clear_cache()


def assert_envelope_contract(structured: dict[str, Any]) -> None:
    """Garante que `structured` segue o contrato padrão `{ok, data, metadata, warnings, errors}`."""
    assert isinstance(structured, dict)
    assert set(structured) == ENVELOPE_KEYS
    assert isinstance(structured["ok"], bool)
    assert isinstance(structured["warnings"], list)
    assert isinstance(structured["errors"], list)
    assert set(structured["metadata"]) == METADATA_KEYS
    assert isinstance(structured["metadata"]["params"], dict)
    assert isinstance(structured["metadata"]["cache_hit"], bool)
    json.dumps(structured)
