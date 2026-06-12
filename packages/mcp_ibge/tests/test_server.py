"""Testes do módulo `server`: importação, tools, resource de status e prompt."""

from __future__ import annotations

import json

import respx
from mcp.server.fastmcp import FastMCP


async def test_importa_server_sem_executar():
    """Importar `mcp_ibge.server` não deve iniciar o servidor (sem `mcp.run`)."""
    from mcp_ibge import server

    assert isinstance(server.mcp, FastMCP)
    assert server.mcp.name == "mcp-ibge"


async def test_tools_de_localidades_e_agregados_registradas():
    from mcp_ibge.server import mcp

    nomes = {tool.name for tool in await mcp.list_tools()}

    assert "listar_estados" in nomes
    assert "consultar_agregado" in nomes
    assert "consultar_populacao_municipio" in nomes


async def test_resource_status_retorna_versao_tools_e_timestamp():
    from mcp_ibge.server import mcp

    recursos = await mcp.list_resources()
    assert any(str(r.uri) == "ibge://status" for r in recursos)

    conteudos = list(await mcp.read_resource("ibge://status"))
    assert len(conteudos) == 1

    payload = json.loads(conteudos[0].content)
    assert payload["status"] == "ok"
    assert payload["server"] == "mcp-ibge"
    assert "version" in payload
    assert "timestamp" in payload
    assert "listar_estados" in payload["tools"]


async def test_resource_mcp_data_br_status_registrado():
    from mcp_ibge.server import mcp

    recursos = await mcp.list_resources()
    assert any(str(r.uri) == "mcp-data-br://status" for r in recursos)


async def test_resource_mcp_data_br_status_retorna_cache_metricas_uptime_e_fontes():
    from mcp_ibge.config import get_settings
    from mcp_ibge.server import mcp

    conteudos = list(await mcp.read_resource("mcp-data-br://status"))
    assert len(conteudos) == 1

    payload = json.loads(conteudos[0].content)

    assert payload["status"] == "ok"
    assert payload["server"] == "mcp-ibge"
    assert "version" in payload
    assert "listar_estados" in payload["tools"]
    assert "timestamp" in payload

    settings = get_settings()
    assert payload["cache"]["enabled"] == settings.cache_enabled
    assert payload["cache"]["ttl_seconds"] == settings.cache_ttl_seconds
    assert payload["cache"]["max_size"] == settings.cache_max_size
    assert "current_size" in payload["cache"]

    metricas = payload["metrics"]
    assert metricas.keys() == {
        "total_requests",
        "cache_hits",
        "cache_misses",
        "errors",
        "cache_hit_rate",
        "average_latency_ms",
    }
    assert metricas["total_requests"] == 0

    assert isinstance(payload["uptime_seconds"], (int, float))
    assert payload["uptime_seconds"] >= 0

    assert payload["data_sources"] == [
        {
            "name": settings.source_name,
            "official_source": settings.official_source_url,
            "api_base_url": settings.api_base_url,
        }
    ]


@respx.mock
async def test_resource_status_reflete_metricas_apos_requisicoes():
    import httpx

    from mcp_ibge.clients.base import AsyncIBGEClient
    from mcp_ibge.clients.localidades import LOCALIDADES_PATH
    from mcp_ibge.config import get_settings
    from mcp_ibge.server import mcp

    base_url = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
    respx.get(f"{base_url}/estados").mock(
        return_value=httpx.Response(200, json=[{"id": 33, "sigla": "RJ"}])
    )

    client = AsyncIBGEClient(LOCALIDADES_PATH)
    await client.get_json("/estados")
    await client.get_json("/estados")

    conteudos = list(await mcp.read_resource("mcp-data-br://status"))
    payload = json.loads(conteudos[0].content)

    assert payload["metrics"]["total_requests"] == 2
    assert payload["metrics"]["cache_hits"] == 1
    assert payload["metrics"]["cache_misses"] == 1
    assert payload["metrics"]["cache_hit_rate"] == 0.5


async def test_prompt_comparar_municipios_registrado():
    from mcp_ibge.server import mcp

    prompts = {p.name for p in await mcp.list_prompts()}
    assert "comparar_municipios" in prompts

    resultado = await mcp.get_prompt(
        "comparar_municipios", {"municipios": "São Paulo/SP, Rio de Janeiro/RJ"}
    )
    assert resultado.messages
    texto = resultado.messages[0].content.text
    assert "São Paulo/SP, Rio de Janeiro/RJ" in texto
    assert "fonte" in texto.lower()
