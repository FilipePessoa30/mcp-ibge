"""Modelos Pydantic para o perfil básico de um município (`gerar_perfil_municipal`)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


class MicrorregiaoOuRegiaoIntermediaria(BaseModel):
    """Microrregião (estrutura antiga) ou região intermediária (estrutura nova) do IBGE.

    A API de Localidades do IBGE descreve a subdivisão regional de um
    município de duas formas, dependendo da versão/endpoint: `microrregiao`
    (com `mesorregiao.UF`) ou `regiao-imediata.regiao-intermediaria` (com
    `UF`). `tipo` indica qual delas foi encontrada.
    """

    model_config = ConfigDict(extra="allow")

    tipo: Literal["microrregiao", "regiao-intermediaria"]
    id: int | None = None
    nome: str | None = None


class MunicipioPerfil(BaseModel):
    """Identificação de um município no perfil municipal."""

    codigo_ibge: int
    nome: str
    uf_sigla: str | None = None
    uf_nome: str | None = None
    regiao_nome: str | None = None
    microrregiao_ou_regiao_intermediaria: MicrorregiaoOuRegiaoIntermediaria | None = None


class IndicadorPerfil(BaseModel):
    """Um indicador obtido para o perfil municipal: dado real, com fonte rastreável."""

    model_config = ConfigDict(extra="allow")

    indicador: str
    valor: float | str | None
    unidade: str | None = None
    periodo: str | None = None
    agregado_id: str | None = None
    variavel_id: str | None = None


class PerfilMunicipal(BaseModel):
    """Perfil básico de um município: identificação + indicadores disponíveis.

    `indicadores` contém apenas dados efetivamente obtidos do IBGE (nunca
    inventados). `proximos_indicadores_sugeridos` lista nomes de indicadores
    ainda não implementados por este servidor — são apenas sugestões, não
    dados.
    """

    municipio: MunicipioPerfil
    indicadores: list[IndicadorPerfil]
    fontes: list[str]
    limitacoes: list[str]
    proximos_indicadores_sugeridos: list[str]


def extrair_microrregiao_ou_regiao_intermediaria(
    data: dict[str, Any],
) -> MicrorregiaoOuRegiaoIntermediaria | None:
    """Extrai a microrregião ou região intermediária do JSON bruto de um município.

    A API do IBGE usa `microrregiao` (estrutura mais antiga, com
    `mesorregiao.UF`) ou `regiao-imediata.regiao-intermediaria` (estrutura
    mais nova), dependendo da versão/endpoint consultado. Retorna `None` se
    nenhuma das duas estiver presente.
    """
    microrregiao = data.get("microrregiao")
    if microrregiao:
        return MicrorregiaoOuRegiaoIntermediaria(
            tipo="microrregiao", id=microrregiao.get("id"), nome=microrregiao.get("nome")
        )

    regiao_imediata = data.get("regiao-imediata") or {}
    regiao_intermediaria = regiao_imediata.get("regiao-intermediaria")
    if regiao_intermediaria:
        return MicrorregiaoOuRegiaoIntermediaria(
            tipo="regiao-intermediaria",
            id=regiao_intermediaria.get("id"),
            nome=regiao_intermediaria.get("nome"),
        )

    return None
