"""Contrato padrão de resposta: todo retorno de tool é `{ok, data, metadata, warnings, errors}`.

Isso garante rastreabilidade (`source_name`, `source_url`, `official_source`,
`endpoint`, `params`, `retrieved_at`, `period`, `territorial_level`,
`license_note`, `version`, `cache_hit`) para qualquer dado retornado por este
servidor, e um formato único e serializável em JSON tanto para sucesso quanto
para erro.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime
from functools import lru_cache
from importlib.metadata import PackageNotFoundError
from importlib.metadata import version as _installed_version
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

from ..config import get_settings

T = TypeVar("T")

_DEFAULT_OFFICIAL_SOURCE = "https://www.ibge.gov.br/"


@lru_cache
def get_package_version() -> str:
    """Retorna a versão instalada do pacote `mcp-ibge` (ou "0.0.0" se desconhecida)."""
    try:
        return _installed_version("mcp-ibge")
    except PackageNotFoundError:  # pragma: no cover - apenas em ambientes não instalados
        return "0.0.0"


class SourceMetadata(BaseModel):
    """Metadados de proveniência de uma resposta."""

    source_name: str
    source_url: str
    official_source: str = _DEFAULT_OFFICIAL_SOURCE
    endpoint: str
    params: dict[str, Any] = Field(default_factory=dict)
    retrieved_at: datetime
    period: str | None = None
    territorial_level: str | None = None
    license_note: str | None = None
    version: str = Field(default_factory=get_package_version)
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


class TypedToolResult(BaseModel, Generic[T]):
    """Envelope tipado e genérico para dados convertidos em schemas Pydantic.

    Usado internamente pelas camadas de serviço para representar resultados já
    convertidos em schemas tipados (`Region`, `State`, `Municipality`, ...)
    com avisos/erros não fatais agregados. `tools/__init__.run_typed_tool`
    converte este modelo no envelope público `ToolResponse`.
    """

    ok: bool
    data: T
    metadata: SourceMetadata
    warnings: list[str] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)


def build_metadata(
    *,
    source_url: str,
    endpoint: str,
    params: dict[str, Any] | None = None,
    period: str | None = None,
    territorial_level: str | None = None,
    cache_hit: bool = False,
) -> SourceMetadata:
    """Monta `SourceMetadata` preenchendo os campos comuns a partir das configurações."""
    settings = get_settings()
    return SourceMetadata(
        source_name=settings.source_name,
        source_url=source_url,
        official_source=settings.official_source_url,
        endpoint=endpoint,
        params=params or {},
        retrieved_at=datetime.now(UTC),
        period=period,
        territorial_level=territorial_level,
        license_note=settings.license_note,
        version=get_package_version(),
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
