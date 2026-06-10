"""Tools MCP do domínio de Localidades (regiões, estados, municípios, distritos)."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.localidades_service import LocalidadesService
from . import run_typed_tool

_service = LocalidadesService()


def register_localidades_tools(mcp: FastMCP) -> None:
    """Registra as tools de Localidades na instância FastMCP fornecida."""

    @mcp.tool()
    async def listar_regioes() -> dict[str, Any]:
        """Lista as grandes regiões brasileiras segundo a API de Localidades do IBGE.

        Retorna as 5 regiões (Norte, Nordeste, Sudeste, Sul, Centro-Oeste),
        cada uma com `id`, `sigla` e `nome`.
        """
        return await run_typed_tool(_service.listar_regioes())

    @mcp.tool()
    async def listar_estados() -> dict[str, Any]:
        """Lista todas as unidades federativas do Brasil com código IBGE, sigla, nome e região.

        Retorna os 26 estados e o Distrito Federal, ordenados por nome, cada
        um com `id` (código IBGE), `sigla`, `nome` e a `regiao` a que pertence.
        """
        return await run_typed_tool(_service.listar_estados())

    @mcp.tool()
    async def obter_estado(
        uf: Annotated[
            str, Field(description='Sigla (ex.: "SP") ou código IBGE (ex.: "35") do estado.')
        ],
    ) -> dict[str, Any]:
        """Obtém os detalhes de um estado (UF) brasileiro a partir da sigla ou do código IBGE."""
        return await run_typed_tool(_service.obter_estado(uf))

    @mcp.tool()
    async def listar_municipios(
        uf: Annotated[
            str,
            Field(description='Sigla da UF (ex.: "RJ", "SP", "MG") ou código IBGE da UF.'),
        ],
    ) -> dict[str, Any]:
        """Lista municípios de uma unidade federativa. Aceita sigla como RJ, SP, MG ou código da UF.

        Cada município retornado inclui `id` (código IBGE de 7 dígitos),
        `nome`, `uf_sigla`, `uf_nome` e `regiao_nome`.
        """
        return await run_typed_tool(_service.listar_municipios(uf))

    @mcp.tool()
    async def buscar_municipio(
        nome: Annotated[str, Field(description="Nome (ou parte do nome) do município a buscar.")],
        uf: Annotated[
            str | None,
            Field(description="Restringe a busca aos municípios desta UF (sigla ou código)."),
        ] = None,
        limite: Annotated[
            int, Field(description="Número máximo de candidatos retornados.", ge=1, le=50)
        ] = 10,
    ) -> dict[str, Any]:
        """Busca município pelo nome, opcionalmente filtrando por UF.

        Retorna candidatos quando houver ambiguidade. A busca ignora acentos
        e maiúsculas/minúsculas, e tenta nesta ordem:
        correspondência exata, depois "contém" e, por fim, similaridade
        textual. Sem `uf`, busca em todo o Brasil. Quando há mais de uma
        correspondência, a resposta inclui um aviso em `warnings` listando os
        candidatos e sugerindo refinar a busca (ex.: informando `uf`).
        """
        return await run_typed_tool(_service.buscar_municipio(nome, uf=uf, limite=limite))

    @mcp.tool()
    async def obter_codigo_municipio(
        nome: Annotated[str, Field(description="Nome do município.")],
        uf: Annotated[str, Field(description='Sigla (ex.: "SP") ou código IBGE da UF.')],
    ) -> dict[str, Any]:
        """Retorna o código IBGE de 7 dígitos de um município a partir do nome e da UF.

        Retorna erro se nenhum município corresponder ao nome informado ou se
        o nome for ambíguo dentro da UF (nesse caso, veja `warnings` para os
        candidatos encontrados).
        """
        return await run_typed_tool(_service.obter_codigo_municipio(nome, uf))

    @mcp.tool()
    async def obter_municipio_por_codigo(
        codigo_ibge: Annotated[
            int, Field(description="Código IBGE do município com 7 dígitos (ex.: 3550308 = SP).")
        ],
    ) -> dict[str, Any]:
        """Retorna informações de município a partir do código IBGE.

        Inclui `nome`, `uf_sigla`, `uf_nome` e `regiao_nome` resolvidos a
        partir do código IBGE de 7 dígitos.
        """
        return await run_typed_tool(_service.obter_municipio_por_codigo(codigo_ibge))

    @mcp.tool()
    async def listar_distritos(
        codigo_municipio: Annotated[
            int, Field(description="Código IBGE do município com 7 dígitos (ex.: 3550308 = SP).")
        ],
    ) -> dict[str, Any]:
        """Lista distritos de um município a partir do código IBGE.

        Cada distrito retornado inclui `id`, `nome`, `municipio_id` e
        `municipio_nome`.
        """
        return await run_typed_tool(_service.listar_distritos(codigo_municipio))
