"""Regras de negócio da comparação de municípios (`comparar_municipios`).

Resolve cada município por nome + UF (mesma lógica de
`obter_codigo_municipio`/`obter_municipio_por_codigo`) e consulta, para cada
um, os indicadores solicitados que já estiverem implementados com segurança
(por ora, apenas população estimada). Indicadores não reconhecidos geram um
`warning` e são listados em `indicadores_nao_implementados`, sem interromper
a comparação dos demais. Municípios não encontrados ou ambíguos aparecem em
`municipios_nao_resolvidos`, com o motivo, sem inventar dados.
"""

from __future__ import annotations

import re

from ..schemas.common import SourceMetadata, TypedToolResult, build_metadata
from ..schemas.comparacao import (
    ComparacaoMunicipios,
    MunicipioComparado,
    MunicipioConsulta,
    MunicipioNaoResolvido,
)
from ..schemas.perfil import IndicadorPerfil
from ..utils.normalization import normalize_text
from .agregados_service import AGREGADO_POPULACAO_ESTIMADA, AgregadosService
from .localidades_service import LocalidadesService

# Número máximo de municípios por chamada, para evitar que um agente dispare
# um número grande de requisições à API do IBGE de uma só vez.
MAX_MUNICIPIOS = 10

# Indicador padrão usado quando `indicadores` não é informado.
_INDICADORES_PADRAO = ["populacao"]

# Variações aceitas para o indicador de população estimada, normalizadas
# (sem acentos/maiúsculas/pontuação) via `_normalizar_chave_indicador`.
_ALIASES_POPULACAO = {"populacao", "populacaoestimada"}

_LIMITACOES_BASE = [
    "Esta comparação cobre apenas os indicadores listados em "
    "`indicadores_consultados`; indicadores em `indicadores_nao_implementados` "
    "são apenas sugestões de nomes, não dados.",
    "O indicador de população usa o agregado SIDRA "
    f"{AGREGADO_POPULACAO_ESTIMADA} (Estimativas de população residente), "
    "que pode ser descontinuado ou renomeado pelo IBGE após um novo Censo.",
]

_LIMITACAO_PERIODO_VARIAVEL = (
    'Sem o parâmetro "ano", cada município retorna o período mais recente '
    "disponível no SIDRA para esse indicador, que pode diferir entre "
    "municípios se algum não tiver dados para o período mais recente."
)


def _normalizar_chave_indicador(valor: str) -> str:
    """Normaliza um nome de indicador para comparação (sem acentos/espaços/pontuação)."""
    return re.sub(r"[^a-z0-9]", "", normalize_text(valor))


def _adicionar_fonte(fontes: list[str], endpoint: str) -> None:
    if endpoint and endpoint not in fontes:
        fontes.append(endpoint)


