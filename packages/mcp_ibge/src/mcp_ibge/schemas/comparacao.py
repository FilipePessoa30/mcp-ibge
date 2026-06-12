"""Modelos Pydantic para comparação de municípios (`comparar_municipios`)."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from .perfil import IndicadorPerfil


class MunicipioConsulta(BaseModel):
    """Um município a comparar, identificado por nome e UF."""

    model_config = ConfigDict(extra="forbid")

    nome: str
    uf: str


class MunicipioNaoResolvido(BaseModel):
    """Município que não pôde ser resolvido: não encontrado ou nome ambíguo na UF."""

    nome: str
    uf: str
    motivo: str


class MunicipioComparado(BaseModel):
    """Um município resolvido, com os indicadores efetivamente obtidos."""

    codigo_ibge: int
    nome: str
    uf_sigla: str | None = None
    uf_nome: str | None = None
    regiao_nome: str | None = None
    indicadores: list[IndicadorPerfil]


class ComparacaoMunicipios(BaseModel):
    """Resultado de `comparar_municipios`: tabela pronta para um agente apresentar.

    `municipios` contém apenas dados efetivamente obtidos do IBGE (nunca
    inventados). Municípios não encontrados ou ambíguos aparecem em
    `municipios_nao_resolvidos`, e indicadores solicitados que ainda não são
    suportados aparecem em `indicadores_nao_implementados` (apenas nomes,
    nunca dados).
    """

    municipios: list[MunicipioComparado]
    municipios_nao_resolvidos: list[MunicipioNaoResolvido]
    indicadores_consultados: list[str]
    indicadores_nao_implementados: list[str]
    fontes: list[str]
    limitacoes: list[str]
