"""Testes de parsing das respostas do SIDRA em schemas Pydantic (`schemas.agregados`)."""

from __future__ import annotations

from mcp_ibge.schemas.agregados import (
    AgregadoMetadata,
    agregado_metadata_from_raw,
    agregado_period_from_raw,
    agregado_query_results_from_raw,
    agregado_variable_from_raw,
    agregados_summary_from_lista,
)


def test_agregados_summary_from_lista_achata_grupos_por_pesquisa():
    bruto = [
        {
            "id": "POP",
            "nome": "Estimativas de população",
            "agregados": [
                {"id": 6579, "nome": "População residente estimada"},
                {"id": 6580, "nome": "Outra tabela"},
            ],
        },
        {
            "id": "CD",
            "nome": "Censo Demográfico",
            "agregados": [{"id": 9514, "nome": "População residente, por sexo e idade"}],
        },
    ]

    resumo = agregados_summary_from_lista(bruto)

    assert [(item.id, item.nome) for item in resumo] == [
        ("6579", "População residente estimada"),
        ("6580", "Outra tabela"),
        ("9514", "População residente, por sexo e idade"),
    ]


def test_agregados_summary_from_lista_grupo_sem_agregados():
    assert agregados_summary_from_lista([{"id": "X", "nome": "Vazio", "agregados": []}]) == []


def test_agregado_metadata_from_raw_extrai_periodicidade_e_preserva_raw():
    bruto = {
        "id": 6579,
        "nome": "População residente estimada",
        "URL": "https://sidra.ibge.gov.br/tabela/6579",
        "pesquisa": "Estimativas de População",
        "assunto": "População",
        "periodicidade": {"frequencia": "anual", "inicio": 2001, "fim": 2024},
        "nivelTerritorial": {"Administrativo": ["N6"]},
        "variaveis": [{"id": 9324, "nome": "População residente estimada", "unidade": "Pessoas"}],
    }

    metadata = agregado_metadata_from_raw(bruto)

    assert isinstance(metadata, AgregadoMetadata)
    assert metadata.id == "6579"
    assert metadata.nome == "População residente estimada"
    assert metadata.pesquisa == "Estimativas de População"
    assert metadata.assunto == "População"
    assert metadata.periodicidade == "anual"
    assert metadata.raw == bruto


def test_agregado_metadata_from_raw_periodicidade_string():
    metadata = agregado_metadata_from_raw({"id": 1, "nome": "Tabela", "periodicidade": "anual"})

    assert metadata.periodicidade == "anual"


def test_agregado_metadata_from_raw_sem_periodicidade():
    metadata = agregado_metadata_from_raw({"id": 1, "nome": "Tabela"})

    assert metadata.periodicidade is None
    assert metadata.pesquisa is None
    assert metadata.assunto is None


def test_agregado_variable_from_raw():
    bruto = {
        "id": 9324,
        "nome": "População residente estimada",
        "unidade": "Pessoas",
        "sumarizacao": {"status": True, "excecao": []},
    }

    variavel = agregado_variable_from_raw(bruto)

    assert variavel.id == "9324"
    assert variavel.nome == "População residente estimada"
    assert variavel.unidade == "Pessoas"
    assert variavel.raw == bruto


def test_agregado_period_from_raw_usa_primeiro_literal():
    bruto = {"id": "2024", "literals": ["2024"], "modificacao": "2025-08-29T00:00:00.000-03:00"}

    periodo = agregado_period_from_raw(bruto)

    assert periodo.id == "2024"
    assert periodo.nome == "2024"


def test_agregado_period_from_raw_sem_literals():
    periodo = agregado_period_from_raw({"id": "2024"})

    assert periodo.id == "2024"
    assert periodo.nome is None


def test_agregado_query_results_from_raw_achata_series_por_localidade_e_periodo():
    bruto = [
        {
            "id": "9324",
            "variavel": "População residente estimada",
            "unidade": "Pessoas",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": "3550308", "nome": "São Paulo"},
                            "serie": {"2023": "11451245", "2024": "11733906"},
                        },
                        {
                            "localidade": {"id": "3304557", "nome": "Rio de Janeiro"},
                            "serie": {"2023": "6211223", "2024": "6211423"},
                        },
                    ]
                }
            ],
        }
    ]

    resultados = agregado_query_results_from_raw("6579", bruto)

    assert len(resultados) == 4
    primeiro = resultados[0]
    assert primeiro.agregado_id == "6579"
    assert primeiro.variavel_id == "9324"
    assert primeiro.localidade_id == "3550308"
    assert primeiro.localidade_nome == "São Paulo"
    assert primeiro.periodo == "2023"
    assert primeiro.valor == 11451245.0
    assert primeiro.unidade == "Pessoas"
    assert primeiro.raw is not None


def test_agregado_query_results_from_raw_trata_marcadores_de_dado_ausente():
    bruto = [
        {
            "id": "9324",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": "1100015", "nome": "Alta Floresta D'Oeste"},
                            "serie": {"2024": "-", "2023": "...", "2022": "X", "2021": ".."},
                        }
                    ]
                }
            ],
        }
    ]

    resultados = agregado_query_results_from_raw("6579", bruto)

    assert {r.periodo: r.valor for r in resultados} == {
        "2024": None,
        "2023": None,
        "2022": None,
        "2021": None,
    }


def test_agregado_query_results_from_raw_preserva_string_nao_numerica():
    bruto = [
        {
            "id": "9324",
            "resultados": [
                {
                    "series": [
                        {
                            "localidade": {"id": "1", "nome": "Brasil"},
                            "serie": {"2024": "n.d."},
                        }
                    ]
                }
            ],
        }
    ]

    resultados = agregado_query_results_from_raw("6579", bruto)

    assert resultados[0].valor == "n.d."


def test_agregado_query_results_from_raw_lista_vazia():
    assert agregado_query_results_from_raw("6579", []) == []


def test_agregado_query_results_from_raw_resultado_sem_series():
    bruto = [{"id": "9324", "resultados": [{"series": []}]}]

    assert agregado_query_results_from_raw("6579", bruto) == []
