"""Contrato padrão de resposta: todo retorno de tool é
`{ok, data, metadata, warnings, errors}`.

Versão simplificada do envelope de `mcp_ibge.schemas.common`, com os campos
de `metadata` exigidos para o scaffold deste módulo (`source_name`,
`source_url`, `endpoint`, `params`, `retrieved_at`, `cache_hit`). Campos
adicionais (`official_source`, `period`, `territorial_level`,
`license_note`, `version`, ...) podem ser acrescentados quando o módulo
ganhar tools de dados reais, seguindo o padrão de `mcp_ibge.schemas.common`.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from ..config import get_settings


class SourceMetadata(BaseModel):
    """Metadados de proveniência de uma resposta."""

    source_name: str
    source_url: str
    endpoint: str
    params: dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime
    cache_hit: bool = False


class ToolWarning(BaseModel):
    """Aviso não fatal associado a uma resposta de tool."""

    message: str
    code: str | None = None


class ToolError(BaseModel):
    """Erro associado a uma resposta de tool, sem stack trace."""

    message: str
    code: str | None = None


class ToolResponse(BaseModel):
    """Envelope padrão retornado por todas as tools, em sucesso ou erro."""

    ok: bool
    data: Any = None
    metadata: SourceMetadata
    warnings: list[ToolWarning] = Field(default_factory=list)
    errors: list[ToolError] = Field(default_factory=list)


def build_metadata(
    *,
    endpoint: str,
    params: dict[str, Any] | None = None,
    cache_hit: bool = False,
) -> SourceMetadata:
    """Monta `SourceMetadata` preenchendo os campos comuns a partir das configurações."""
    settings = get_settings()
    return SourceMetadata(
        source_name=settings.source_name,
        source_url=settings.source_url,
        endpoint=endpoint,
        params=params or {},
        retrieved_at=datetime.now(UTC),
        cache_hit=cache_hit,
    )


def _as_warning(value: str | ToolWarning) -> ToolWarning:
    return value if isinstance(value, ToolWarning) else ToolWarning(message=value)


def _as_error(value: str | ToolError) -> ToolError:
    return value if isinstance(value, ToolError) else ToolError(message=value)


def build_tool_response(
    *,
    ok: bool,
    data: Any,
    metadata: SourceMetadata,
    warnings: Sequence[str | ToolWarning] = (),
    errors: Sequence[str | ToolError] = (),
) -> dict[str, Any]:
    """Monta o envelope padrão `{ok, data, metadata, warnings, errors}`."""
    response = ToolResponse(
        ok=ok,
        data=data,
        metadata=metadata,
        warnings=[_as_warning(item) for item in warnings],
        errors=[_as_error(item) for item in errors],
    )
    return response.model_dump(mode="json")
