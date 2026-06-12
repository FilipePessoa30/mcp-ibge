"""Regras de negócio do perfil básico de município (`gerar_perfil_municipal`).

Combina `LocalidadesService` (identificação) e `AgregadosService` (indicador
de população) para montar um `PerfilMunicipal` sem inventar dados: cada
indicador retornado vem de uma chamada real à API do IBGE, e indicadores
ainda não implementados aparecem apenas em
`proximos_indicadores_sugeridos` (nomes, não dados).
"""

from __future__ import annotations

from ..schemas.common import TypedToolResult
from ..schemas.perfil import (
    IndicadorPerfil,
    MunicipioPerfil,
    PerfilMunicipal,
    extrair_microrregiao_ou_regiao_intermediaria,
)
from .agregados_service import AGREGADO_POPULACAO_ESTIMADA, AgregadosService
from .localidades_service import LocalidadesService

# Limitações conhecidas, sempre presentes no perfil.
_LIMITACOES_BASE = [
    "Este perfil cobre apenas identificação básica do município e o "
    "indicador de população estimada; não inclui PIB, IDH, área territorial "
    "ou outros indicadores socioeconômicos.",
    "O indicador de população usa o agregado SIDRA "
    f"{AGREGADO_POPULACAO_ESTIMADA} (Estimativas de população residente), "
    "que pode ser descontinuado ou renomeado pelo IBGE após um novo Censo.",
]

# Indicadores que ainda não são consultados por `gerar_perfil_municipal`, mas
# que poderiam ser adicionados em uma versão futura. Apenas nomes/sugestões —
# nunca dados.
PROXIMOS_INDICADORES_SUGERIDOS = [
    "Área territorial e densidade demográfica",
    "PIB municipal e PIB per capita",
    "IDH municipal",
    "Distritos do município (via `listar_distritos`)",
    "Indicadores educacionais e de saúde",
]


class PerfilService:
    """Monta um perfil básico de município combinando Localidades e Agregados/SIDRA."""

    def __init__(
        self,
        localidades_service: LocalidadesService | None = None,
        agregados_service: AgregadosService | None = None,
    ) -> None:
        self._localidades = localidades_service or LocalidadesService()
        self._agregados = agregados_service or AgregadosService()

    async def gerar_perfil_municipal(
        self, nome: str, uf: str, ano: int | None = None
    ) -> TypedToolResult[PerfilMunicipal | None]:
        """Gera o perfil básico de um município a partir do nome e da UF.

        Retorna `ok=False` (com `errors`/`warnings`) se o município não for
        encontrado ou se o nome for ambíguo dentro da UF — propagando o
        mesmo comportamento de `LocalidadesService.obter_codigo_municipio`.
        """
        codigo = await self._localidades.obter_codigo_municipio(nome, uf)
        if not codigo.ok or codigo.data is None:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=codigo.metadata,
                warnings=codigo.warnings,
                errors=codigo.errors,
            )

        municipio_result = await self._localidades.obter_municipio_por_codigo(codigo.data)
        if not municipio_result.ok or municipio_result.data is None:
            return TypedToolResult(
                ok=False,
                data=None,
                metadata=municipio_result.metadata,
                warnings=municipio_result.warnings,
                errors=municipio_result.errors,
            )

        municipio = municipio_result.data
        raw = municipio.raw or {}

        municipio_perfil = MunicipioPerfil(
            codigo_ibge=municipio.id,
            nome=municipio.nome,
            uf_sigla=municipio.uf_sigla,
            uf_nome=municipio.uf_nome,
            regiao_nome=municipio.regiao_nome,
            microrregiao_ou_regiao_intermediaria=extrair_microrregiao_ou_regiao_intermediaria(raw),
        )

        warnings = list(municipio_result.warnings)
        fontes = [municipio_result.metadata.endpoint]
        indicadores: list[IndicadorPerfil] = []

        populacao = await self._agregados.consultar_populacao_municipio(codigo.data, ano=ano)
        fontes.append(populacao.metadata.endpoint)

        if populacao.ok:
            valores_disponiveis = [item for item in populacao.data if item.valor is not None]
            if valores_disponiveis:
                item = valores_disponiveis[0]
                indicadores.append(
                    IndicadorPerfil(
                        indicador="populacao_estimada",
                        valor=item.valor,
                        unidade=item.unidade,
                        periodo=item.periodo,
                        agregado_id=item.agregado_id,
                        variavel_id=item.variavel_id,
                    )
                )
                if ano is None:
                    warnings.append(
                        f'Nenhum "ano" foi informado para a população: retornado o '
                        f'período mais recente disponível no SIDRA ("{item.periodo}").'
                    )
            else:
                warnings.append(
                    "Indicador de população não disponível: o SIDRA não retornou um "
                    "valor para este município/período (dado ausente ou sigiloso)."
                )
        else:
            warnings.extend(populacao.warnings)
            warnings.append(
                "Indicador de população não pôde ser obtido: "
                + "; ".join(populacao.errors or ["erro desconhecido ao consultar o SIDRA."])
            )

        perfil = PerfilMunicipal(
            municipio=municipio_perfil,
            indicadores=indicadores,
            fontes=fontes,
            limitacoes=list(_LIMITACOES_BASE),
            proximos_indicadores_sugeridos=list(PROXIMOS_INDICADORES_SUGERIDOS),
        )

        metadata = municipio_result.metadata.model_copy(
            update={"params": {"nome": nome, "uf": uf, **municipio_result.metadata.params}}
        )

        return TypedToolResult(ok=True, data=perfil, metadata=metadata, warnings=warnings)
