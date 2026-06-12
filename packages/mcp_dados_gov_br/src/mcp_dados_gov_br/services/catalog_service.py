"""Regras de negócio do catálogo de dados abertos: busca, detalhes e sugestões.

Esta camada usa `CatalogClient` para falar com a API CKAN do dados.gov.br e
os schemas de `mcp_dados_gov_br.schemas.catalog` para devolver dados
tipados e rastreáveis (`TypedToolResult`) às tools MCP. Nenhum dataset,
organização, grupo ou tag é inventado: toda lista vem diretamente de uma
resposta da API.
"""

from __future__ import annotations

from typing import Any

from ..clients.catalog import CatalogClient
from ..schemas.catalog import (
    Dataset,
    DatasetSummary,
    Group,
    Organization,
    Resource,
    Tag,
    dataset_from_raw,
    dataset_summary_from_raw,
    group_from_raw,
    organization_from_raw,
    tag_from_raw,
)
from ..schemas.common import SourceMetadata, TypedToolResult, build_metadata
from ..utils.errors import CkanClientError
from ..utils.keywords import extract_keywords
from ..utils.validators import validate_limit, validate_non_empty


def _metadata(*, endpoint: str, params: dict[str, Any], cache_hit: bool = False) -> SourceMetadata:
    return build_metadata(endpoint=endpoint, params=params, cache_hit=cache_hit)


