"""Tools MCP de grupos temáticos e tags do catálogo dados.gov.br."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.catalog_service import CatalogService
from . import run_typed_tool

_service = CatalogService()


def register_catalogo_tools(mcp: FastMCP) -> None:
    """Registra as tools de grupos e tags na instância FastMCP fornecida."""

    @mcp.tool()
    async def listar_grupos(
        limite: Annotated[
            int, Field(description="Número máximo de grupos retornados.", ge=1, le=100)
        ] = 20,
    ) -> dict[str, Any]:
        """Lista grupos temáticos disponíveis no catálogo.

        Consulta `group_list` (com metadados completos) e retorna até
        `limite` grupos, cada um com `id`, `name`, `title`, `description` e
        `package_count`. Útil para descobrir como os datasets do dados.gov.br
        são organizados por tema (ex.: "saúde", "educação", "meio-ambiente").
        """
        return await run_typed_tool(_service.listar_grupos(limite=limite))

    @mcp.tool()
    async def buscar_tags(
        query: Annotated[
            str, Field(description='Termo de busca pelo nome da tag (ex.: "saude", "censo").')
        ],
        limite: Annotated[
            int, Field(description="Número máximo de tags retornadas.", ge=1, le=100)
        ] = 20,
    ) -> dict[str, Any]:
        """Busca tags relacionadas a datasets públicos.

        Consulta `tag_search` e retorna até `limite` tags cujo nome contenha
        `query`. Use os nomes retornados como pistas de termos relacionados
        para refinar uma chamada a `buscar_datasets`.
        """
        return await run_typed_tool(_service.buscar_tags(query, limite=limite))
