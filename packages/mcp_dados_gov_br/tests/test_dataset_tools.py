"""Testes de contrato das tools MCP de datasets: existência e formato JSON."""

from __future__ import annotations

import httpx
import respx

from mcp_dados_gov_br.config import get_settings
from mcp_dados_gov_br.server import mcp

from .conftest import assert_envelope_contract

BASE_URL = get_settings().api_base_url

DATASET_TOOLS = {
    "buscar_datasets",
    "obter_dataset",
    "listar_recursos_dataset",
    "sugerir_datasets_para_pergunta",
}

DATASET_SUMMARY_RAW = {
    "id": "dataset-educacao-2024",
    "name": "dataset-educacao-2024",
    "title": "Dados de Educação 2024",
    "notes": "Microdados do censo escolar.",
    "organization": {"id": "org-mec", "name": "mec", "title": "Ministério da Educação"},
    "tags": [{"name": "educacao"}],
    "groups": [],
    "num_resources": 1,
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


def _ckan_ok(result: object) -> httpx.Response:
    return httpx.Response(200, json={"success": True, "result": result})


async def test_todas_as_tools_de_datasets_estao_registradas():
    tools = await mcp.list_tools()
    nomes = {tool.name for tool in tools}

    assert DATASET_TOOLS.issubset(nomes)


@respx.mock
async def test_buscar_datasets_retorna_contrato_json():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 1, "results": [DATASET_SUMMARY_RAW]})
    )

    _, structured = await mcp.call_tool("buscar_datasets", {"query": "educação", "limite": 5})

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert len(structured["data"]) == 1
    assert structured["data"][0]["id"] == "dataset-educacao-2024"
    assert structured["metadata"]["params"] == {"q": "educação", "rows": 5}


@respx.mock
async def test_obter_dataset_retorna_contrato_json():
    respx.get(f"{BASE_URL}/package_show").mock(return_value=_ckan_ok(DATASET_FULL_RAW))

    _, structured = await mcp.call_tool(
        "obter_dataset", {"dataset_id": "dataset-educacao-2024"}
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"]["id"] == "dataset-educacao-2024"
    assert len(structured["data"]["resources"]) == 1


@respx.mock
async def test_listar_recursos_dataset_retorna_contrato_json():
    respx.get(f"{BASE_URL}/package_show").mock(return_value=_ckan_ok(DATASET_FULL_RAW))

    _, structured = await mcp.call_tool(
        "listar_recursos_dataset", {"dataset_id": "dataset-educacao-2024"}
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"][0]["format"] == "CSV"


@respx.mock
async def test_sugerir_datasets_para_pergunta_retorna_contrato_json():
    respx.get(f"{BASE_URL}/package_search").mock(
        return_value=_ckan_ok({"count": 1, "results": [DATASET_SUMMARY_RAW]})
    )

    _, structured = await mcp.call_tool(
        "sugerir_datasets_para_pergunta",
        {"pergunta": "Quais dados existem sobre educação no Brasil?", "limite": 5},
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert len(structured["data"]) == 1
    assert "educação" in structured["metadata"]["params"]["keywords"]


async def test_sugerir_datasets_para_pergunta_sem_palavras_chave_retorna_aviso():
    _, structured = await mcp.call_tool(
        "sugerir_datasets_para_pergunta", {"pergunta": "e os de para com", "limite": 5}
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is True
    assert structured["data"] == []
    assert structured["warnings"]


@respx.mock
async def test_obter_dataset_nao_encontrado_retorna_erro_no_contrato():
    respx.get(f"{BASE_URL}/package_show").mock(
        return_value=httpx.Response(
            200,
            json={
                "success": False,
                "error": {"__type": "Not Found Error", "message": "Package not found"},
            },
        )
    )

    _, structured = await mcp.call_tool(
        "obter_dataset", {"dataset_id": "dataset-inexistente"}
    )

    assert_envelope_contract(structured)
    assert structured["ok"] is False
    assert structured["data"] is None
    assert structured["errors"]
