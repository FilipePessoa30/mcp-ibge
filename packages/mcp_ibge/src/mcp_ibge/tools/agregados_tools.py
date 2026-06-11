"""Tools MCP do domínio de Agregados/SIDRA, incluindo indicador de população."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..schemas.agregados import AgregadoQueryResult
from ..schemas.common import TypedToolResult
from ..services.agregados_service import AgregadosService
from ..services.localidades_service import LocalidadesService
from . import run_typed_tool

_agregados_service = AgregadosService()
_localidades_service = LocalidadesService()

_AGREGADO_ID_DESCRIPTION = 'ID do agregado do SIDRA (ex.: "6579" = "População residente estimada").'

_LOCALIDADES_DESCRIPTION = (
    'Unidade territorial no formato N<nivel>[<ids>], ex.: "N1[all]" (Brasil), '
    '"N3[all]" (todos os estados), "N6[3550308]" (município de São Paulo). '
    '"BR" é aceito como atalho para "N1[all]".'
)

_PERIODOS_DESCRIPTION = (
    'Período(s): um ano ("2021"), intervalo ("2010-2020"), lista '
    '("2019,2021") ou relativo ("-6" = últimos 6 períodos, "-1" = último '
    "período disponível)."
)


async def _consultar_populacao_por_nome(
    nome: str, uf: str, ano: int | None
) -> TypedToolResult[list[AgregadoQueryResult]]:
    """Resolve `nome`/`uf` para um código IBGE e consulta a população estimada."""
    busca = await _localidades_service.obter_codigo_municipio(nome, uf)

    if not busca.ok or busca.data is None:
        return TypedToolResult(
            ok=False,
            data=[],
            metadata=busca.metadata,
            warnings=busca.warnings,
            errors=busca.errors,
        )

    resultado = await _agregados_service.consultar_populacao_municipio(busca.data, ano=ano)

    warnings = list(resultado.warnings)
    if resultado.ok:
        if any(item.valor is None for item in resultado.data):
            warnings.append(
                "O valor de população não está disponível (dado ausente ou "
                "sigiloso no SIDRA) para um ou mais períodos retornados."
            )
        if ano is None and resultado.data:
            periodo = resultado.data[0].periodo
            warnings.append(
                f'Nenhum "ano" foi informado: retornado o período mais recente '
                f'disponível no SIDRA ("{periodo}"), que pode não ser o ano corrente.'
            )

    metadata = resultado.metadata.model_copy(
        update={"params": {"nome": nome, "uf": uf, **resultado.metadata.params}}
    )

    return TypedToolResult(
        ok=resultado.ok,
        data=resultado.data,
        metadata=metadata,
        warnings=warnings,
        errors=resultado.errors,
    )


def register_agregados_tools(mcp: FastMCP) -> None:
    """Registra as tools de Agregados/SIDRA na instância FastMCP fornecida."""

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
        """Lista agregados disponíveis na API de Agregados do IBGE.

        Cada agregado retornado inclui `id` e `nome`. Use esta tool para
        descobrir o ID de um agregado antes de chamar
        `obter_metadados_agregado`, `listar_variaveis_agregado` ou
        `consultar_agregado`.
        """
        return await run_typed_tool(
            _agregados_service.listar_agregados(pesquisa=pesquisa, assunto=assunto, texto=texto)
        )

    @mcp.tool()
    async def obter_metadados_agregado(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Obtém metadados de um agregado do IBGE/SIDRA, incluindo variáveis,
        classificações e informações disponíveis.

        Os campos `pesquisa`, `assunto` e `periodicidade` ficam disponíveis
        diretamente; o JSON completo (variáveis, classificações, níveis
        territoriais) está em `raw`.
        """
        return await run_typed_tool(_agregados_service.obter_metadados_agregado(agregado_id))

    @mcp.tool()
    async def listar_variaveis_agregado(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Lista variáveis disponíveis em um agregado do IBGE.

        Cada variável retornada inclui `id`, `nome` e `unidade`. Use o `id`
        de uma variável no parâmetro `variaveis` de `consultar_agregado`.
        """
        return await run_typed_tool(_agregados_service.listar_variaveis_agregado(agregado_id))

    @mcp.tool()
    async def listar_periodos_agregado(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
    ) -> dict[str, Any]:
        """Lista períodos disponíveis em um agregado do IBGE.

        Cada período retornado inclui `id` (ex.: "2024") e `nome`. Use o `id`
        de um período no parâmetro `periodos` de `consultar_agregado`.
        """
        return await run_typed_tool(_agregados_service.listar_periodos_agregado(agregado_id))

    @mcp.tool()
    async def listar_localidades_agregado(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
        niveis: Annotated[
            str,
            Field(
                description=(
                    'Nível(is) territorial(is), ex.: "N1" (Brasil), "N2" '
                    '(regiões), "N3" (estados) ou "N6" (municípios). '
                    'Múltiplos níveis são separados por "|" (ex.: "N1|N3").'
                )
            ),
        ],
    ) -> dict[str, Any]:
        """Lista localidades disponíveis para um agregado em níveis como N1, N2, N3 ou N6.

        Cada localidade retornada inclui `id`, `nome` e `nivel`, exatamente
        como veio da API do SIDRA (não há schema tipado para este endpoint).
        Use o `id` de uma localidade no parâmetro `localidades` de
        `consultar_agregado` (ex.: "N6[3550308]").
        """
        return await run_typed_tool(
            _agregados_service.listar_localidades_agregado(agregado_id, niveis)
        )

    @mcp.tool()
    async def consultar_agregado(
        agregado_id: Annotated[str, Field(description=_AGREGADO_ID_DESCRIPTION)],
        variaveis: Annotated[
            str,
            Field(description='ID de variável, lista separada por vírgula, ou "all" para todas.'),
        ],
        localidades: Annotated[str, Field(description=_LOCALIDADES_DESCRIPTION)],
        periodos: Annotated[str, Field(description=_PERIODOS_DESCRIPTION)] = "-6",
        classificacao: Annotated[
            str | None,
            Field(description='Classificação opcional ("<id_classificacao>[<id_categoria>]").'),
        ] = None,
        view: Annotated[
            str | None,
            Field(description='Formato alternativo de resposta da API (ex.: "flat").'),
        ] = None,
    ) -> dict[str, Any]:
        """Consulta dados de um agregado do IBGE/SIDRA com variáveis,
        localidades, períodos e classificações.

        Retorna uma lista achatada de valores, um por combinação de
        (variável, localidade, período), cada um com `valor` (número, ou
        `null` quando o dado é ausente/sigiloso no SIDRA), `unidade`,
        `localidade_nome` etc. Para descobrir IDs válidos, use
        `listar_variaveis_agregado`, `listar_periodos_agregado` e
        `listar_localidades_agregado`.
        """
        return await run_typed_tool(
            _agregados_service.consultar_agregado(
                agregado_id,
                variaveis=variaveis,
                localidades=localidades,
                periodos=periodos,
                classificacao=classificacao,
                view=view,
            )
        )

    @mcp.tool()
    async def consultar_populacao_municipio(
        nome: Annotated[str, Field(description="Nome do município.")],
        uf: Annotated[str, Field(description='Sigla (ex.: "SP") ou código IBGE da UF.')],
        ano: Annotated[
            int | None,
            Field(description="Ano de referência. Sem este parâmetro, usa o mais recente."),
        ] = None,
    ) -> dict[str, Any]:
        """Consulta população de um município usando nome e UF.

        Resolve o código IBGE do município (buscando por `nome`/`uf` via o
        serviço de Localidades) antes de consultar o agregado de população
        residente estimada do SIDRA. Se o nome for ambíguo dentro da UF, ou
        se nenhum município for encontrado, retorna erro com os candidatos
        em `warnings`/`error`. A resposta de sucesso pode incluir `warnings`
        adicionais sobre incertezas metodológicas (ex.: dado indisponível
        para o período, ou qual período foi retornado quando `ano` não é
        informado).
        """
        return await run_typed_tool(_consultar_populacao_por_nome(nome, uf, ano))
