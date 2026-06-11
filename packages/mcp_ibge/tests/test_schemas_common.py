"""Testes de serialização dos schemas comuns (`mcp_ibge.schemas.common`)."""

from __future__ import annotations

from datetime import UTC, datetime

from mcp_ibge.schemas.common import (
    SourceMetadata,
    ToolErrorResponse,
    ToolResponse,
    TypedToolResult,
    build_error_response,
    build_response,
)


def test_source_metadata_serializa_retrieved_at_como_iso_string():
    metadata = SourceMetadata(
        source_name="IBGE",
        source_url="https://example.test/regioes",
        endpoint="https://example.test/regioes",
        params={"a": 1},
        retrieved_at=datetime(2026, 6, 10, 12, 0, 0, tzinfo=UTC),
    )

    dumped = metadata.model_dump(mode="json")

    assert dumped["retrieved_at"] == "2026-06-10T12:00:00Z"
    assert dumped["license_note"] is None


def test_source_metadata_aceita_license_note_opcional():
    metadata = SourceMetadata(
        source_name="IBGE",
        source_url="https://example.test/regioes",
        endpoint="https://example.test/regioes",
        params={},
        retrieved_at=datetime.now(UTC),
        license_note="Dados públicos do IBGE.",
    )

    assert metadata.model_dump(mode="json")["license_note"] == "Dados públicos do IBGE."


def test_build_response_monta_envelope_de_sucesso():
    envelope = build_response(
        source_url="https://example.test/regioes",
        endpoint="https://example.test/regioes",
        params={},
        data=[{"id": 1, "sigla": "N", "nome": "Norte"}],
    )

    ToolResponse.model_validate(envelope)
    assert envelope["data"] == [{"id": 1, "sigla": "N", "nome": "Norte"}]
    assert envelope["metadata"]["source_url"] == "https://example.test/regioes"


def test_build_error_response_monta_envelope_de_erro():
    envelope = build_error_response(
        source_url="https://example.test/municipios/0",
        endpoint="https://example.test/municipios/0",
        params={"municipio_id": 0},
        error="não encontrado",
    )

    ToolErrorResponse.model_validate(envelope)
    assert envelope["error"] == "não encontrado"


def test_typed_tool_result_serializa_dados_genericos():
    metadata = SourceMetadata(
        source_name="IBGE",
        source_url="https://example.test/regioes",
        endpoint="https://example.test/regioes",
        params={},
        retrieved_at=datetime.now(UTC),
    )

    result: TypedToolResult[list[dict[str, int]]] = TypedToolResult(
        ok=True,
        data=[{"id": 1}],
        metadata=metadata,
        warnings=["aviso"],
        errors=[],
    )

    dumped = result.model_dump(mode="json")
    assert dumped["ok"] is True
    assert dumped["data"] == [{"id": 1}]
    assert dumped["warnings"] == ["aviso"]
    assert dumped["errors"] == []
