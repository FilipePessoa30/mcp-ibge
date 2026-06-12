"""Cliente "fino" para as ações CKAN do catálogo do dados.gov.br.

Documentação oficial da API CKAN (Action API):
<https://docs.ckan.org/en/latest/api/>

Cada método mapeia diretamente uma ação `GET <api_base_url>/<action>` e
preserva o JSON bruto retornado em `CkanResult.data`. Conversões para os
schemas tipados (`Dataset`, `Organization`, ...) ficam em
`mcp_dados_gov_br.services.catalog_service`.
"""

from __future__ import annotations

from .base import AsyncCkanClient, CkanResult

__all__ = ["CatalogClient"]


class CatalogClient(AsyncCkanClient):
    """Cliente HTTP para as ações de catálogo (datasets, organizações, grupos, tags)."""

    async def package_search(self, query: str, rows: int) -> CkanResult:
        """`package_search` — busca datasets por texto livre.

        Retorna `result = {"count": int, "results": [...]}`.
        """
        return await self.call_action("package_search", {"q": query, "rows": rows})

    async def package_show(self, dataset_id: str) -> CkanResult:
        """`package_show` — detalhes completos de um dataset (incluindo `resources`)."""
        return await self.call_action("package_show", {"id": dataset_id})

    async def organization_list(self, limit: int) -> CkanResult:
        """`organization_list` — lista organizações cadastradas (com metadados completos).

        Retorna `result = [...]` (lista de organizações).
        """
        return await self.call_action(
            "organization_list", {"all_fields": "true", "limit": limit}
        )

    async def organization_autocomplete(self, query: str, limit: int) -> CkanResult:
        """`organization_autocomplete` — busca organizações por nome/título.

        Retorna `result = [{"id", "name", "title"}, ...]`.
        """
        return await self.call_action("organization_autocomplete", {"q": query, "limit": limit})

    async def organization_show(self, organization_id: str) -> CkanResult:
        """`organization_show` — detalhes de uma organização (sem listar seus datasets)."""
        return await self.call_action(
            "organization_show", {"id": organization_id, "include_datasets": "false"}
        )

    async def group_list(self, limit: int) -> CkanResult:
        """`group_list` — lista grupos temáticos cadastrados (com metadados completos).

        Retorna `result = [...]` (lista de grupos).
        """
        return await self.call_action("group_list", {"all_fields": "true", "limit": limit})

    async def tag_search(self, query: str, limit: int) -> CkanResult:
        """`tag_search` — busca tags cujo nome contenha `query`.

        Retorna `result = {"count": int, "results": [...]}`.
        """
        return await self.call_action("tag_search", {"query": query, "limit": limit})
