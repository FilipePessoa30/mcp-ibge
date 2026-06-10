"""Testes do cliente de indicadores de população."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients import populacao
from mcp_ibge.config import AGREGADOS_BASE_URL, PROJECOES_BASE_URL

POPULACAO_MUNICIPIO = [
    {
        "id": "9324",
        "variavel": "População residente estimada",
        "resultados": [
            {
                "series": [
                    {
                        "localidade": {"id": "4205407", "nome": "Florianópolis"},
                        "serie": {"2024": "537062"},
                    }
                ]
            }
        ],
    }
]

PROJECAO_BR = {
    "localidade": "BR",
    "projecao": {"populacao": 213000000, "periodo_disponivel": "2000-2070"},
}


@respx.mock
async def test_obter_populacao_municipio():
    endpoint = (
        f"{AGREGADOS_BASE_URL}/{populacao.AGREGADO_POPULACAO_ESTIMADA}"
        f"/periodos/-1/variaveis/{populacao.VARIAVEL_POPULACAO_ESTIMADA}"
    )
    route = respx.get(endpoint).mock(return_value=httpx.Response(200, json=POPULACAO_MUNICIPIO))

    result = await populacao.obter_populacao_municipio("4205407")

    assert result.data == POPULACAO_MUNICIPIO
    assert result.endpoint == endpoint
    assert result.params == {"codigo_municipio": "4205407", "localidades": "N6[4205407]"}
    assert route.calls.last.request.url.params["localidades"] == "N6[4205407]"


@respx.mock
async def test_obter_projecao_populacao_brasil():
    respx.get(f"{PROJECOES_BASE_URL}/populacao/BR").mock(
        return_value=httpx.Response(200, json=PROJECAO_BR)
    )

    result = await populacao.obter_projecao_populacao()

    assert result.data == PROJECAO_BR
    assert result.params == {"localidade": "BR"}


@respx.mock
async def test_obter_projecao_populacao_uf():
    respx.get(f"{PROJECOES_BASE_URL}/populacao/35").mock(
        return_value=httpx.Response(200, json={"localidade": "35"})
    )

    result = await populacao.obter_projecao_populacao("35")

    assert result.data == {"localidade": "35"}
    assert result.params == {"localidade": "35"}
