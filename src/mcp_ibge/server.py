"""Servidor MCP `mcp-ibge`: define as tools expostas via FastMCP.

Todas as tools seguem o mesmo contrato:
    - Retornam um dicionário JSON-serializável.
    - Em caso de sucesso: ``{"metadata": {...}, "data": ...}``.
    - Em caso de erro: ``{"metadata": {...}, "error": "..."}``.

O bloco ``metadata`` sempre contém ``source_name``, ``source_url``,
``retrieved_at``, ``endpoint`` e ``params``, garantindo rastreabilidade da
origem dos dados.
"""

from __future__ import annotations

import logging
from collections.abc import Awaitable
from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from .clients import agregados, localidades, populacao
from .clients.base import IBGEResult
from .config import AGREGADOS_BASE_URL, LOCALIDADES_BASE_URL, PROJECOES_BASE_URL
from .envelope import build_error_response, build_response
from .errors import IBGERequestError

logger = logging.getLogger(__name__)

mcp = FastMCP(
    "mcp-ibge",
    instructions=(
        "Servidor MCP para consultar dados públicos e oficiais do IBGE: "
        "localidades (regiões, estados, municípios e seus códigos), agregados "
        "estatísticos do SIDRA (com metadados de variáveis e períodos) e "
        "indicadores de população. Toda resposta inclui metadados de fonte "
        "(source_name, source_url, retrieved_at, endpoint, params) para "
        "rastreabilidade."
    ),
)


async def _run(
    call: Awaitable[IBGEResult],
    *,
    endpoint: str,
    params: dict[str, Any],
) -> dict[str, Any]:
    """Executa uma chamada de cliente IBGE e converte o resultado no envelope padrão."""
    try:
        result = await call
    except IBGERequestError as exc:
        logger.warning("Erro ao consultar %s: %s", exc.url, exc)
        return build_error_response(
            source_url=exc.url, endpoint=exc.url, params=params, error=str(exc)
        )
    except Exception as exc:  # pragma: no cover - rede de segurança
        logger.exception("Erro inesperado ao consultar %s", endpoint)
        return build_error_response(
            source_url=endpoint,
            endpoint=endpoint,
            params=params,
            error=f"Erro inesperado: {exc}",
        )

    return build_response(
        source_url=result.endpoint,
        endpoint=result.endpoint,
        params=result.params,
        data=result.data,
    )


# ---------------------------------------------------------------------------
# Localidades
# ---------------------------------------------------------------------------


@mcp.tool()
async def listar_regioes() -> dict[str, Any]:
    """Lista as 5 grandes regiões geográficas do Brasil (Norte, Nordeste, Sudeste, Sul, CO)."""
    return await _run(
        localidades.listar_regioes(),
        endpoint=f"{LOCALIDADES_BASE_URL}/regioes",
        params={},
    )


@mcp.tool()
async def listar_estados(
    regiao: Annotated[
        str | None,
        Field(description='Sigla da grande região ("N", "NE", "CO", "SE", "S") ou ID numérico.'),
    ] = None,
) -> dict[str, Any]:
    """Lista os 26 estados e o Distrito Federal, com sigla, nome e região."""
    return await _run(
        localidades.listar_estados(regiao=regiao),
        endpoint=f"{LOCALIDADES_BASE_URL}/estados",
        params={"regiao": regiao} if regiao else {},
    )


@mcp.tool()
async def obter_estado(
    uf: Annotated[str, Field(description='Sigla (ex.: "SP") ou ID IBGE (ex.: "35") do estado.')],
) -> dict[str, Any]:
    """Obtém os detalhes de um estado (UF) brasileiro."""
    return await _run(
        localidades.obter_estado(uf),
        endpoint=f"{LOCALIDADES_BASE_URL}/estados/{uf}",
        params={"uf": uf},
    )


@mcp.tool()
async def listar_municipios(
    uf: Annotated[
        str | None,
        Field(
            description='Sigla (ex.: "SP") ou ID IBGE do estado. Se omitido, lista todo o Brasil.'
        ),
    ] = None,
) -> dict[str, Any]:
    """Lista municípios brasileiros, opcionalmente filtrados por estado.

    Sem o parâmetro `uf`, retorna todos os ~5570 municípios do Brasil.
    """
    endpoint = (
        f"{LOCALIDADES_BASE_URL}/estados/{uf}/municipios"
        if uf
        else f"{LOCALIDADES_BASE_URL}/municipios"
    )
    return await _run(
        localidades.listar_municipios(uf=uf),
        endpoint=endpoint,
        params={"uf": uf} if uf else {},
    )


@mcp.tool()
async def obter_municipio(
    codigo: Annotated[
        str,
        Field(
            description='Código IBGE do município com 7 dígitos (ex.: "3550308" = São Paulo/SP).'
        ),
    ],
) -> dict[str, Any]:
    """Obtém os detalhes completos de um município pelo código IBGE."""
    return await _run(
        localidades.obter_municipio(codigo),
        endpoint=f"{LOCALIDADES_BASE_URL}/municipios/{codigo}",
        params={"codigo": codigo},
    )


