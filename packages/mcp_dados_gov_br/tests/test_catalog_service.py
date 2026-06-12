"""Testes da camada de serviço `CatalogService` (conversões, validação, sugestões)."""

from __future__ import annotations

import httpx
import respx

from mcp_dados_gov_br.config import get_settings
from mcp_dados_gov_br.services.catalog_service import CatalogService

BASE_URL = get_settings().api_base_url

DATASET_SUMMARY_RAW = {
    "id": "dataset-educacao-2024",
    "name": "dataset-educacao-2024",
    "title": "Dados de Educação 2024",
    "notes": "Microdados do censo escolar.",
    "organization": {"id": "org-mec", "name": "mec", "title": "Ministério da Educação"},
    "tags": [{"name": "educacao"}, {"name": "censo-escolar"}],
    "groups": [{"name": "educacao"}],
    "num_resources": 2,
    "license_id": "cc-by",
    "license_title": "Creative Commons Attribution",
    "metadata_created": "2024-01-10T12:00:00",
    "metadata_modified": "2024-02-01T08:30:00",
}

DATASET_FULL_RAW = {
    **DATASET_SUMMARY_RAW,
    "resources": [
        {
            "id": "recurso-1",
            "name": "Microdados CSV",
            "description": "Arquivo CSV completo.",
            "format": "CSV",
            "url": "https://dados.gov.br/dataset/educacao-2024/resource/recurso-1",
            "mimetype": "text/csv",
            "size": 123456,
            "created": "2024-01-10T12:00:00",
            "last_modified": "2024-02-01T08:30:00",
        },
    ],
}

ORGANIZATION_RAW = {
    "id": "org-mec",
    "name": "mec",
    "title": "Ministério da Educação",
    "description": "Órgão responsável pela política educacional.",
    "image_url": "https://dados.gov.br/images/mec.png",
    "package_count": 42,
}

GROUP_RAW = {
    "id": "grupo-educacao",
    "name": "educacao",
    "title": "Educação",
    "description": "Datasets sobre educação.",
    "package_count": 10,
}


def _ckan_ok(result: object) -> httpx.Response:
    return httpx.Response(200, json={"success": True, "result": result})


def _ckan_error(tipo: str, mensagem: str) -> httpx.Response:
    return httpx.Response(
        200, json={"success": False, "error": {"__type": tipo, "message": mensagem}}
    )


@respx.mock
async def test_buscar_datasets_retorna_resumos():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 1, "results": [DATASET_SUMMARY_RAW]})
    )

    result = await CatalogService().buscar_datasets("educação", limite=10)

    assert result.ok is True
    assert len(result.data) == 1
    assert result.data[0].id == "dataset-educacao-2024"
    assert result.data[0].organization is not None
    assert result.data[0].organization.title == "Ministério da Educação"
    assert result.data[0].tags == ["educacao", "censo-escolar"]
    assert result.metadata.params == {"q": "educação", "rows": 10}


async def test_buscar_datasets_query_vazia_retorna_erro_de_validacao():
    result = await CatalogService().buscar_datasets("   ", limite=10)

    assert result.ok is False
    assert result.data == []
    assert result.errors
    assert "não pode ser vazio" in result.errors[0]


async def test_buscar_datasets_limite_invalido_retorna_erro_de_validacao():
    result = await CatalogService().buscar_datasets("educação", limite=0)

    assert result.ok is False
    assert result.data == []
    assert "Limite inválido" in result.errors[0]


@respx.mock
async def test_obter_dataset_retorna_dataset_com_recursos():
    respx.get(f"{BASE_URL}/package_show").mock(return_value=_ckan_ok(DATASET_FULL_RAW))

    result = await CatalogService().obter_dataset("dataset-educacao-2024")

    assert result.ok is True
    assert result.data is not None
    assert result.data.id == "dataset-educacao-2024"
    assert len(result.data.resources) == 1
    assert result.data.resources[0].format == "CSV"


@respx.mock
async def test_obter_dataset_nao_encontrado_retorna_erro():
    respx.get(f"{BASE_URL}/package_show").mock(
        return_value=_ckan_error("Not Found Error", "Package not found")
    )

    result = await CatalogService().obter_dataset("dataset-inexistente")

    assert result.ok is False
    assert result.data is None
    assert result.errors


async def test_obter_dataset_id_vazio_retorna_erro_de_validacao():
    result = await CatalogService().obter_dataset("")

    assert result.ok is False
    assert result.data is None
    assert "não pode ser vazio" in result.errors[0]


