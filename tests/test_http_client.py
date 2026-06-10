"""Testes do cliente HTTP assíncrono: cache, timeout e tratamento de erros."""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.errors import IBGERequestError
from mcp_ibge.http_client import get_json

URL = "https://servicodados.ibge.gov.br/api/v1/localidades/regioes"


@respx.mock
async def test_get_json_sucesso():
    route = respx.get(URL).mock(return_value=httpx.Response(200, json=[{"id": 1}]))

    data = await get_json(URL)

    assert data == [{"id": 1}]
    assert route.call_count == 1


@respx.mock
async def test_get_json_usa_cache():
    route = respx.get(URL).mock(return_value=httpx.Response(200, json=[{"id": 1}]))

    primeiro = await get_json(URL)
    segundo = await get_json(URL)

    assert primeiro == segundo
    assert route.call_count == 1


@respx.mock
async def test_get_json_use_cache_false_ignora_cache():
    route = respx.get(URL).mock(return_value=httpx.Response(200, json=[{"id": 1}]))

    await get_json(URL, use_cache=False)
    await get_json(URL, use_cache=False)

    assert route.call_count == 2


@respx.mock
async def test_get_json_timeout_levanta_erro():
    respx.get(URL).mock(side_effect=httpx.TimeoutException("boom"))

    with pytest.raises(IBGERequestError) as exc_info:
        await get_json(URL)

    assert exc_info.value.url == URL


@respx.mock
async def test_get_json_http_status_error():
    respx.get(URL).mock(return_value=httpx.Response(404, json={"detail": "not found"}))

    with pytest.raises(IBGERequestError) as exc_info:
        await get_json(URL)

    assert exc_info.value.status_code == 404


@respx.mock
async def test_get_json_resposta_invalida():
    respx.get(URL).mock(return_value=httpx.Response(200, content=b"<html>nao e json</html>"))

    with pytest.raises(IBGERequestError):
        await get_json(URL)


@respx.mock
async def test_get_json_request_error():
    respx.get(URL).mock(side_effect=httpx.ConnectError("falha de conexao"))

    with pytest.raises(IBGERequestError):
        await get_json(URL)
