"""Testes de integração das tools do servidor MCP (com HTTP mockado)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge import server
from mcp_ibge.config import AGREGADOS_BASE_URL, LOCALIDADES_BASE_URL
from mcp_ibge.errors import IBGERequestError

REGIOES = [{"id": 1, "sigla": "N", "nome": "Norte"}]


@respx.mock
async def test_listar_regioes_envelope_de_sucesso():
    respx.get(f"{LOCALIDADES_BASE_URL}/regioes").mock(
        return_value=httpx.Response(200, json=REGIOES)
    )

    response = await server.listar_regioes()

    assert response["data"] == REGIOES

    metadata = response["metadata"]
    assert metadata["source_name"] == "IBGE - Instituto Brasileiro de Geografia e Estatística"
    assert metadata["source_url"] == f"{LOCALIDADES_BASE_URL}/regioes"
    assert metadata["endpoint"] == f"{LOCALIDADES_BASE_URL}/regioes"
    assert metadata["params"] == {}
    assert "retrieved_at" in metadata
    assert "error" not in response


@respx.mock
async def test_obter_municipio_propaga_parametros():
    municipio = {"id": 3550308, "nome": "São Paulo"}
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3550308").mock(
        return_value=httpx.Response(200, json=municipio)
    )

    response = await server.obter_municipio(codigo="3550308")

    assert response["data"] == municipio
    assert response["metadata"]["params"] == {"codigo": "3550308"}


@respx.mock
async def test_envelope_de_erro_em_falha_http():
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/0000000").mock(
        return_value=httpx.Response(404, json={"detail": "not found"})
    )

    response = await server.obter_municipio(codigo="0000000")

    assert "error" in response
    assert "data" not in response
    assert response["metadata"]["params"] == {"codigo": "0000000"}


async def test_envelope_de_erro_inesperado(monkeypatch):
    async def _quebrado(*_args, **_kwargs):
        raise RuntimeError("falha inesperada")

    monkeypatch.setattr(server.localidades, "listar_regioes", _quebrado)

    response = await server.listar_regioes()

    assert "error" in response
    assert "falha inesperada" in response["error"]


@respx.mock
async def test_consultar_dados_agregado_propaga_localidades_resolvidas():
    dados = [{"id": "9324", "resultados": []}]
    respx.get(f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324").mock(
        return_value=httpx.Response(200, json=dados)
    )

    response = await server.consultar_dados_agregado(
        agregado_id=6579, variaveis="9324", localidades="BR"
    )

    assert response["data"] == dados
    assert response["metadata"]["params"]["localidades"] == "N1[all]"


@respx.mock
async def test_obter_populacao_municipio_envelope():
    endpoint = f"{AGREGADOS_BASE_URL}/6579/periodos/-1/variaveis/9324"
    dados = [{"id": "9324", "resultados": []}]
    respx.get(endpoint).mock(return_value=httpx.Response(200, json=dados))

    response = await server.obter_populacao_municipio(codigo_municipio="4205407")

    assert response["data"] == dados
    assert response["metadata"]["endpoint"] == endpoint
    assert response["metadata"]["params"]["codigo_municipio"] == "4205407"


def test_ibge_request_error_carrega_url_e_status():
    erro = IBGERequestError("boom", url="https://example.com", status_code=500)
    assert erro.url == "https://example.com"
    assert erro.status_code == 500
