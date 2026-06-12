"""Testes de contrato da tool MCP `status` do `mcp-saude`."""

from __future__ import annotations

import json
from typing import Any

from mcp_saude.server import mcp

ENVELOPE_KEYS = {"ok", "data", "metadata", "warnings", "errors"}
METADATA_KEYS = {"source_name", "source_url", "endpoint", "params", "retrieved_at", "cache_hit"}


def _assert_envelope_contract(structured: dict[str, Any]) -> None:
    assert set(structured) == ENVELOPE_KEYS
    assert isinstance(structured["ok"], bool)
    assert isinstance(structured["warnings"], list)
    assert isinstance(structured["errors"], list)
    assert set(structured["metadata"]) == METADATA_KEYS
    json.dumps(structured)


async def test_status_tool_returns_envelope() -> None:
    _, structured = await mcp.call_tool("status", {})

    _assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["module"] == "mcp-saude"
    assert structured["data"]["status"] == "ok"
    assert structured["data"]["tools_implemented"] == []
    assert (
        structured["metadata"]["source_name"]
        == "Ministério da Saúde - DataSUS"
    )
    assert structured["metadata"]["source_url"] == "https://datasus.saude.gov.br/"
    assert structured["metadata"]["endpoint"] == "status"
    assert structured["metadata"]["params"] == {}
    assert structured["metadata"]["cache_hit"] is False
