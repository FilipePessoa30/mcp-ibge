"""Modelos Pydantic para a API de Localidades do IBGE.

Os modelos usam ``extra="allow"`` porque a API do IBGE retorna estruturas
aninhadas ricas (mesorregião, microrregião, região imediata, etc.) que não
precisamos tipar por completo: validamos os campos que usamos e preservamos
o restante como veio da API.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class RegiaoResumida(BaseModel):
    """Referência resumida a uma grande região (usada dentro de `Estado`)."""

    model_config = ConfigDict(extra="allow")

    id: int
    sigla: str | None = None
    nome: str | None = None


class Regiao(BaseModel):
    """Uma das 5 grandes regiões geográficas do Brasil."""

    model_config = ConfigDict(extra="allow")

    id: int
    sigla: str
    nome: str


class Estado(BaseModel):
    """Unidade federativa (estado ou Distrito Federal)."""

    model_config = ConfigDict(extra="allow")

    id: int
    sigla: str
    nome: str
    regiao: RegiaoResumida | None = None


class Municipio(BaseModel):
    """Município brasileiro, identificado pelo código IBGE de 7 dígitos."""

    model_config = ConfigDict(extra="allow")

    id: int
    nome: str
