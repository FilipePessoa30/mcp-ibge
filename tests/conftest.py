"""Fixtures compartilhadas pelos testes.

Além do isolamento do cache, este módulo expõe exemplos realistas de
respostas da API do IBGE (estado RJ, municípios Rio de Janeiro/Niterói,
busca ambígua por "São José" e dados de um agregado do SIDRA) para serem
reutilizados pelos testes de cliente, serviço, tools e cache.
"""

from __future__ import annotations

from typing import Any

import pytest

from mcp_ibge.utils.cache import clear_cache


@pytest.fixture(autouse=True)
def _isolar_cache():
    """Garante que o cache em memória não vaze entre testes."""
    clear_cache()
    yield
    clear_cache()


@pytest.fixture
def estado_rj() -> dict[str, Any]:
    """Exemplo de item de `/estados`: Rio de Janeiro (RJ)."""
    return {
        "id": 33,
        "sigla": "RJ",
        "nome": "Rio de Janeiro",
        "regiao": {"id": 3, "sigla": "SE", "nome": "Sudeste"},
    }


def _municipio_rj(
    municipio_id: int, nome: str, microrregiao_id: int, microrregiao_nome: str
) -> dict[str, Any]:
    return {
        "id": municipio_id,
        "nome": nome,
        "microrregiao": {
            "id": microrregiao_id,
            "nome": microrregiao_nome,
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


@pytest.fixture
def municipio_rio_de_janeiro() -> dict[str, Any]:
    """Exemplo de item de `/municipios`: Rio de Janeiro - RJ (código IBGE 3304557)."""
    return _municipio_rj(3304557, "Rio de Janeiro", 33018, "Rio de Janeiro")


@pytest.fixture
def municipio_niteroi() -> dict[str, Any]:
    """Exemplo de item de `/municipios`: Niterói - RJ (código IBGE 3303302)."""
    return _municipio_rj(3303302, "Niterói", 33014, "Niterói")


def _municipio(
    municipio_id: int,
    nome: str,
    *,
    microrregiao_id: int,
    microrregiao_nome: str,
    mesorregiao_id: int,
    mesorregiao_nome: str,
    uf_id: int,
    uf_sigla: str,
    uf_nome: str,
    regiao_id: int,
    regiao_sigla: str,
    regiao_nome: str,
) -> dict[str, Any]:
    return {
        "id": municipio_id,
        "nome": nome,
        "microrregiao": {
            "id": microrregiao_id,
            "nome": microrregiao_nome,
            "mesorregiao": {
                "id": mesorregiao_id,
                "nome": mesorregiao_nome,
                "UF": {
                    "id": uf_id,
                    "sigla": uf_sigla,
                    "nome": uf_nome,
                    "regiao": {"id": regiao_id, "sigla": regiao_sigla, "nome": regiao_nome},
                },
            },
        },
    }


@pytest.fixture
def municipios_sao_jose_ambiguo() -> list[dict[str, Any]]:
    """Municípios "São José" em UFs diferentes — exemplo de busca nacional ambígua."""
    return [
        _municipio(
            3548807,
            "São José dos Campos",
            microrregiao_id=35062,
            microrregiao_nome="São José dos Campos",
            mesorregiao_id=3502,
            mesorregiao_nome="Vale do Paraíba Paulista",
            uf_id=35,
            uf_sigla="SP",
            uf_nome="São Paulo",
            regiao_id=3,
            regiao_sigla="SE",
            regiao_nome="Sudeste",
        ),
        _municipio(
            4125506,
            "São José dos Pinhais",
            microrregiao_id=41010,
            microrregiao_nome="Curitiba",
            mesorregiao_id=4108,
            mesorregiao_nome="Metropolitana de Curitiba",
            uf_id=41,
            uf_sigla="PR",
            uf_nome="Paraná",
            regiao_id=4,
            regiao_sigla="S",
            regiao_nome="Sul",
        ),
    ]


@pytest.fixture
def agregado_metadados() -> dict[str, Any]:
    """Exemplo de resposta de `/agregados/6579/metadados` (Estimativas de população)."""
    return {
        "id": 6579,
        "nome": "População residente estimada",
        "URL": "https://servicodados.ibge.gov.br/api/v3/agregados/6579",
        "pesquisa": "Estimativas de População",
        "assunto": "População",
        "periodicidade": {"frequencia": "anual", "inicio": 2001, "fim": 2024},
        "nivelTerritorial": {
            "Administrativo": ["N1", "N2", "N3", "N6"],
            "Especial": [],
            "IBGE": [],
        },
        "variaveis": [
            {
                "id": 9324,
                "nome": "População residente estimada",
                "unidade": "Pessoas",
                "sumarizacao": [],
            }
        ],
        "classificacoes": [],
    }


@pytest.fixture
def agregado_consulta_resposta() -> list[dict[str, Any]]:
    """Exemplo de resposta de `/agregados/6579/periodos/.../variaveis/9324` para Niterói."""
    return [
        {
            "id": "9324",
            "variavel": "População residente estimada",
            "unidade": "Pessoas",
            "resultados": [
                {
                    "classificacoes": [],
                    "series": [
                        {
                            "localidade": {
                                "id": "3303302",
                                "nome": "Niterói",
                                "nivel": {"id": "N6", "nome": "Município"},
                            },
                            "serie": {"2024": "516981"},
                        }
                    ],
                }
            ],
        }
    ]
