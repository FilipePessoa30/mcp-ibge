"""Tools MCP de busca e detalhamento de datasets do catálogo dados.gov.br."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.catalog_service import CatalogService
from . import run_typed_tool

_service = CatalogService()


def register_dataset_tools(mcp: FastMCP) -> None:
    """Registra as tools de datasets na instância FastMCP fornecida."""

    @mcp.tool()
    async def buscar_datasets(
        query: Annotated[
            str, Field(description="Termo de busca (texto livre, ex.: \"educação\", \"covid-19\").")
        ],
        limite: Annotated[
            int, Field(description="Número máximo de datasets retornados.", ge=1, le=100)
        ] = 10,
    ) -> dict[str, Any]:
        """Busca conjuntos de dados públicos no Portal Brasileiro de Dados Abertos.

        Faz uma busca textual (`package_search`) no catálogo dados.gov.br e
        retorna até `limite` datasets correspondentes, cada um com `id`,
        `name`, `title`, `notes`, `organization`, `tags`, `groups` e
        `num_resources`. Não inventa datasets: retorna apenas o que a API
        encontrar (lista vazia se nada corresponder).
        """
        return await run_typed_tool(_service.buscar_datasets(query, limite=limite))

    @mcp.tool()
    async def obter_dataset(
        dataset_id: Annotated[
            str, Field(description="ID ou nome (slug) do dataset no dados.gov.br.")
        ],
    ) -> dict[str, Any]:
        """Obtém detalhes de um dataset específico do Portal Brasileiro de Dados Abertos.

        Consulta `package_show` e retorna o dataset completo: `title`,
        `notes`, `organization`, `tags`, `groups`, `license_title`,
        `metadata_modified` e a lista de `resources` (arquivos/links
        associados). Use `dataset_id` retornado por `buscar_datasets` ou
        `sugerir_datasets_para_pergunta`.
        """
        return await run_typed_tool(_service.obter_dataset(dataset_id))

    @mcp.tool()
    async def listar_recursos_dataset(
        dataset_id: Annotated[
            str, Field(description="ID ou nome (slug) do dataset no dados.gov.br.")
        ],
    ) -> dict[str, Any]:
        """Lista recursos associados a um dataset (CSV, JSON, API, PDF, XLSX e outros formatos).

        Cada recurso retornado inclui `id`, `name`, `format`, `url`,
        `description`, `mimetype`, `size`, `created` e `last_modified`. Use
        `url` para acessar o arquivo/endpoint diretamente. Retorna lista
        vazia se o dataset não tiver recursos publicados.
        """
        return await run_typed_tool(_service.listar_recursos_dataset(dataset_id))

    @mcp.tool()
    async def sugerir_datasets_para_pergunta(
        pergunta: Annotated[
            str,
            Field(
                description=(
                    "Pergunta em linguagem natural sobre um tema "
                    '(ex.: "Quais dados existem sobre desmatamento na Amazônia?").'
                )
            ),
        ],
        limite: Annotated[
            int, Field(description="Número máximo de datasets sugeridos.", ge=1, le=100)
        ] = 5,
    ) -> dict[str, Any]:
        """Recebe uma pergunta em linguagem natural e sugere datasets possivelmente úteis.

        Extrai palavras-chave de `pergunta` (tokenização e remoção de
        stopwords em português — **sem** usar nenhum modelo de linguagem) e
        busca esses termos no catálogo via `package_search`. As
        palavras-chave usadas ficam em `metadata.params["keywords"]`. Se
        nenhuma palavra-chave relevante for encontrada, retorna lista vazia
        com um aviso em `warnings`, em vez de inventar sugestões.
        """
        return await run_typed_tool(
            _service.sugerir_datasets_para_pergunta(pergunta, limite=limite)
        )
