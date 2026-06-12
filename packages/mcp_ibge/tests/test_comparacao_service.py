"""Testes da camada de serviço `ComparacaoService` (`comparar_municipios`)."""

from __future__ import annotations

import httpx
import respx

from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings
from mcp_ibge.schemas.comparacao import MunicipioConsulta
from mcp_ibge.services.agregados_service import (
    AGREGADO_POPULACAO_ESTIMADA,
    VARIAVEL_POPULACAO_ESTIMADA,
)
from mcp_ibge.services.comparacao_service import MAX_MUNICIPIOS, ComparacaoService

LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"

_POPULACAO_URL = (
    f"{AGREGADOS_BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}"
    f"/periodos/-1/variaveis/{VARIAVEL_POPULACAO_ESTIMADA}"
)

MARICA = {
    "id": 3302904,
    "nome": "Maricá",
    "microrregiao": {
        "id": 33013,
        "nome": "Rio de Janeiro",
        "mesorregiao": {
            "id": 3305,
            "nome": "Metropolitana do Rio de Janeiro",
            "UF": {
                "id": 33,
                "sigla": "RJ",
                "nome": "Rio de Janeiro",
                "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
            },
        },
    },
}


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


def _populacao_side_effect(populacao_por_codigo: dict[str, list]):
    def _handler(request: httpx.Request) -> httpx.Response:
        localidades = request.url.params["localidades"]
        codigo = localidades.removeprefix("N6[").removesuffix("]")
        return httpx.Response(200, json=populacao_por_codigo[codigo])

    return _handler


@respx.mock
async def test_comparar_municipios_rio_niteroi_marica(municipio_rio_de_janeiro, municipio_niteroi):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro, municipio_niteroi, MARICA])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3303302").mock(
        return_value=httpx.Response(200, json=municipio_niteroi)
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3302904").mock(
        return_value=httpx.Response(200, json=MARICA)
    )

    populacao_por_codigo = {
        "3304557": _dados_populacao("3304557", "Rio de Janeiro", "2024", "6211423"),
        "3303302": _dados_populacao("3303302", "Niterói", "2024", "516981"),
        "3302904": _dados_populacao("3302904", "Maricá", "2024", "161745"),
    }
    respx.get(_POPULACAO_URL).mock(side_effect=_populacao_side_effect(populacao_por_codigo))

    municipios = [
        MunicipioConsulta(nome="Rio de Janeiro", uf="RJ"),
        MunicipioConsulta(nome="Niterói", uf="RJ"),
        MunicipioConsulta(nome="Maricá", uf="RJ"),
    ]

    result = await ComparacaoService().comparar_municipios(municipios)

    assert result.ok is True
    assert result.data is not None
    assert result.data.municipios_nao_resolvidos == []
    assert result.data.indicadores_consultados == ["populacao_estimada"]
    assert result.data.indicadores_nao_implementados == []

    por_nome = {m.nome: m for m in result.data.municipios}
    assert set(por_nome) == {"Rio de Janeiro", "Niterói", "Maricá"}

    assert por_nome["Rio de Janeiro"].codigo_ibge == 3304557
    assert por_nome["Rio de Janeiro"].indicadores[0].valor == 6211423.0
    assert por_nome["Niterói"].indicadores[0].valor == 516981.0
    assert por_nome["Maricá"].indicadores[0].valor == 161745.0
    for municipio in result.data.municipios:
        assert municipio.indicadores[0].indicador == "populacao_estimada"
        assert municipio.indicadores[0].periodo == "2024"
        assert municipio.indicadores[0].unidade == "Pessoas"
        assert municipio.indicadores[0].agregado_id == AGREGADO_POPULACAO_ESTIMADA

    assert result.data.fontes
    assert result.data.limitacoes
    assert any('"ano"' in limitacao for limitacao in result.data.limitacoes)
    assert result.warnings == []


@respx.mock
async def test_comparar_municipios_indicador_nao_implementado_gera_warning_e_continua(
    municipio_rio_de_janeiro,
):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(_POPULACAO_URL).mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("3304557", "Rio de Janeiro", "2024", "6211423")
        )
    )

    municipios = [MunicipioConsulta(nome="Rio de Janeiro", uf="RJ")]

    result = await ComparacaoService().comparar_municipios(
        municipios, indicadores=["populacao", "pib"]
    )

    assert result.ok is True
    assert result.data is not None
    assert result.data.indicadores_consultados == ["populacao_estimada"]
    assert result.data.indicadores_nao_implementados == ["pib"]
    assert any('"pib"' in aviso for aviso in result.warnings)

    municipio = result.data.municipios[0]
    assert len(municipio.indicadores) == 1
    assert municipio.indicadores[0].indicador == "populacao_estimada"


@respx.mock
async def test_comparar_municipios_nome_ambiguo_aparece_em_nao_resolvidos(
    municipio_rio_de_janeiro,
):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro])
    )
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios/3304557").mock(
        return_value=httpx.Response(200, json=municipio_rio_de_janeiro)
    )
    respx.get(_POPULACAO_URL).mock(
        return_value=httpx.Response(
            200, json=_dados_populacao("3304557", "Rio de Janeiro", "2024", "6211423")
        )
    )

    municipios_sao_jose = [
        _municipio_sp(3548807, "São José dos Campos"),
        _municipio_sp(3549904, "São José do Rio Preto"),
    ]
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose)
    )

    municipios = [
        MunicipioConsulta(nome="Rio de Janeiro", uf="RJ"),
        MunicipioConsulta(nome="São José", uf="SP"),
    ]

    result = await ComparacaoService().comparar_municipios(municipios)

    assert result.ok is True
    assert result.data is not None
    assert len(result.data.municipios) == 1
    assert result.data.municipios[0].nome == "Rio de Janeiro"

    assert len(result.data.municipios_nao_resolvidos) == 1
    nao_resolvido = result.data.municipios_nao_resolvidos[0]
    assert nao_resolvido.nome == "São José"
    assert nao_resolvido.uf == "SP"
    assert "São José dos Campos" in nao_resolvido.motivo
    assert "São José do Rio Preto" in nao_resolvido.motivo

    assert any("São José dos Campos" in aviso for aviso in result.warnings)


@respx.mock
async def test_comparar_municipios_nenhum_resolvido_retorna_erro():
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[])
    )

    municipios = [MunicipioConsulta(nome="Inexistente", uf="RJ")]

    result = await ComparacaoService().comparar_municipios(municipios)

    assert result.ok is False
    assert result.data is None
    assert result.errors
    assert any("Inexistente" in aviso for aviso in result.warnings)


async def test_comparar_municipios_lista_vazia_retorna_erro():
    result = await ComparacaoService().comparar_municipios([])

    assert result.ok is False
    assert result.data is None
    assert result.errors


async def test_comparar_municipios_excede_limite_retorna_erro():
    municipios = [
        MunicipioConsulta(nome=f"Município {i}", uf="RJ") for i in range(MAX_MUNICIPIOS + 1)
    ]

    result = await ComparacaoService().comparar_municipios(municipios)

    assert result.ok is False
    assert result.data is None
    assert result.errors
    assert str(MAX_MUNICIPIOS) in result.errors[0]
