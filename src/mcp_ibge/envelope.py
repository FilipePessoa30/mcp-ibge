"""Envelope de resposta padrão: todo retorno de tool inclui metadados de fonte.

Isso garante rastreabilidade (source_name, source_url, retrieved_at, endpoint
e params) para qualquer dado retornado por este servidor, conforme exigido
pelo projeto.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from .config import SOURCE_NAME


class SourceMetadata(BaseModel):
    """Metadados de proveniência de uma resposta."""

    source_name: str = SOURCE_NAME
    source_url: str
    retrieved_at: str
    endpoint: str
    params: dict[str, Any] = Field(default_factory=dict)


class ToolResponse(BaseModel):
    """Envelope retornado por todas as tools em caso de sucesso."""

    metadata: SourceMetadata
    data: Any


class ToolErrorResponse(BaseModel):
    """Envelope retornado por todas as tools em caso de erro."""

    metadata: SourceMetadata
    error: str


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def build_response(
    *,
    source_url: str,
    endpoint: str,
    params: dict[str, Any] | None,
    data: Any,
) -> dict[str, Any]:
    """Monta o envelope de sucesso `{metadata, data}`."""
    metadata = SourceMetadata(
        source_url=source_url,
        retrieved_at=_now_iso(),
        endpoint=endpoint,
        params=params or {},
    )
    return ToolResponse(metadata=metadata, data=data).model_dump(mode="json")


def build_error_response(
    *,
    source_url: str,
    endpoint: str,
    params: dict[str, Any] | None,
    error: str,
) -> dict[str, Any]:
    """Monta o envelope de erro `{metadata, error}`."""
    metadata = SourceMetadata(
        source_url=source_url,
        retrieved_at=_now_iso(),
        endpoint=endpoint,
        params=params or {},
    )
    return ToolErrorResponse(metadata=metadata, error=error).model_dump(mode="json")