class CatalogService:
    """Operações de alto nível sobre datasets, organizações, grupos e tags."""

    def __init__(self, client: CatalogClient | None = None) -> None:
        self._client = client or CatalogClient()

    async def buscar_datasets(
        self, query: str, limite: int = 10
    ) -> TypedToolResult[list[DatasetSummary]]:
        """Busca datasets públicos por texto livre (`package_search`)."""
        params: dict[str, Any] = {"query": query, "limite": limite}
        try:
            limite = validate_limit(limite, url=f"{self._client.base_url}/package_search")
            texto = validate_non_empty(
                query, field_name="query", url=f"{self._client.base_url}/package_search"
            )
            result = await self._client.package_search(texto, limite)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        resultados = result.data.get("results", []) if isinstance(result.data, dict) else []
        datasets = [dataset_summary_from_raw(item) for item in resultados]
        return TypedToolResult(
            ok=True,
            data=datasets,
            metadata=_metadata(
                endpoint=result.endpoint,
                params={"q": texto, "rows": limite},
                cache_hit=result.cache_hit,
            ),
        )

    async def obter_dataset(self, dataset_id: str) -> TypedToolResult[Dataset | None]:
        """Obtém os detalhes completos de um dataset (`package_show`)."""
        params: dict[str, Any] = {"dataset_id": dataset_id}
        try:
            id_normalizado = validate_non_empty(
                dataset_id, field_name="dataset_id", url=f"{self._client.base_url}/package_show"
            )
            result = await self._client.package_show(id_normalizado)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        return TypedToolResult(
            ok=True,
            data=dataset_from_raw(result.data),
            metadata=_metadata(
                endpoint=result.endpoint, params=result.params, cache_hit=result.cache_hit
            ),
        )

    async def listar_recursos_dataset(self, dataset_id: str) -> TypedToolResult[list[Resource]]:
        """Lista os recursos (CSV, JSON, API, PDF, XLSX, ...) de um dataset."""
        params: dict[str, Any] = {"dataset_id": dataset_id}
        try:
            id_normalizado = validate_non_empty(
                dataset_id, field_name="dataset_id", url=f"{self._client.base_url}/package_show"
            )
            result = await self._client.package_show(id_normalizado)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        dataset = dataset_from_raw(result.data)
        return TypedToolResult(
            ok=True,
            data=dataset.resources,
            metadata=_metadata(
                endpoint=result.endpoint, params=result.params, cache_hit=result.cache_hit
            ),
        )

    async def buscar_organizacoes(
        self, query: str | None = None, limite: int = 10
    ) -> TypedToolResult[list[Organization]]:
        """Busca organizações por nome/título, ou lista as cadastradas se `query` for omitido."""
        params: dict[str, Any] = {"query": query, "limite": limite}
        try:
            limite = validate_limit(limite, url=f"{self._client.base_url}/organization_list")
            texto = query.strip() if query and query.strip() else None
            if texto:
                result = await self._client.organization_autocomplete(texto, limite)
                action = "organization_autocomplete"
                call_params: dict[str, Any] = {"q": texto, "limit": limite}
            else:
                result = await self._client.organization_list(limite)
                action = "organization_list"
                call_params = {"all_fields": "true", "limit": limite}
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        itens = result.data if isinstance(result.data, list) else []
        organizacoes = [organization_from_raw(item) for item in itens]
        return TypedToolResult(
            ok=True,
            data=organizacoes,
            metadata=_metadata(
                endpoint=f"{self._client.base_url}/{action}",
                params=call_params,
                cache_hit=result.cache_hit,
            ),
        )

    async def obter_organizacao(self, organization_id: str) -> TypedToolResult[Organization | None]:
        """Obtém os detalhes de uma organização publicadora (`organization_show`)."""
        params: dict[str, Any] = {"organization_id": organization_id}
        try:
            id_normalizado = validate_non_empty(
                organization_id,
                field_name="organization_id",
                url=f"{self._client.base_url}/organization_show",
            )
            result = await self._client.organization_show(id_normalizado)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        return TypedToolResult(
            ok=True,
            data=organization_from_raw(result.data),
            metadata=_metadata(
                endpoint=result.endpoint, params=result.params, cache_hit=result.cache_hit
            ),
        )

    async def listar_grupos(self, limite: int = 20) -> TypedToolResult[list[Group]]:
        """Lista os grupos temáticos disponíveis no catálogo (`group_list`)."""
        params: dict[str, Any] = {"limite": limite}
        try:
            limite = validate_limit(limite, url=f"{self._client.base_url}/group_list")
            result = await self._client.group_list(limite)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        itens = result.data if isinstance(result.data, list) else []
        grupos = [group_from_raw(item) for item in itens]
        return TypedToolResult(
            ok=True,
            data=grupos,
            metadata=_metadata(
                endpoint=result.endpoint,
                params={"all_fields": "true", "limit": limite},
                cache_hit=result.cache_hit,
            ),
        )

    async def buscar_tags(self, query: str, limite: int = 20) -> TypedToolResult[list[Tag]]:
        """Busca tags relacionadas a datasets públicos (`tag_search`)."""
        params: dict[str, Any] = {"query": query, "limite": limite}
        try:
            limite = validate_limit(limite, url=f"{self._client.base_url}/tag_search")
            texto = validate_non_empty(
                query, field_name="query", url=f"{self._client.base_url}/tag_search"
            )
            result = await self._client.tag_search(texto, limite)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        resultados = result.data.get("results", []) if isinstance(result.data, dict) else []
        tags = [tag_from_raw(item) for item in resultados]
        return TypedToolResult(
            ok=True,
            data=tags,
            metadata=_metadata(
                endpoint=result.endpoint,
                params={"query": texto, "limit": limite},
                cache_hit=result.cache_hit,
            ),
        )

    async def sugerir_datasets_para_pergunta(
        self, pergunta: str, limite: int = 5
    ) -> TypedToolResult[list[DatasetSummary]]:
        """Sugere datasets para uma pergunta em linguagem natural.

        Extrai palavras-chave de `pergunta` (tokenização + remoção de
        stopwords em português, sem nenhum modelo de linguagem) e usa
        `package_search` com essas palavras-chave como consulta textual. As
        palavras-chave usadas ficam em `metadata.params["keywords"]` para
        rastreabilidade.
        """
        params: dict[str, Any] = {"pergunta": pergunta, "limite": limite}
        endpoint = f"{self._client.base_url}/package_search"
        try:
            limite = validate_limit(limite, url=endpoint)
            texto = validate_non_empty(pergunta, field_name="pergunta", url=endpoint)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        keywords = extract_keywords(texto)
        if not keywords:
            return TypedToolResult(
                ok=True,
                data=[],
                metadata=_metadata(endpoint=endpoint, params={"pergunta": texto, "keywords": []}),
                warnings=[
                    "Não foi possível extrair palavras-chave da pergunta; "
                    "nenhuma sugestão de dataset foi feita."
                ],
            )

        consulta = " ".join(keywords)
        try:
            result = await self._client.package_search(consulta, limite)
        except CkanClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(
                    endpoint=exc.url, params={**params, "keywords": keywords, "q": consulta}
                ),
                errors=[str(exc)],
            )

        resultados = result.data.get("results", []) if isinstance(result.data, dict) else []
        datasets = [dataset_summary_from_raw(item) for item in resultados]
        return TypedToolResult(
            ok=True,
            data=datasets,
            metadata=_metadata(
                endpoint=result.endpoint,
                params={"pergunta": texto, "keywords": keywords, "q": consulta, "rows": limite},
                cache_hit=result.cache_hit,
            ),
        )
