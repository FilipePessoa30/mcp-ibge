"""Modelos Pydantic para a API de Localidades do IBGE.

Os modelos usam ``extra="allow"`` porque a API do IBGE retorna estruturas
aninhadas ricas (mesorregião, microrregião, região imediata, etc.) que não
precisamos tipar por completo: validamos os campos que usamos e preservamos
o restante como veio da API.
"""

from __future__ import annotations

from typing import Any

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


class Region(BaseModel):
    """Uma das 5 grandes regiões geográficas do Brasil (nomes em inglês)."""

    model_config = ConfigDict(extra="allow")

    id: int
    sigla: str | None = None
    nome: str


class State(BaseModel):
    """Unidade federativa (estado ou Distrito Federal), nomes em inglês."""

    model_config = ConfigDict(extra="allow")

    id: int
    sigla: str
    nome: str
    regiao: Region | None = None


class Municipality(BaseModel):
    """Município brasileiro com a UF/região "achatadas" e o JSON bruto da API.

    Pensado para conversões a partir do JSON retornado por
    `/municipios` ou `/municipios/{id}`, que traz a UF e a região aninhadas em
    `microrregiao.mesorregiao.UF` (ou `regiao-imediata.regiao-intermediaria.UF`).
    """

    model_config = ConfigDict(extra="allow")

    id: int
    nome: str
    uf_id: int | None = None
    uf_sigla: str | None = None
    uf_nome: str | None = None
    regiao_nome: str | None = None
    raw: dict[str, Any] | None = None


class District(BaseModel):
    """Distrito de um município, com o município "achatado" e o JSON bruto."""

    model_config = ConfigDict(extra="allow")

    id: int
    nome: str
    municipio_id: int | None = None
    municipio_nome: str | None = None
    raw: dict[str, Any] | None = None


def region_from_raw(data: dict[str, Any]) -> Region:
    """Converte um item bruto de `/regioes` (ou `estado.regiao`) em `Region`."""
    return Region(id=data["id"], sigla=data.get("sigla"), nome=data["nome"])


def state_from_raw(data: dict[str, Any]) -> State:
    """Converte um item bruto de `/estados` (ou `/estados/{uf}`) em `State`."""
    regiao = data.get("regiao")
    return State(
        id=data["id"],
        sigla=data["sigla"],
        nome=data["nome"],
        regiao=region_from_raw(regiao) if regiao else None,
    )


def _extract_uf(data: dict[str, Any]) -> dict[str, Any] | None:
    """Localiza o objeto "UF" dentro do JSON bruto de um município, se houver."""
    microrregiao = data.get("microrregiao") or {}
    mesorregiao = microrregiao.get("mesorregiao") or {}
    uf = mesorregiao.get("UF")
    if uf:
        return uf

    regiao_imediata = data.get("regiao-imediata") or {}
    regiao_intermediaria = regiao_imediata.get("regiao-intermediaria") or {}
    return regiao_intermediaria.get("UF")


def municipality_from_raw(data: dict[str, Any]) -> Municipality:
    """Converte um item bruto de `/municipios` (ou `/municipios/{id}`) em `Municipality`.

    Extrai sigla/nome da UF e nome da região de dentro da estrutura aninhada
    da API e preserva o JSON original em `raw`.
    """
    uf = _extract_uf(data) or {}
    regiao = uf.get("regiao") or {}
    return Municipality(
        id=data["id"],
        nome=data["nome"],
        uf_id=uf.get("id"),
        uf_sigla=uf.get("sigla"),
        uf_nome=uf.get("nome"),
        regiao_nome=regiao.get("nome"),
        raw=data,
    )


def district_from_raw(data: dict[str, Any]) -> District:
    """Converte um item bruto de `/municipios/{id}/distritos` em `District`."""
    municipio = data.get("municipio") or {}
    return District(
        id=data["id"],
        nome=data["nome"],
        municipio_id=municipio.get("id"),
        municipio_nome=municipio.get("nome"),
        raw=data,
    )
