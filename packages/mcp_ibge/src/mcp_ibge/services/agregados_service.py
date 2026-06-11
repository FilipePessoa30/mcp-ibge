"""Regras de negócio do domínio de Agregados/SIDRA: filtros e indicadores.

Esta camada usa `AgregadosClient` para falar com a API do IBGE e os schemas de
`mcp_ibge.schemas.agregados` para devolver dados limpos, tipados e
rastreáveis (`TypedToolResult`) às tools MCP.
"""

from __future__ import annotations

import re
from typing import Any

from ..clients.agregados import AgregadosClient
from ..schemas.agregados import (
    AgregadoMetadata,
    AgregadoPeriod,
    AgregadoQueryResult,
    AgregadoSummary,
    AgregadoVariable,
    agregado_metadata_from_raw,
    agregado_period_from_raw,
    agregado_query_results_from_raw,
    agregado_variable_from_raw,
    agregados_summary_from_lista,
)
from ..schemas.common import SourceMetadata, TypedToolResult, build_metadata
from ..utils.errors import IBGEClientError

# Nível territorial fixo do indicador de população por município.
_NIVEL_MUNICIPIO = "N6"

_NIVEL_PATTERN = re.compile(r"N\d+")

# Agregado SIDRA "Estimativas de população residente" (variável "População
# residente estimada"), usado por `consultar_populacao_municipio`.
# Referência: https://sidra.ibge.gov.br/tabela/6579
#
# O IBGE costuma descontinuar/renomear agregados e variáveis após cada Censo;
# se estas constantes pararem de funcionar, atualize-as (ou use
# `consultar_agregado` diretamente após localizar os novos IDs com
# `listar_agregados`/`obter_metadados_agregado`).
AGREGADO_POPULACAO_ESTIMADA = "6579"
VARIAVEL_POPULACAO_ESTIMADA = "9324"

# Alias amigável para o nível territorial "Brasil" (N1) no SIDRA.
_LOCALIDADE_ALIASES = {
    "brasil": "N1[all]",
    "br": "N1[all]",
}


def _resolver_localidades(localidades: str) -> str:
    """Resolve aliases simples (ex.: "BR") para a sintaxe N<nivel>[<ids>] do SIDRA."""
    return _LOCALIDADE_ALIASES.get(localidades.strip().lower(), localidades)


def _extrair_niveis_territoriais(localidades: str) -> str | None:
    """Extrai os níveis territoriais (ex.: "N1", "N6") de uma string `localidades`.

    `localidades` pode combinar múltiplos níveis separados por "|" (ex.:
    "N3[33,35]|N6[3550308]"). Retorna os níveis únicos, na ordem em que
    aparecem, separados por "|" (ou `None` se nenhum for encontrado).
    """
    niveis = dict.fromkeys(_NIVEL_PATTERN.findall(localidades))
    return "|".join(niveis) or None


def _metadata(
    *,
    endpoint: str,
    params: dict[str, Any],
    period: str | None = None,
    territorial_level: str | None = None,
    cache_hit: bool = False,
) -> SourceMetadata:
    return build_metadata(
        source_url=endpoint,
        endpoint=endpoint,
        params=params,
        period=period,
        territorial_level=territorial_level,
        cache_hit=cache_hit,
    )


