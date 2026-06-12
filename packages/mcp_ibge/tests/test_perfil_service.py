"""Testes da camada de serviço `PerfilService` (`gerar_perfil_municipal`)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.services.agregados_service import (
    AGREGADO_POPULACAO_ESTIMADA,
    VARIAVEL_POPULACAO_ESTIMADA,
)
from mcp_ibge.services.perfil_service import PerfilService

LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

_POPULACAO_URL = (
    f"{AGREGADOS_BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}"
    f"/periodos/-1/variaveis/{VARIAVEL_POPULACAO_ESTIMADA}"
)


def _dados_populacao(localidade_id: str, localidade_nome: str, periodo: str, valor: str) -> list:
    return [
        {
            "id": VARIAVEL_POPULACAO_ESTIMADA,
            "unidade": "Pessoas",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": localidade_id, "nome": localidade_nome},
                            "serie": {periodo: valor},
                        }
                    ]
                }
            ],
        }
    ]


def _municipio_sp(municipio_id: int, nome: str) -> dict:
    return {
        "id": municipio_id,
        "nome": nome,
        "microrregiao": {
            "id": 1,
            "nome": "Microrregião",
            "mesorregiao": {
                "id": 1,
                "nome": "Mesorregião",
                "UF": {
                    "id": 35,
                    "sigla": "SP",
                    "nome": "São Paulo",
                    "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
                },
            },
        },
    }


@respx.mock
async def test_gerar_perfil_municipal_rio_de_janeiro(municipio_rio_de_janeiro):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(_POPULACAO_URL).mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("3304557", "Rio de Janeiro", "2024", "6775561")
        )
    )

    result = await PerfilService().gerar_perfil_municipal("Rio de Janeiro", "RJ")

    assert result.ok is True
    assert result.data is not None

    municipio = result.data.municipio
    assert municipio.codigo_ibge == 3304557
    assert municipio.nome == "Rio de Janeiro"
    assert municipio.uf_sigla == "RJ"
    assert municipio.uf_nome == "Rio de Janeiro"
    assert municipio.regiao_nome == "Sudeste"
    assert municipio.microrregiao_ou_regiao_intermediaria is not None
    assert municipio.microrregiao_ou_regiao_intermediaria.tipo == "microrregiao"
    assert municipio.microrregiao_ou_regiao_intermediaria.nome == "Rio de Janeiro"

    assert len(result.data.indicadores) == 1
    indicador = result.data.indicadores[0]
    assert indicador.indicador == "populacao_estimada"
    assert indicador.valor == 6775561.0
    assert indicador.periodo == "2024"
    assert indicador.agregado_id == AGREGADO_POPULACAO_ESTIMADA

    assert len(result.data.fontes) == 2
    assert result.data.limitacoes
    assert result.data.proximos_indicadores_sugeridos

    assert any('"ano"' in aviso for aviso in result.warnings)


@respx.mock
async def test_gerar_perfil_municipal_niteroi(municipio_niteroi, agregado_consulta_resposta):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_niteroi])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=municipio_niteroi)
    )
    respx.get(_POPULACAO_URL).mock(
        return_value=httpx.Response(200, json=agregado_consulta_resposta)
    )

    result = await PerfilService().gerar_perfil_municipal("Niterói", "RJ")

    assert result.ok is True
    assert result.data is not None

    municipio = result.data.municipio
    assert municipio.codigo_ibge == 3303302
    assert municipio.nome == "Niterói"
    assert municipio.uf_sigla == "RJ"
    assert municipio.regiao_nome == "Sudeste"
    assert municipio.microrregiao_ou_regiao_intermediaria is not None
    assert municipio.microrregiao_ou_regiao_intermediaria.tipo == "microrregiao"
    assert municipio.microrregiao_ou_regiao_intermediaria.nome == "Niterói"

    assert len(result.data.indicadores) == 1
    indicador = result.data.indicadores[0]
    assert indicador.indicador == "populacao_estimada"
    assert indicador.valor == 516981.0
    assert indicador.periodo == "2024"


@respx.mock
async def test_gerar_perfil_municipal_nome_ambiguo_retorna_warnings_sem_erro():
    municipios_sao_jose = [
        _municipio_sp(3548807, "São José dos Campos"),
        _municipio_sp(3549904, "São José do Rio Preto"),
    ]
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose)
    )

    result = await PerfilService().gerar_perfil_municipal("São José", "SP")

    assert result.ok is False
    assert result.data is None
    assert result.errors == []
    assert result.warnings
    assert "São José dos Campos" in result.warnings[0]
    assert "São José do Rio Preto" in result.warnings[0]
