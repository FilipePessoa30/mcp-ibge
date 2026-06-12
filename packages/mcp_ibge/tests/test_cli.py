"""Testes da CLI `mcp-data-br` (Typer + `CliRunner`).

A CLI reaproveita os mesmos services das tools MCP (ver `cli.py`), então
estes testes focam no "encanamento": parsing de argumentos, formatação JSON
(`--pretty`), comportamento do `--no-cache` e código de saída em caso de
erro (`ok=False` -> exit code 1).
"""

from __future__ import annotations

import json

import httpx
import respx
from typer.testing import CliRunner

from mcp_ibge.cli import app
from mcp_ibge.clients.agregados import AGREGADOS_PATH
from mcp_ibge.clients.localidades import LOCALIDADES_PATH
from mcp_ibge.config import get_settings

from .conftest import assert_envelope_contract

runner = CliRunner()

LOCALIDADES_BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"
AGREGADOS_BASE_URL = f"{get_settings().api_base_url}{AGREGADOS_PATH}"


@respx.mock
def test_ibge_estados_retorna_envelope_json(estado_rj):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[estado_rj])
    )

    result = runner.invoke(app, ["ibge", "estados"])

    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert_envelope_contract(envelope)
    assert envelope["ok"] is True
    assert any(estado["sigla"] == "RJ" for estado in envelope["data"])


@respx.mock
def test_ibge_estados_pretty_formata_com_indentacao(estado_rj):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[estado_rj])
    )

    result = runner.invoke(app, ["ibge", "estados", "--pretty"])

    assert result.exit_code == 0
    assert "\n" in result.stdout
    envelope = json.loads(result.stdout)
    assert envelope["ok"] is True


@respx.mock
def test_ibge_municipios_com_uf(municipio_rio_de_janeiro):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_rio_de_janeiro])
    )

    result = runner.invoke(app, ["ibge", "municipios", "--uf", "RJ"])

    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert_envelope_contract(envelope)
    assert envelope["data"][0]["nome"] == "Rio de Janeiro"
    assert envelope["data"][0]["id"] == 3304557


@respx.mock
def test_ibge_codigo_municipio(municipio_niteroi):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/RJ/municipios").mock(
        return_value=httpx.Response(200, json=[municipio_niteroi])
    )

    result = runner.invoke(app, ["ibge", "codigo-municipio", "Niterói", "--uf", "RJ"])

    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert_envelope_contract(envelope)
    assert envelope["ok"] is True
    assert envelope["data"] == 3303302


@respx.mock
def test_ibge_codigo_municipio_ambiguo_retorna_exit_code_1(municipios_sao_jose_ambiguo):
    respx.get(f"{LOCALIDADES_BASE_URL}/estados/SP/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose_ambiguo)
    )

    result = runner.invoke(app, ["ibge", "codigo-municipio", "São José", "--uf", "SP"])

    assert result.exit_code == 1
    envelope = json.loads(result.stdout)
    assert_envelope_contract(envelope)
    assert envelope["ok"] is False
    assert envelope["data"] is None


@respx.mock
def test_ibge_buscar_municipio_ambiguo_inclui_warnings(municipios_sao_jose_ambiguo):
    respx.get(f"{LOCALIDADES_BASE_URL}/municipios").mock(
        return_value=httpx.Response(200, json=municipios_sao_jose_ambiguo)
    )

    result = runner.invoke(app, ["ibge", "buscar-municipio", "São José"])

    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert_envelope_contract(envelope)
    assert envelope["ok"] is True
    assert envelope["warnings"]


@respx.mock
def test_sidra_metadados(agregado_metadados):
    respx.get(f"{AGREGADOS_BASE_URL}/6579/metadados").mock(
        return_value=httpx.Response(200, json=agregado_metadados)
    )

    result = runner.invoke(app, ["sidra", "metadados", "--agregado", "6579"])

    assert result.exit_code == 0
    envelope = json.loads(result.stdout)
    assert_envelope_contract(envelope)
    assert envelope["ok"] is True
    assert envelope["data"]["id"] == "6579"


@respx.mock
def test_no_cache_ignora_o_cache_em_memoria(estado_rj):
    route = respx.get(f"{LOCALIDADES_BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[estado_rj])
    )

    primeira = runner.invoke(app, ["ibge", "estados"])
    segunda = runner.invoke(app, ["ibge", "estados"])
    assert route.call_count == 1
    assert json.loads(primeira.stdout)["metadata"]["cache_hit"] is False
    assert json.loads(segunda.stdout)["metadata"]["cache_hit"] is True

    runner.invoke(app, ["ibge", "estados", "--no-cache"])
    terceira = runner.invoke(app, ["ibge", "estados", "--no-cache"])
    assert route.call_count == 3
    assert json.loads(terceira.stdout)["metadata"]["cache_hit"] is False


def test_status_retorna_versao_tools_e_cache():
    result = runner.invoke(app, ["status"])

    assert result.exit_code == 0
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"
    assert payload["server"] == "mcp-ibge"
    assert "listar_estados" in payload["tools"]
    assert "cache" in payload


def test_status_pretty_formata_com_indentacao():
    result = runner.invoke(app, ["status", "--pretty"])

    assert result.exit_code == 0
    assert "\n" in result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "ok"


def test_app_sem_argumentos_mostra_ajuda():
    result = runner.invoke(app, [])

    assert result.exit_code == 2
    assert "ibge" in result.output
    assert "sidra" in result.output
    assert "status" in result.output
