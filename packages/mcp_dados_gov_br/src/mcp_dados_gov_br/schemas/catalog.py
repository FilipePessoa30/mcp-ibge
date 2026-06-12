"""Modelos Pydantic para o catálogo CKAN do dados.gov.br.

A API CKAN retorna estruturas JSON ricas, com muitos campos internos que não
são úteis para um agente (`revision_id`, `state`, `type`, flags internas,
...). Os modelos abaixo usam ``extra="allow"`` e tipam apenas os campos mais
relevantes para descoberta/uso de datasets — o restante do JSON original é
preservado como atributos extras, mas não é removido nem inventado.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class OrganizationRef(BaseModel):
    """Referência resumida a uma organização (usada dentro de `Dataset`)."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str | None = None
    title: str | None = None


class Resource(BaseModel):
    """Um recurso (arquivo/link) associado a um dataset (CSV, JSON, API, PDF, ...)."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str | None = None
    description: str | None = None
    format: str | None = None
    url: str | None = None
    mimetype: str | None = None
    size: int | None = None
    created: str | None = None
    last_modified: str | None = None


class DatasetSummary(BaseModel):
    """Resumo de um dataset, como retornado por `package_search`."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    title: str | None = None
    notes: str | None = None
    organization: OrganizationRef | None = None
    tags: list[str] = Field(default_factory=list)
    groups: list[str] = Field(default_factory=list)
    num_resources: int | None = None
    license_id: str | None = None
    license_title: str | None = None
    metadata_created: str | None = None
    metadata_modified: str | None = None


class Dataset(DatasetSummary):
    """Detalhes completos de um dataset, incluindo seus recursos (`package_show`)."""

    resources: list[Resource] = Field(default_factory=list)


class Organization(BaseModel):
    """Organização publicadora de datasets."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    title: str | None = None
    description: str | None = None
    image_url: str | None = None
    package_count: int | None = None


class Group(BaseModel):
    """Grupo temático do catálogo."""

    model_config = ConfigDict(extra="allow")

    id: str
    name: str
    title: str | None = None
    description: str | None = None
    package_count: int | None = None


class Tag(BaseModel):
    """Tag associada a datasets."""

    model_config = ConfigDict(extra="allow")

    id: str | None = None
    name: str


def organization_ref_from_raw(data: dict[str, Any]) -> OrganizationRef:
    """Converte o objeto `organization` aninhado em um dataset em `OrganizationRef`."""
    return OrganizationRef(id=data.get("id"), name=data.get("name"), title=data.get("title"))


def resource_from_raw(data: dict[str, Any]) -> Resource:
    """Converte um item de `package_show().resources` em `Resource`."""
    return Resource(
        id=data["id"],
        name=data.get("name"),
        description=data.get("description"),
        format=data.get("format"),
        url=data.get("url"),
        mimetype=data.get("mimetype"),
        size=data.get("size"),
        created=data.get("created"),
        last_modified=data.get("last_modified"),
    )


def _tag_names_from_raw(data: dict[str, Any]) -> list[str]:
    return [tag.get("name", "") for tag in data.get("tags", []) if tag.get("name")]


def _group_names_from_raw(data: dict[str, Any]) -> list[str]:
    return [group.get("name", "") for group in data.get("groups", []) if group.get("name")]


def dataset_summary_from_raw(data: dict[str, Any]) -> DatasetSummary:
    """Converte um item de `package_search().results` em `DatasetSummary`."""
    organization = data.get("organization")
    return DatasetSummary(
        id=data["id"],
        name=data["name"],
        title=data.get("title"),
        notes=data.get("notes"),
        organization=organization_ref_from_raw(organization) if organization else None,
        tags=_tag_names_from_raw(data),
        groups=_group_names_from_raw(data),
        num_resources=data.get("num_resources", len(data.get("resources", []))),
        license_id=data.get("license_id"),
        license_title=data.get("license_title"),
        metadata_created=data.get("metadata_created"),
        metadata_modified=data.get("metadata_modified"),
    )


def dataset_from_raw(data: dict[str, Any]) -> Dataset:
    """Converte o resultado de `package_show` em `Dataset`, incluindo `resources`."""
    summary = dataset_summary_from_raw(data)
    return Dataset(
        **summary.model_dump(),
        resources=[resource_from_raw(item) for item in data.get("resources", [])],
    )


def organization_from_raw(data: dict[str, Any]) -> Organization:
    """Converte um item de `organization_list`/`organization_show` em `Organization`."""
    return Organization(
        id=data["id"],
        name=data["name"],
        title=data.get("title"),
        description=data.get("description"),
        image_url=data.get("image_url"),
        package_count=data.get("package_count"),
    )


def group_from_raw(data: dict[str, Any]) -> Group:
    """Converte um item de `group_list` em `Group`."""
    return Group(
        id=data["id"],
        name=data["name"],
        title=data.get("title"),
        description=data.get("description"),
        package_count=data.get("package_count"),
    )


def tag_from_raw(item: Any) -> Tag:
    """Converte um item de `tag_search().results` em `Tag`.

    A API CKAN pode retornar `results` como uma lista de strings (apenas o
    nome da tag) ou de dicionários (`{"id": ..., "name": ..., ...}`),
    dependendo da configuração do portal/vocabulário.
    """
    if isinstance(item, str):
        return Tag(name=item)
    return Tag(id=item.get("id"), name=item["name"])
