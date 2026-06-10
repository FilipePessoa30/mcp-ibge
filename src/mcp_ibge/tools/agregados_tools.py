"""Tools MCP do domínio de Agregados/SIDRA, incluindo indicador de população."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..config import get_settings
from ..services.agregados_service import (
    AGREGADO_POPULACAO_ESTIMADA,
    VARIAVEL_POPULACAO_ESTIMADA,
    AgregadosService,
)
from . import run_tool

_service = AgregadosService()


def register(mcp: FastMCP) -> None:
    """Registra as tools de Agregados/SIDRA na instância FastMCP fornecida."""
    base_url = get_settings().agregados_base_url

    @mcp.tool()
    async def listar_agregados(
        pesquisa: Annotated[
            str | None,
            Field(description='Filtra pela pesquisa de origem (ex.: "Censo Demográfico").'),
        ] = None,
        assunto: Annotated[
            str | None,
            Field(description='Filtra pelo nome do assunto (ex.: "População").'),
        ] = None,
        texto: Annotated[
            str | None,
            Field(description="Filtro textual adicional pelo nome dos agregados (substring)."),
        ] = None,
    ) -> dict[str, Any]:
        """Lista os agregados (tabelas estatísticas) disponíveis no SIDRA.

        Use esta tool para descobrir o ID de um agregado antes de chamar
        `obter_metadados_agregado` ou `consultar_dados_agregado`.
        """
        params: dict[str, Any] = {}
        if pesquisa:
            params["pesquisa"] = pesquisa
        if assunto:
            params["assunto"] = assunto
        if texto:
            params["texto"] = texto

        return await run_tool(
            _service.listar_agregados(pesquisa=pesquisa, assunto=assunto, texto=texto),
            endpoint=base_url,
            params=params,
        )

    @mcp.tool()
    async def obter_metadados_agregado(
        agregado_id: Annotated[
            int,
            Field(
                description='ID numérico do agregado (ex.: 6579 = "População residente estimada").'
            ),
        ],
    ) -> dict[str, Any]:
        """Obtém os metadados de um agregado do SIDRA: variáveis, períodos e níveis territoriais.

        Use o resultado para escolher os parâmetros de `consultar_dados_agregado`.
        """
        return await run_tool(
            _service.obter_metadados(agregado_id),
            endpoint=f"{base_url}/{agregado_id}/metadados",
            params={"agregado_id": agregado_id},
        )

    @mcp.tool()
    async def consultar_dados_agregado(
        agregado_id: Annotated[int, Field(description="ID numérico do agregado do SIDRA.")],
        variaveis: Annotated[
            str,
            Field(description='ID de variável, lista separada por vírgula, ou "all" para todas.'),
        ] = "all",
        periodos: Annotated[
            str,
            Field(
                description=(
                    'Período(s): um ano ("2021"), intervalo ("2010-2020"), lista '
                    '("2019,2021") ou relativo ("-1" = último período disponível).'
                )
            ),
        ] = "-1",
        localidades: Annotated[
            str,
            Field(
                description=(
                    'Unidade territorial no formato N<nivel>[<ids>], ex.: "N1[all]" '
                    '(Brasil), "N3[all]" (todos os estados), "N6[3550308]" (município '
                    'de São Paulo). "BR" é aceito como atalho para "N1[all]".'
                )
            ),
        ] = "N1[all]",
        classificacoes: Annotated[
            str | None,
            Field(description='Classificação opcional ("<id_classificacao>[<id_categoria>]").'),
        ] = None,
    ) -> dict[str, Any]:
        """Consulta valores de um agregado do SIDRA para variáveis, períodos e localidades.

        Para descobrir IDs válidos de variáveis, períodos e níveis
        territoriais, chame `obter_metadados_agregado` antes.
        """
        params: dict[str, Any] = {
            "agregado_id": agregado_id,
            "variaveis": variaveis,
            "periodos": periodos,
            "localidades": localidades,
        }
        if classificacoes:
            params["classificacao"] = classificacoes

        return await run_tool(
            _service.consultar_dados(
                agregado_id,
                variaveis=variaveis,
                periodos=periodos,
                localidades=localidades,
                classificacoes=classificacoes,
            ),
            endpoint=f"{base_url}/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}",
            params=params,
        )

    @mcp.tool()
    async def obter_populacao_municipio(
        codigo_municipio: Annotated[
            str,
            Field(description='Código IBGE do município com 7 dígitos (ex.: "3550308" = SP).'),
        ],
    ) -> dict[str, Any]:
        """Obtém a população residente estimada mais recente de um município.

        Baseado no agregado 6579 (Estimativas de população) do SIDRA.
        """
        return await run_tool(
            _service.obter_populacao_municipio(codigo_municipio),
            endpoint=(
                f"{base_url}/{AGREGADO_POPULACAO_ESTIMADA}"
                f"/periodos/-1/variaveis/{VARIAVEL_POPULACAO_ESTIMADA}"
            ),
            params={"codigo_municipio": codigo_municipio, "localidades": f"N6[{codigo_municipio}]"},
        )