class AgregadosService:
    """Operações de alto nível sobre tabelas (agregados) do SIDRA."""

    def __init__(self, client: AgregadosClient | None = None) -> None:
        self._client = client or AgregadosClient()

    async def listar_agregados(
        self,
        pesquisa: str | None = None,
        assunto: str | None = None,
        texto: str | None = None,
    ) -> TypedToolResult[list[AgregadoSummary]]:
        """Lista agregados do SIDRA, com filtro textual local opcional pelo nome."""
        params: dict[str, Any] = {}
        if pesquisa:
            params["pesquisa"] = pesquisa
        if assunto:
            params["assunto"] = assunto

        try:
            result = await self._client.list_agregados(pesquisa=pesquisa, assunto=assunto)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params=params),
                errors=[str(exc)],
            )

        agregados = agregados_summary_from_lista(result.data)

        if texto:
            termo = texto.strip().lower()
            agregados = [a for a in agregados if termo in a.nome.lower()]

        params = dict(result.params)
        if texto:
            params["texto"] = texto

        return TypedToolResult(
            ok=True,
            data=agregados,
            metadata=_metadata(endpoint=result.endpoint, params=params, cache_hit=result.cache_hit),
        )

    async def obter_metadados_agregado(
        self, agregado_id: str
    ) -> TypedToolResult[AgregadoMetadata | None]:
        """Obtém os metadados de um agregado: pesquisa, assunto, periodicidade etc."""
        try:
            result = await self._client.get_agregado_metadata(agregado_id)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=_metadata(endpoint=exc.url, params={"agregado_id": agregado_id}),
                errors=[str(exc)],
            )

        return TypedToolResult(
            ok=True,
            data=agregado_metadata_from_raw(result.data),
            metadata=_metadata(
                endpoint=result.endpoint, params=result.params, cache_hit=result.cache_hit
            ),
        )

    async def listar_variaveis_agregado(
        self, agregado_id: str
    ) -> TypedToolResult[list[AgregadoVariable]]:
        """Lista as variáveis disponíveis em um agregado."""
        try:
            result = await self._client.get_agregado_variaveis(agregado_id)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params={"agregado_id": agregado_id}),
                errors=[str(exc)],
            )

        variaveis = [agregado_variable_from_raw(item) for item in result.data]
        return TypedToolResult(
            ok=True,
            data=variaveis,
            metadata=_metadata(
                endpoint=result.endpoint, params=result.params, cache_hit=result.cache_hit
            ),
        )

    async def listar_periodos_agregado(
        self, agregado_id: str
    ) -> TypedToolResult[list[AgregadoPeriod]]:
        """Lista os períodos disponíveis para consulta em um agregado."""
        try:
            result = await self._client.get_agregado_periodos(agregado_id)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(endpoint=exc.url, params={"agregado_id": agregado_id}),
                errors=[str(exc)],
            )

        periodos = [agregado_period_from_raw(item) for item in result.data]
        return TypedToolResult(
            ok=True,
            data=periodos,
            metadata=_metadata(
                endpoint=result.endpoint, params=result.params, cache_hit=result.cache_hit
            ),
        )

    async def listar_localidades_agregado(
        self, agregado_id: str, niveis: str
    ) -> TypedToolResult[list[dict[str, Any]]]:
        """Lista as localidades disponíveis para um agregado em um ou mais níveis territoriais.

        `niveis` aceita um único nível (ex.: "N6") ou múltiplos separados por
        "|" (ex.: "N1|N3"). Não há um schema tipado para localidades de
        agregado: cada item é devolvido como veio da API (`id`, `nome`,
        `nivel`, ...).
        """
        try:
            result = await self._client.get_agregado_localidades(agregado_id, niveis)
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(
                    endpoint=exc.url,
                    params={"agregado_id": agregado_id, "niveis": niveis},
                    territorial_level=niveis,
                ),
                errors=[str(exc)],
            )

        return TypedToolResult(
            ok=True,
            data=result.data,
            metadata=_metadata(
                endpoint=result.endpoint,
                params=result.params,
                territorial_level=niveis,
                cache_hit=result.cache_hit,
            ),
        )

    async def consultar_agregado(
        self,
        agregado_id: str,
        variaveis: str,
        localidades: str,
        periodos: str = "-6",
        classificacao: str | None = None,
        view: str | None = None,
    ) -> TypedToolResult[list[AgregadoQueryResult]]:
        """Consulta valores de um agregado, resolvendo aliases de localidade (ex.: "BR")."""
        localidades_resolvidas = _resolver_localidades(localidades)

        try:
            result = await self._client.query_agregado(
                agregado_id,
                variaveis=variaveis,
                localidades=localidades_resolvidas,
                periodos=periodos,
                classificacao=classificacao,
                view=view,
            )
        except IBGEClientError as exc:
            params: dict[str, Any] = {
                "agregado_id": agregado_id,
                "variaveis": variaveis,
                "localidades": localidades_resolvidas,
                "periodos": periodos,
            }
            if classificacao:
                params["classificacao"] = classificacao
            if view:
                params["view"] = view
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(
                    endpoint=exc.url,
                    params=params,
                    period=periodos,
                    territorial_level=_extrair_niveis_territoriais(localidades_resolvidas),
                ),
                errors=[str(exc)],
            )

        valores = agregado_query_results_from_raw(agregado_id, result.data)
        return TypedToolResult(
            ok=True,
            data=valores,
            metadata=_metadata(
                endpoint=result.endpoint,
                params=result.params,
                period=str(result.params.get("periodos", periodos)),
                territorial_level=_extrair_niveis_territoriais(
                    str(result.params.get("localidades", localidades_resolvidas))
                ),
                cache_hit=result.cache_hit,
            ),
        )

    async def consultar_populacao_municipio(
        self, codigo_municipio: int, ano: int | None = None
    ) -> TypedToolResult[list[AgregadoQueryResult]]:
        """Obtém a população residente estimada de um município.

        Usa o agregado `AGREGADO_POPULACAO_ESTIMADA` (variável
        `VARIAVEL_POPULACAO_ESTIMADA`) do SIDRA. Sem `ano`, usa o período mais
        recente disponível ("-1").

        Se a consulta falhar (ex.: o IBGE descontinuou/renomeou essa tabela
        após um novo Censo), o resultado vem com `ok=False` e uma mensagem de
        erro orientando a usar `consultar_agregado` diretamente, após
        localizar os IDs corretos com `listar_agregados`,
        `obter_metadados_agregado` e `listar_variaveis_agregado`.
        """
        periodos = str(ano) if ano is not None else "-1"
        localidades = f"N6[{codigo_municipio}]"

        params: dict[str, Any] = {
            "codigo_municipio": codigo_municipio,
            "agregado_id": AGREGADO_POPULACAO_ESTIMADA,
            "variaveis": VARIAVEL_POPULACAO_ESTIMADA,
            "localidades": localidades,
            "periodos": periodos,
        }

        try:
            result = await self._client.query_agregado(
                AGREGADO_POPULACAO_ESTIMADA,
                variaveis=VARIAVEL_POPULACAO_ESTIMADA,
                localidades=localidades,
                periodos=periodos,
            )
        except IBGEClientError as exc:
            return TypedToolResult(
                ok=False,
                data=[],
                metadata=_metadata(
                    endpoint=exc.url,
                    params=params,
                    period=periodos,
                    territorial_level=_NIVEL_MUNICIPIO,
                ),
                errors=[
                    f"Não foi possível obter a população do município {codigo_municipio} "
                    f"usando o agregado {AGREGADO_POPULACAO_ESTIMADA} (variável "
                    f"{VARIAVEL_POPULACAO_ESTIMADA}) do SIDRA: {exc} "
                    "Essa tabela pode ter sido descontinuada ou renomeada pelo IBGE. "
                    "Use `consultar_agregado` diretamente, após localizar os IDs "
                    "corretos com `listar_agregados`, `obter_metadados_agregado` e "
                    "`listar_variaveis_agregado`."
                ],
            )

        valores = agregado_query_results_from_raw(AGREGADO_POPULACAO_ESTIMADA, result.data)

        params = {"codigo_municipio": codigo_municipio, **result.params}
        return TypedToolResult(
            ok=True,
            data=valores,
            metadata=_metadata(
                endpoint=result.endpoint,
                params=params,
                period=periodos,
                territorial_level=_NIVEL_MUNICIPIO,
                cache_hit=result.cache_hit,
            ),
        )