@mcp.tool()
async def buscar_municipios_por_nome(
    nome: Annotated[str, Field(description='Termo de busca (ex.: "Sao Jose").')],
    uf: Annotated[
        str | None,
        Field(description="Restringe a busca aos municípios desta UF (sigla ou ID)."),
    ] = None,
    limit: Annotated[int, Field(description="Número máximo de resultados.", ge=1, le=200)] = 20,
) -> dict[str, Any]:
    """Busca municípios cujo nome contenha o termo informado.

    A busca ignora maiúsculas/minúsculas e acentos (ex.: "sao jose" encontra
    "São José dos Campos"). Útil para descobrir o código IBGE de um município
    a partir do nome.
    """
    endpoint = (
        f"{LOCALIDADES_BASE_URL}/estados/{uf}/municipios"
        if uf
        else f"{LOCALIDADES_BASE_URL}/municipios"
    )
    params: dict[str, Any] = {"nome": nome, "limit": limit}
    if uf:
        params["uf"] = uf

    return await _run(
        localidades.buscar_municipios_por_nome(nome=nome, uf=uf, limit=limit),
        endpoint=endpoint,
        params=params,
    )


# ---------------------------------------------------------------------------
# Agregados / SIDRA
# ---------------------------------------------------------------------------


@mcp.tool()
async def listar_agregados(
    pesquisa: Annotated[
        str | None,
        Field(
            description='Filtra pelo nome/sigla da pesquisa de origem (ex.: "Censo Demográfico").'
        ),
    ] = None,
    assunto: Annotated[
        str | None,
        Field(description='Filtra pelo nome do assunto (ex.: "População").'),
    ] = None,
    texto: Annotated[
        str | None,
        Field(
            description=(
                "Filtro textual adicional aplicado ao nome dos agregados (substring, sem caixa)."
            )
        ),
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

    return await _run(
        agregados.listar_agregados(pesquisa=pesquisa, assunto=assunto, texto=texto),
        endpoint=AGREGADOS_BASE_URL,
        params=params,
    )


@mcp.tool()
async def obter_metadados_agregado(
    agregado_id: Annotated[
        int,
        Field(description='ID numérico do agregado (ex.: 6579 = "População residente estimada").'),
    ],
) -> dict[str, Any]:
    """Obtém os metadados de um agregado do SIDRA: variáveis, períodos e níveis territoriais.

    Use o resultado para escolher os parâmetros de `consultar_dados_agregado`.
    """
    return await _run(
        agregados.obter_metadados_agregado(agregado_id),
        endpoint=f"{AGREGADOS_BASE_URL}/{agregado_id}/metadados",
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
        Field(
            description=(
                'Filtro opcional de classificação, formato "<id_classificacao>[<id_categoria>]".'
            )
        ),
    ] = None,
) -> dict[str, Any]:
    """Consulta valores de um agregado do SIDRA para variáveis, períodos e localidades específicos.

    Para descobrir IDs válidos de variáveis, períodos e níveis territoriais,
    chame `obter_metadados_agregado` antes.
    """
    params: dict[str, Any] = {
        "agregado_id": agregado_id,
        "variaveis": variaveis,
        "periodos": periodos,
        "localidades": localidades,
    }
    if classificacoes:
        params["classificacao"] = classificacoes

    return await _run(
        agregados.consultar_dados_agregado(
            agregado_id=agregado_id,
            variaveis=variaveis,
            periodos=periodos,
            localidades=localidades,
            classificacoes=classificacoes,
        ),
        endpoint=f"{AGREGADOS_BASE_URL}/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}",
        params=params,
    )


# ---------------------------------------------------------------------------
# População
# ---------------------------------------------------------------------------


@mcp.tool()
async def obter_populacao_municipio(
    codigo_municipio: Annotated[
        str,
        Field(
            description='Código IBGE do município com 7 dígitos (ex.: "3550308" = São Paulo/SP).'
        ),
    ],
) -> dict[str, Any]:
    """Obtém a população residente estimada mais recente de um município.

    Baseado no agregado 6579 (Estimativas de população) do SIDRA.
    """
    return await _run(
        populacao.obter_populacao_municipio(codigo_municipio),
        endpoint=(
            f"{AGREGADOS_BASE_URL}/{populacao.AGREGADO_POPULACAO_ESTIMADA}"
            f"/periodos/-1/variaveis/{populacao.VARIAVEL_POPULACAO_ESTIMADA}"
        ),
        params={"codigo_municipio": codigo_municipio, "localidades": f"N6[{codigo_municipio}]"},
    )


@mcp.tool()
async def obter_projecao_populacao(
    localidade: Annotated[
        str,
        Field(description='"BR" para o Brasil, ou código IBGE de 2 dígitos de uma UF (ex.: "35").'),
    ] = "BR",
) -> dict[str, Any]:
    """Obtém a projeção populacional do IBGE para o Brasil ou uma unidade federativa."""
    return await _run(
        populacao.obter_projecao_populacao(localidade),
        endpoint=f"{PROJECOES_BASE_URL}/populacao/{localidade}",
        params={"localidade": localidade},
    )