class ComparacaoService:
    """Compara municípios com base nos indicadores já implementados com segurança."""

    def __init__(
        self,
        localidades_service: LocalidadesService | None = None,
        agregados_service: AgregadosService | None = None,
    ) -> None:
        self._localidades = localidades_service or LocalidadesService()
        self._agregados = agregados_service or AgregadosService()

    async def comparar_municipios(
        self,
        municipios: list[MunicipioConsulta],
        indicadores: list[str] | None = None,
        ano: int | None = None,
    ) -> TypedToolResult[ComparacaoMunicipios | None]:
        """Compara municípios (nome + UF) usando os indicadores solicitados (ou os padrão)."""
        if not municipios:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=build_metadata(source_url="", endpoint=""),
                errors=['Informe ao menos um município em "municipios".'],
            )

        if len(municipios) > MAX_MUNICIPIOS:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=build_metadata(source_url="", endpoint=""),
                errors=[
                    f"No máximo {MAX_MUNICIPIOS} municípios por chamada "
                    f"(recebidos {len(municipios)})."
                ],
            )

        indicadores_resolvidos, indicadores_nao_implementados, warnings = (
            self._resolver_indicadores(indicadores)
        )

        municipios_resolvidos: list[MunicipioComparado] = []
        municipios_nao_resolvidos: list[MunicipioNaoResolvido] = []
        fontes: list[str] = []
        metadata_referencia: SourceMetadata | None = None

        for municipio in municipios:
            codigo = await self._localidades.obter_codigo_municipio(municipio.nome, municipio.uf)
            _adicionar_fonte(fontes, codigo.metadata.endpoint)
            metadata_referencia = metadata_referencia or codigo.metadata

            if not codigo.ok or codigo.data is None:
                motivo = "; ".join(codigo.errors or codigo.warnings) or "Município não encontrado."
                municipios_nao_resolvidos.append(
                    MunicipioNaoResolvido(nome=municipio.nome, uf=municipio.uf, motivo=motivo)
                )
                warnings.extend(codigo.errors or codigo.warnings)
                continue

            detalhes = await self._localidades.obter_municipio_por_codigo(codigo.data)
            _adicionar_fonte(fontes, detalhes.metadata.endpoint)

            if not detalhes.ok or detalhes.data is None:
                motivo = "; ".join(detalhes.errors) or (
                    "Não foi possível obter os detalhes do município."
                )
                municipios_nao_resolvidos.append(
                    MunicipioNaoResolvido(nome=municipio.nome, uf=municipio.uf, motivo=motivo)
                )
                warnings.extend(detalhes.errors)
                continue

            dados_municipio = detalhes.data
            indicadores_municipio: list[IndicadorPerfil] = []

            for indicador in indicadores_resolvidos:
                if indicador == "populacao_estimada":
                    item, item_warnings, populacao_metadata = await self._consultar_populacao(
                        codigo.data, dados_municipio.nome, ano
                    )
                    if populacao_metadata is not None:
                        _adicionar_fonte(fontes, populacao_metadata.endpoint)
                        metadata_referencia = populacao_metadata
                    if item is not None:
                        indicadores_municipio.append(item)
                    warnings.extend(item_warnings)

            municipios_resolvidos.append(
                MunicipioComparado(
                    codigo_ibge=dados_municipio.id,
                    nome=dados_municipio.nome,
                    uf_sigla=dados_municipio.uf_sigla,
                    uf_nome=dados_municipio.uf_nome,
                    regiao_nome=dados_municipio.regiao_nome,
                    indicadores=indicadores_municipio,
                )
            )

        if not municipios_resolvidos:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=metadata_referencia or build_metadata(source_url="", endpoint=""),
                warnings=warnings,
                errors=["Nenhum dos municípios informados pôde ser resolvido."],
            )

        limitacoes = list(_LIMITACOES_BASE)
        if ano is None and "populacao_estimada" in indicadores_resolvidos:
            limitacoes.append(_LIMITACAO_PERIODO_VARIAVEL)

        comparacao = ComparacaoMunicipios(
            municipios=municipios_resolvidos,
            municipios_nao_resolvidos=municipios_nao_resolvidos,
            indicadores_consultados=indicadores_resolvidos,
            indicadores_nao_implementados=indicadores_nao_implementados,
            fontes=fontes,
            limitacoes=limitacoes,
        )

        metadata = (metadata_referencia or build_metadata(source_url="", endpoint="")).model_copy(
            update={
                "params": {
                    "municipios": [{"nome": m.nome, "uf": m.uf} for m in municipios],
                    "indicadores": indicadores_resolvidos,
                    "ano": ano,
                }
            }
        )

        return TypedToolResult(ok=True, data=comparacao, metadata=metadata, warnings=warnings)

    def _resolver_indicadores(
        self, indicadores: list[str] | None
    ) -> tuple[list[str], list[str], list[str]]:
        """Mapeia os nomes de indicadores solicitados para os indicadores suportados.

        Retorna `(indicadores_resolvidos, indicadores_nao_implementados, warnings)`.
        """
        solicitados = indicadores if indicadores else list(_INDICADORES_PADRAO)

        resolvidos: list[str] = []
        nao_implementados: list[str] = []
        warnings: list[str] = []

        for indicador in solicitados:
            chave = _normalizar_chave_indicador(indicador)
            if chave in _ALIASES_POPULACAO:
                if "populacao_estimada" not in resolvidos:
                    resolvidos.append("populacao_estimada")
            else:
                nao_implementados.append(indicador)
                warnings.append(
                    f'Indicador "{indicador}" não está implementado e foi ignorado. '
                    'Indicadores disponíveis atualmente: "populacao" (população '
                    "residente estimada)."
                )

        return resolvidos, nao_implementados, warnings

    async def _consultar_populacao(
        self, codigo_municipio: int, nome_municipio: str, ano: int | None
    ) -> tuple[IndicadorPerfil | None, list[str], SourceMetadata | None]:
        """Consulta a população estimada de um município, sem inventar dados em caso de falha."""
        populacao = await self._agregados.consultar_populacao_municipio(codigo_municipio, ano=ano)

        if not populacao.ok:
            mensagem = "; ".join(populacao.errors or ["erro desconhecido ao consultar o SIDRA."])
            warnings = [
                *populacao.warnings,
                f'Não foi possível obter a população de "{nome_municipio}": {mensagem}',
            ]
            return None, warnings, populacao.metadata

        valores_disponiveis = [item for item in populacao.data if item.valor is not None]
        if not valores_disponiveis:
            return (
                None,
                [
                    f'População não disponível para "{nome_municipio}" '
                    "(dado ausente ou sigiloso no SIDRA)."
                ],
                populacao.metadata,
            )

        item = valores_disponiveis[0]
        indicador = IndicadorPerfil(
            indicador="populacao_estimada",
            valor=item.valor,
            unidade=item.unidade,
            periodo=item.periodo,
            agregado_id=item.agregado_id,
            variavel_id=item.variavel_id,
        )
        return indicador, [], populacao.metadata
