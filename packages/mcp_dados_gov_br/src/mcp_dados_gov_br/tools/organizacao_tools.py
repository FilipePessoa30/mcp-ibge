"""Tools MCP de organizações publicadoras do catálogo dados.gov.br."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.catalog_service import CatalogService
from . import run_typed_tool

_service = CatalogService()


def register_organizacao_tools(mcp: FastMCP) -> None:
    """Registra as tools de organizações na instância FastMCP fornecida."""

    @mcp.tool()
    async def buscar_organizacoes(
        query: Annotated[
            str | None,
            Field(
                description=(
                    "Termo de busca pelo nome/título da organização "
                    '(ex.: "ministério da saúde"). Se omitido, lista as '
                    "organizações cadastradas."
                )
            ),
        ] = None,
        limite: Annotated[
            int, Field(description="Número máximo de organizações retornadas.", ge=1, le=100)
        ] = 10,
    ) -> dict[str, Any]:
        """Busca ou lista organizações publicadoras de dados.

        Com `query`, usa `organization_autocomplete` para buscar por
        nome/título. Sem `query`, usa `organization_list` para listar as
        organizações cadastradas no catálogo (com metadados completos). Cada
        item retornado inclui `id`, `name`, `title` e, quando disponível,
        `description` e `package_count`.
        """
        return await run_typed_tool(_service.buscar_organizacoes(query, limite=limite))

    @mcp.tool()
    async def obter_organizacao(
        organization_id: Annotated[
            str, Field(description="ID ou nome (slug) da organização no dados.gov.br.")
        ],
    ) -> dict[str, Any]:
        """Obtém detalhes de uma organização publicadora.

        Consulta `organization_show` e retorna `id`, `name`, `title`,
        `description`, `image_url` e `package_count`. Use `organization_id`
        retornado por `buscar_organizacoes` ou pelo campo `organization` de
        um dataset (`buscar_datasets`/`obter_dataset`).
        """
        return await run_typed_tool(_service.obter_organizacao(organization_id))
