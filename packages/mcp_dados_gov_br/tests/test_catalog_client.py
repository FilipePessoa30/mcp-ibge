"""Testes do cliente "fino" `CatalogClient`/`AsyncCkanClient` (sem regras de negócio)."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_dados_gov_br.clients.catalog import CatalogClient
from mcp_dados_gov_br.config import get_settings
from mcp_dados_gov_br.utils.errors import (
    CkanAuthRequiredError,
    CkanClientError,
    CkanNotFoundError,
    CkanRateLimitError,
    CkanServerError,
    CkanValidationError,
)

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
async def test_package_search():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 1, "results": [DATASET_SUMMARY_RAW]})
    )

    client = CatalogClient()
    result = await client.package_search("educação", 10)

    assert result.data == {"count": 1, "results": [DATASET_SUMMARY_RAW]}
    assert result.endpoint == f"{BASE_URL}/package_search"
    assert result.params == {"q": "educação", "rows": 10}
    assert result.cache_hit is False


@respx.mock
async def test_package_show():
    respx.get(f"{BASE_URL}/package_show").mock(return_value=_ckan_ok(DATASET_FULL_RAW))

    client = CatalogClient()
    result = await client.package_show("dataset-educacao-2024")

    assert result.data == DATASET_FULL_RAW
    assert result.params == {"id": "dataset-educacao-2024"}


@respx.mock
async def test_organization_list():
    respx.get(f"{BASE_URL}/organization_list").mock(return_value=_ckan_ok([ORGANIZATION_RAW]))

    client = CatalogClient()
    result = await client.organization_list(10)

    assert result.data == [ORGANIZATION_RAW]
    assert result.params == {"all_fields": "true", "limit": 10}


@respx.mock
async def test_organization_autocomplete():
    autocomplete_result = [{"id": "org-mec", "name": "mec", "title": "Ministério da Educação"}]
    respx.get(f"{BASE_URL}/organization_autocomplete").mock(
        return_value=_ckan_ok(autocomplete_result)
    )

    client = CatalogClient()
    result = await client.organization_autocomplete("educação", 10)

    assert result.data == autocomplete_result
    assert result.params == {"q": "educação", "limit": 10}


@respx.mock
async def test_organization_show():
    respx.get(f"{BASE_URL}/organization_show").mock(return_value=_ckan_ok(ORGANIZATION_RAW))

    client = CatalogClient()
    result = await client.organization_show("org-mec")

    assert result.data == ORGANIZATION_RAW
    assert result.params == {"id": "org-mec", "include_datasets": "false"}


@respx.mock
async def test_group_list():
    respx.get(f"{BASE_URL}/group_list").mock(return_value=_ckan_ok([GROUP_RAW]))

    client = CatalogClient()
    result = await client.group_list(20)

    assert result.data == [GROUP_RAW]
    assert result.params == {"all_fields": "true", "limit": 20}


@respx.mock
async def test_tag_search():
    tag_result = {"count": 2, "results": ["saude", {"id": "tag-1", "name": "educacao"}]}
    respx.get(f"{BASE_URL}/tag_search").mock(return_value=_ckan_ok(tag_result))

    client = CatalogClient()
    result = await client.tag_search("edu", 20)

    assert result.data == tag_result
    assert result.params == {"query": "edu", "limit": 20}


@respx.mock
async def test_cache_hit_evita_segunda_requisicao():
    route = respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 0, "results": []})
    )

    client = CatalogClient()
    primeira = await client.package_search("educação", 10)
    segunda = await client.package_search("educação", 10)

    assert primeira.cache_hit is False
    assert segunda.cache_hit is True
    assert segunda.data == primeira.data
    assert route.call_count == 1


@respx.mock
async def test_http_404_levanta_ckan_not_found_error():
    respx.get(f"{BASE_URL}/package_show").mock(return_value=httpx.Response(404))

    client = CatalogClient()
    with pytest.raises(CkanNotFoundError):
        await client.package_show("dataset-inexistente")


@respx.mock
async def test_http_429_levanta_ckan_rate_limit_error():
    respx.get(f"{BASE_URL}/package_search").mock(return_value=httpx.Response(429))

    client = CatalogClient()
    with pytest.raises(CkanRateLimitError):
        await client.package_search("educação", 10)


@respx.mock
async def test_http_500_levanta_ckan_server_error():
    respx.get(f"{BASE_URL}/package_search").mock(return_value=httpx.Response(500))

    client = CatalogClient()
    with pytest.raises(CkanServerError):
        await client.package_search("educação", 10)


@respx.mock
async def test_http_401_sem_token_levanta_ckan_auth_required_error():
    respx.get(f"{BASE_URL}/organization_show").mock(return_value=httpx.Response(401))

    client = CatalogClient()
    with pytest.raises(CkanAuthRequiredError) as exc_info:
        await client.organization_show("org-privada")

    assert "DADOS_GOV_BR_API_TOKEN" in str(exc_info.value)


@respx.mock
async def test_corpo_success_false_not_found_error():
    respx.get(f"{BASE_URL}/package_show").mock(
        return_value=_ckan_error("Not Found Error", "Package not found")
    )

    client = CatalogClient()
    with pytest.raises(CkanNotFoundError):
        await client.package_show("dataset-inexistente")


@respx.mock
async def test_corpo_success_false_validation_error():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_error("Validation Error", "q é obrigatório")
    )

    client = CatalogClient()
    with pytest.raises(CkanValidationError):
        await client.package_search("educação", 10)


@respx.mock
async def test_corpo_success_false_authorization_error_sem_token_configurado():
    respx.get(f"{BASE_URL}/organization_show").mock(
        return_value=_ckan_error("Authorization Error", "Access denied")
    )

    client = CatalogClient()
    with pytest.raises(CkanAuthRequiredError) as exc_info:
        await client.organization_show("org-privada")

    mensagem = str(exc_info.value)
    assert "Configure a variável de ambiente DADOS_GOV_BR_API_TOKEN" in mensagem


@respx.mock
async def test_corpo_success_false_authorization_error_com_token_configurado(monkeypatch):
    monkeypatch.setenv("DADOS_GOV_BR_API_TOKEN", "minha-chave-secreta")
    get_settings.cache_clear()
    try:
        respx.get(f"{BASE_URL}/organization_show").mock(
            return_value=_ckan_error("Authorization Error", "Access denied")
        )

        client = CatalogClient()
        with pytest.raises(CkanAuthRequiredError) as exc_info:
            await client.organization_show("org-privada")

        mensagem = str(exc_info.value)
        assert "token configurado em DADOS_GOV_BR_API_TOKEN" in mensagem
    finally:
        get_settings.cache_clear()


@respx.mock
async def test_token_enviado_no_header_authorization(monkeypatch):
    monkeypatch.setenv("DADOS_GOV_BR_API_TOKEN", "minha-chave-secreta")
    get_settings.cache_clear()
    try:
        route = respx.get(f"{BASE_URL}/package_search").mock(
            return_value=_ckan_ok({"count": 0, "results": []})
        )

        client = CatalogClient()
        await client.package_search("educação", 10)

        assert route.calls.last.request.headers["Authorization"] == "minha-chave-secreta"
    finally:
        get_settings.cache_clear()


@respx.mock
async def test_sem_token_configurado_nao_envia_header_authorization():
    route = respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 0, "results": []})
    )

    client = CatalogClient()
    await client.package_search("educação", 10)

    assert "Authorization" not in route.calls.last.request.headers


@respx.mock
async def test_resposta_json_invalida_levanta_ckan_server_error():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=httpx.Response(200, content=b"isto nao e json")
    )

    client = CatalogClient()
    with pytest.raises(CkanServerError):
        await client.package_search("educação", 10)


@respx.mock
async def test_timeout_levanta_ckan_client_error():
    respx.get(f"{BASE_URL}/package_search").mock(side_effect=httpx.TimeoutException("timeout"))

    client = CatalogClient()
    with pytest.raises(CkanClientError):
        await client.package_search("educação", 10)