@respx.mock
async def test_listar_recursos_dataset_retorna_recursos():
    respx.get(f"{BASE_URL}/package_show").mock(return_value=_ckan_ok(DATASET_FULL_RAW))

    result = await CatalogService().listar_recursos_dataset("dataset-educacao-2024")

    assert result.ok is True
    assert len(result.data) == 1
    assert result.data[0].id == "recurso-1"
    assert result.data[0].url == "https://dados.gov.br/dataset/educacao-2024/resource/recurso-1"


@respx.mock
async def test_listar_recursos_dataset_sem_recursos_retorna_lista_vazia():
    dataset_sem_recursos = {**DATASET_SUMMARY_RAW, "resources": []}
    respx.get(f"{BASE_URL}/package_show").mock(return_value=_ckan_ok(dataset_sem_recursos))

    result = await CatalogService().listar_recursos_dataset("dataset-educacao-2024")

    assert result.ok is True
    assert result.data == []


@respx.mock
async def test_buscar_organizacoes_com_query_usa_autocomplete():
    autocomplete_result = [{"id": "org-mec", "name": "mec", "title": "Ministério da Educação"}]
    respx.get(f"{BASE_URL}/organization_autocomplete").mock(
        return_value=_ckan_ok(autocomplete_result)
    )

    result = await CatalogService().buscar_organizacoes("educação", limite=10)

    assert result.ok is True
    assert len(result.data) == 1
    assert result.data[0].name == "mec"
    assert result.metadata.endpoint == f"{BASE_URL}/organization_autocomplete"
    assert result.metadata.params == {"q": "educação", "limit": 10}


@respx.mock
async def test_buscar_organizacoes_sem_query_usa_organization_list():
    respx.get(f"{BASE_URL}/organization_list").mock(return_value=_ckan_ok([ORGANIZATION_RAW]))

    result = await CatalogService().buscar_organizacoes(None, limite=10)

    assert result.ok is True
    assert len(result.data) == 1
    assert result.data[0].name == "mec"
    assert result.metadata.endpoint == f"{BASE_URL}/organization_list"
    assert result.metadata.params == {"all_fields": "true", "limit": 10}


@respx.mock
async def test_obter_organizacao_retorna_detalhes():
    respx.get(f"{BASE_URL}/organization_show").mock(return_value=_ckan_ok(ORGANIZATION_RAW))

    result = await CatalogService().obter_organizacao("org-mec")

    assert result.ok is True
    assert result.data is not None
    assert result.data.title == "Ministério da Educação"
    assert result.data.package_count == 42


@respx.mock
async def test_listar_grupos_retorna_grupos():
    respx.get(f"{BASE_URL}/group_list").mock(return_value=_ckan_ok([GROUP_RAW]))

    result = await CatalogService().listar_grupos(limite=20)

    assert result.ok is True
    assert len(result.data) == 1
    assert result.data[0].name == "educacao"


@respx.mock
async def test_buscar_tags_com_resultados_mistos():
    tag_result = {"count": 2, "results": ["saude", {"id": "tag-1", "name": "educacao"}]}
    respx.get(f"{BASE_URL}/tag_search").mock(return_value=_ckan_ok(tag_result))

    result = await CatalogService().buscar_tags("e", limite=20)

    assert result.ok is True
    assert [tag.name for tag in result.data] == ["saude", "educacao"]
    assert result.data[0].id is None
    assert result.data[1].id == "tag-1"


@respx.mock
async def test_sugerir_datasets_para_pergunta_extrai_palavras_chave_e_busca():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 1, "results": [DATASET_SUMMARY_RAW]})
    )

    result = await CatalogService().sugerir_datasets_para_pergunta(
        "Quais dados existem sobre desmatamento na Amazônia?", limite=5
    )

    assert result.ok is True
    assert len(result.data) == 1
    pergunta = "Quais dados existem sobre desmatamento na Amazônia?"
    assert result.metadata.params["pergunta"] == pergunta
    assert "desmatamento" in result.metadata.params["keywords"]
    assert "amazônia" in result.metadata.params["keywords"]
    assert result.metadata.params["q"] == " ".join(result.metadata.params["keywords"])


async def test_sugerir_datasets_para_pergunta_sem_palavras_chave_retorna_aviso():
    result = await CatalogService().sugerir_datasets_para_pergunta("e os de para com", limite=5)

    assert result.ok is True
    assert result.data == []
    assert result.warnings
    assert "Não foi possível extrair palavras-chave" in result.warnings[0]


async def test_sugerir_datasets_para_pergunta_vazia_retorna_erro_de_validacao():
    result = await CatalogService().sugerir_datasets_para_pergunta("   ", limite=5)

    assert result.ok is False
    assert result.data == []
    assert "não pode ser vazio" in result.errors[0]
