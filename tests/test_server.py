"""Testes do módulo `server`: importação, tools, resource de status e prompt."""

from __future__ import annotations

import json

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
