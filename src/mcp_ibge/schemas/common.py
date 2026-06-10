"""Envelope de resposta padrão: todo retorno de tool inclui metadados de fonte.

Isso garante rastreabilidade (source_name, source_url, retrieved_at, endpoint
e params) para qualquer dado retornado por este servidor.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from ..config import get_settings

T = TypeVar("T")


class SourceMetadata(BaseModel):
    """Metadados de proveniência de uma resposta."""

    source_name: str
    source_url: str
    endpoint: str
    params: dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime
    license_note: str | None = None


class ToolResponse(BaseModel):
    """Envelope retornado por todas as tools em caso de sucesso."""

    metadata: SourceMetadata
    data: Any


class ToolErrorResponse(BaseModel):
    """Envelope retornado por todas as tools em caso de erro."""

    metadata: SourceMetadata
    error: str


class TypedToolResult(BaseModel, Generic[T]):
    """Envelope tipado e genérico para dados convertidos em schemas Pydantic.

    Diferente de `ToolResponse`/`ToolErrorResponse` (o envelope MCP montado por
    `build_response`/`build_error_response` e usado por `tools/__init__.py`),
    este modelo serve para representar resultados já convertidos em schemas
    tipados (`Region`, `State`, `Municipality`, ...) com avisos/erros não
    fatais agregados — útil para conversões internas e testes.
    """

    ok: bool
    data: T
    metadata: SourceMetadata
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def _build_metadata(
    *, source_url: str, endpoint: str, params: dict[str, Any] | None
) -> SourceMetadata:
    return SourceMetadata(
        source_name=get_settings().source_name,
        source_url=source_url,
        retrieved_at=datetime.now(UTC),
        endpoint=endpoint,
        params=params or {},
    )


def build_response(
    *,
    source_url: str,
    endpoint: str,
    params: dict[str, Any] | None,
    data: Any,
) -> dict[str, Any]:
    """Monta o envelope de sucesso `{metadata, data}`."""
    metadata = _build_metadata(source_url=source_url, endpoint=endpoint, params=params)
    return ToolResponse(metadata=metadata, data=data).model_dump(mode="json")


def build_error_response(
    *,
    source_url: str,
    endpoint: str,
    params: dict[str, Any] | None,
    error: str,
) -> dict[str, Any]:
    """Monta o envelope de erro `{metadata, error}`."""
    metadata = _build_metadata(source_url=source_url, endpoint=endpoint, params=params)
    return ToolErrorResponse(metadata=metadata, error=error).model_dump(mode="json")
