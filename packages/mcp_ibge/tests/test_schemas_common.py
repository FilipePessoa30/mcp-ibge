"""Testes de serialização dos schemas comuns (`mcp_ibge.schemas.common`)."""

from __future__ import annotations

from datetime import UTC, datetime

from mcp_ibge.config import get_settings
from mcp_ibge.schemas.common import (
    SourceMetadata,
    ToolError,
    ToolResponse,
    ToolWarning,
    TypedToolResult,
    build_metadata,
    build_tool_response,
    get_package_version,
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
    assert dumped["period"] is None
    assert dumped["territorial_level"] is None
    assert dumped["cache_hit"] is False
    assert dumped["official_source"]
    assert dumped["version"]


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


def test_build_metadata_preenche_campos_a_partir_das_configuracoes():
    settings = get_settings()

    metadata = build_metadata(
        source_url="https://example.test/regioes",
        endpoint="https://example.test/regioes",
        params={"a": 1},
        period="2024",
        territorial_level="N6",
        cache_hit=True,
    )

    assert metadata.source_name == settings.source_name
    assert metadata.official_source == settings.official_source_url
    assert metadata.license_note == settings.license_note
    assert metadata.version == get_package_version()
    assert metadata.period == "2024"
    assert metadata.territorial_level == "N6"
    assert metadata.cache_hit is True
    assert metadata.params == {"a": 1}


def test_build_tool_response_envelope_de_sucesso():
    metadata = build_metadata(source_url="https://example.test/regioes", endpoint="x")

    envelope = build_tool_response(
        ok=True,
        data=[{"id": 1, "sigla": "N", "nome": "Norte"}],
        metadata=metadata,
    )

    ToolResponse.model_validate(envelope)
    assert envelope["ok"] is True
    assert envelope["data"] == [{"id": 1, "sigla": "N", "nome": "Norte"}]
    assert envelope["warnings"] == []
    assert envelope["errors"] == []
    assert envelope["metadata"]["source_url"] == "https://example.test/regioes"


def test_build_tool_response_envelope_de_erro_converte_strings():
    metadata = build_metadata(source_url="https://example.test/municipios/0", endpoint="x")

    envelope = build_tool_response(
        ok=False,
        data=None,
        metadata=metadata,
        warnings=["aviso"],
        errors=["não encontrado"],
    )

    ToolResponse.model_validate(envelope)
    assert envelope["ok"] is False
    assert envelope["data"] is None
    assert envelope["warnings"] == [{"message": "aviso", "code": None}]
    assert envelope["errors"] == [{"message": "não encontrado", "code": None}]


def test_build_tool_response_aceita_tool_warning_e_tool_error():
    metadata = build_metadata(source_url="https://example.test/regioes", endpoint="x")

    envelope = build_tool_response(
        ok=False,
        data=None,
        metadata=metadata,
        warnings=[ToolWarning(message="aviso", code="AMBIGUOUS")],
        errors=[ToolError(message="erro", code="NOT_FOUND")],
    )

    assert envelope["warnings"] == [{"message": "aviso", "code": "AMBIGUOUS"}]
    assert envelope["errors"] == [{"message": "erro", "code": "NOT_FOUND"}]


def test_typed_tool_result_serializa_dados_genericos():
    metadata = build_metadata(source_url="https://example.test/regioes", endpoint="x")

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
