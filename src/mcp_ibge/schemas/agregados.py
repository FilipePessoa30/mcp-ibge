"""Modelos Pydantic para a API de Agregados (SIDRA) do IBGE.

Assim como em `schemas.localidades`, usamos ``extra="allow"`` para preservar
campos adicionais retornados pela API sem precisar mapear toda a estrutura.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AgregadoResumo(BaseModel):
    """Referência resumida a um agregado dentro de uma pesquisa."""

    model_config = ConfigDict(extra="allow")

    id: int
    nome: str


class PesquisaAgregados(BaseModel):
    """Grupo de agregados pertencentes a uma mesma pesquisa (ex.: Censo)."""

    model_config = ConfigDict(extra="allow")

    id: str
    nome: str
    agregados: list[AgregadoResumo] = Field(default_factory=list)


class Variavel(BaseModel):
    """Uma variável (grandeza medida) dentro de um agregado."""

    model_config = ConfigDict(extra="allow")

    id: int
    nome: str
    unidade: str | None = None


class MetadadosAgregado(BaseModel):
    """Metadados completos de um agregado: variáveis, períodos e níveis territoriais."""

    model_config = ConfigDict(extra="allow")

    id: int
    nome: str
    variaveis: list[Variavel] = Field(default_factory=list)
