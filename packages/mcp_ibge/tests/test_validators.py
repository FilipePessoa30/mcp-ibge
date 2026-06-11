"""Testes dos validadores de formato em `mcp_ibge.utils.validators`."""

from __future__ import annotations

import pytest

from mcp_ibge.utils.errors import IBGEValidationError
from mcp_ibge.utils.validators import (
    validate_agregado_id,
    validate_limit,
    validate_municipality_code,
    validate_niveis,
    validate_periodos,
    validate_uf,
    validate_variaveis,
)

# ---------------------------------------------------------------------------
# validate_uf
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("uf", ["RJ", "rj", " rj ", "33", "SP", "sp", "MG", "mg", "DF", "53"])
def test_validate_uf_aceita_sigla_ou_codigo_validos(uf: str):
    assert validate_uf(uf) == uf.strip().upper()


@pytest.mark.parametrize("uf", ["XX", "ZZ", "99", "00", "", "   ", "Rio de Janeiro", "R J"])
def test_validate_uf_rejeita_valores_invalidos(uf: str):
    with pytest.raises(IBGEValidationError):
        validate_uf(uf)


# ---------------------------------------------------------------------------
# validate_municipality_code
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("codigo", [3550308, "3550308", "9999999", " 3304557 "])
def test_validate_municipality_code_aceita_codigos_de_7_digitos(codigo: int | str):
    resultado = validate_municipality_code(codigo)
    assert resultado == int(str(codigo).strip())
    assert isinstance(resultado, int)


@pytest.mark.parametrize(
    "codigo",
    ["", "   ", "123", "12345678", "abcdefg", "-123456", "33.5030.8", 3.5],
)
def test_validate_municipality_code_rejeita_codigo_curto_longo_ou_nao_numerico(codigo: object):
    with pytest.raises(IBGEValidationError):
        validate_municipality_code(codigo)  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# validate_agregado_id
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("agregado_id", ["6579", " 6579 ", "1", "123456789"])
def test_validate_agregado_id_aceita_apenas_numeros_como_string(agregado_id: str):
    assert validate_agregado_id(agregado_id) == agregado_id.strip()


@pytest.mark.parametrize(
    "agregado_id", ["", "   ", "abc", "65a9", "-6579", "65 79", "6579.0", "6579;DROP"]
)
def test_validate_agregado_id_rejeita_vazio_negativo_ou_caracteres_estranhos(agregado_id: str):
    with pytest.raises(IBGEValidationError):
        validate_agregado_id(agregado_id)


# ---------------------------------------------------------------------------
# validate_variaveis
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("variaveis", ["all", "93", "93|1000093", " 93 ", "1|2|3"])
def test_validate_variaveis_aceita_all_ou_ids_separados_por_pipe(variaveis: str):
    assert validate_variaveis(variaveis) == variaveis.strip()


@pytest.mark.parametrize(
    "variaveis", ["", "   ", "ALL", "abc", "93,1000093", "93|", "-93", "93;1000093"]
)
def test_validate_variaveis_rejeita_strings_vazias_ou_invalidas(variaveis: str):
    with pytest.raises(IBGEValidationError):
        validate_variaveis(variaveis)


# ---------------------------------------------------------------------------
# validate_periodos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "periodos",
    [
        "-1",
        "-6",
        "2021",
        "2024",
        "all",
        "2010-2020",
        "2010,2015-2020,-1",
        "2020|2021|2022",
        "202101",
        "202101-202104",
    ],
)
def test_validate_periodos_aceita_formatos_validos(periodos: str):
    assert validate_periodos(periodos) == periodos


@pytest.mark.parametrize(
    "periodos",
    ["", "   ", "abc", "21", "2021;2022", "2021--2022", "-", "2021,abc", "2021|abc", "ALL"],
)
def test_validate_periodos_rejeita_caracteres_invalidos(periodos: str):
    with pytest.raises(IBGEValidationError):
        validate_periodos(periodos)


# ---------------------------------------------------------------------------
# validate_niveis
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "niveis",
    [
        "N1",
        "N2",
        "N3",
        "N6",
        "N105",
        "N1|N3",
        "N1|N3|N6",
        " N6 ",
        "N3[33]",
        "N3[33,35]",
        "N6[all]",
        "N3[33]|N6[3550308]",
    ],
)
def test_validate_niveis_aceita_niveis_simples_e_composicoes(niveis: str):
    assert validate_niveis(niveis) == niveis.strip()


@pytest.mark.parametrize(
    "niveis",
    [
        "",
        "   ",
        "6",
        "n6",
        "N",
        "N1|",
        "N1|n3",
        "N1,N3",
        "N1234",
        "N3[]",
        "N3[abc]",
        "N3[33;DROP]",
        "N3[<script>]",
    ],
)
def test_validate_niveis_rejeita_valores_perigosos_ou_invalidos(niveis: str):
    with pytest.raises(IBGEValidationError):
        validate_niveis(niveis)


# ---------------------------------------------------------------------------
# validate_limit
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("limit", [1, 10, 50, 100])
def test_validate_limit_aceita_valores_entre_1_e_100(limit: int):
    assert validate_limit(limit) == limit


@pytest.mark.parametrize("limit", [0, -1, 101, 1000, 1.5, "10", True, False])
def test_validate_limit_rejeita_fora_do_intervalo_ou_nao_inteiro(limit: object):
    with pytest.raises(IBGEValidationError):
        validate_limit(limit)  # type: ignore[arg-type]
