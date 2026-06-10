"""Testes de serialização e conversão dos schemas de Localidades."""

from __future__ import annotations

from mcp_ibge.schemas.localidades import (
    District,
    Municipality,
    Region,
    State,
    district_from_raw,
    municipality_from_raw,
    region_from_raw,
    state_from_raw,
)

REGIAO_RAW = {"id": 3, "sigla": "SE", "nome": "Sudeste"}

ESTADO_RAW = {
    "id": 35,
    "sigla": "SP",
    "nome": "São Paulo",
    "regiao": REGIAO_RAW,
}

MUNICIPIO_RAW = {
    "id": 3550308,
    "nome": "São Paulo",
    "microrregiao": {
        "id": 35061,
        "nome": "São Paulo",
        "mesorregiao": {
            "id": 3515,
            "nome": "Metropolitana de São Paulo",
            "UF": ESTADO_RAW,
        },
    },
}

MUNICIPIO_RAW_REGIAO_IMEDIATA = {
    "id": 3550308,
    "nome": "São Paulo",
    "regiao-imediata": {
        "id": 350001,
        "nome": "São Paulo",
        "regiao-intermediaria": {
            "id": 3501,
            "nome": "São Paulo",
            "UF": ESTADO_RAW,
        },
    },
}

DISTRITO_RAW = {
    "id": 355030801,
    "nome": "Sé",
    "municipio": {"id": 3550308, "nome": "São Paulo"},
}


def test_region_from_raw():
    region = region_from_raw(REGIAO_RAW)

    assert region == Region(id=3, sigla="SE", nome="Sudeste")
    assert region.model_dump(mode="json") == REGIAO_RAW


def test_state_from_raw():
    state = state_from_raw(ESTADO_RAW)

    assert state.id == 35
    assert state.sigla == "SP"
    assert state.regiao == Region(id=3, sigla="SE", nome="Sudeste")


def test_state_from_raw_sem_regiao():
    state = state_from_raw({"id": 35, "sigla": "SP", "nome": "São Paulo"})

    assert state.regiao is None
    assert state == State(id=35, sigla="SP", nome="São Paulo", regiao=None)


def test_municipality_from_raw_extrai_uf_de_microrregiao():
    municipality = municipality_from_raw(MUNICIPIO_RAW)

    assert municipality == Municipality(
        id=3550308,
        nome="São Paulo",
        uf_id=35,
        uf_sigla="SP",
        uf_nome="São Paulo",
        regiao_nome="Sudeste",
        raw=MUNICIPIO_RAW,
    )


def test_municipality_from_raw_extrai_uf_de_regiao_imediata():
    municipality = municipality_from_raw(MUNICIPIO_RAW_REGIAO_IMEDIATA)

    assert municipality.uf_sigla == "SP"
    assert municipality.regiao_nome == "Sudeste"
    assert municipality.raw == MUNICIPIO_RAW_REGIAO_IMEDIATA


def test_municipality_from_raw_sem_uf():
    municipality = municipality_from_raw({"id": 1, "nome": "Município sem UF"})

    assert municipality.uf_id is None
    assert municipality.uf_sigla is None
    assert municipality.uf_nome is None
    assert municipality.regiao_nome is None


def test_district_from_raw():
    district = district_from_raw(DISTRITO_RAW)

    assert district == District(
        id=355030801,
        nome="Sé",
        municipio_id=3550308,
        municipio_nome="São Paulo",
        raw=DISTRITO_RAW,
    )


def test_municipality_serializa_para_json():
    municipality = municipality_from_raw(MUNICIPIO_RAW)

    dumped = municipality.model_dump(mode="json")

    assert dumped["uf_sigla"] == "SP"
    assert dumped["raw"] == MUNICIPIO_RAW
