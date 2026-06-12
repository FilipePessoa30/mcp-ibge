"""Testes da camada de segurança (`mcp_ibge.security`).

Cobre os pontos do modelo de ameaças descrito em `docs/security.md` e
`packages/mcp_ibge/docs/security.md`: allowlist de domínios e verificação de
URL antes de qualquer requisição, limite de tamanho de resposta, mensagens de
erro sem stack trace e validação de entradas (incluindo entradas maliciosas)
antes de qualquer chamada de rede.
"""

from __future__ import annotations

import httpx
import pytest
import respx

from mcp_ibge.clients.base import AsyncIBGEClient
from mcp_ibge.config import get_settings
from mcp_ibge.security import (
    ResponseTooLargeError,
    URLNotAllowedError,
    assert_allowed_url,
    is_allowed_url,
    response_size_guard,
    safe_error_response,
)
from mcp_ibge.utils.errors import IBGEClientError, IBGEServerError, IBGEValidationError
from mcp_ibge.utils.validators import (
    validate_agregado_id,
    validate_limit,
    validate_municipality_code,
    validate_niveis,
    validate_periodos,
    validate_uf,
    validate_variaveis,
)

BASE_URL = get_settings().api_base_url


# --- allowlist de domínios / verificação de URL ----------------------------


@pytest.mark.parametrize(
    "url",
    [
        "https://servicodados.ibge.gov.br/api/v1/localidades/estados",
        "https://servicodados.ibge.gov.br/api/v3/agregados/6579/metadados",
    ],
)
def test_is_allowed_url_aceita_dominio_oficial(url: str):
    assert is_allowed_url(url) is True
    assert_allowed_url(url)  # não levanta


@pytest.mark.parametrize(
    "url",
    [
        "http://servicodados.ibge.gov.br/api/v1/localidades/estados",  # http, não https
        "https://example.com/api/v1/localidades/estados",  # domínio fora da allowlist
        "https://servicodados.ibge.gov.br.evil.com/api/v1/localidades",  # domínio "parecido"
        "https://evil.com/?url=servicodados.ibge.gov.br",  # host real é evil.com
        "file:///etc/passwd",  # esquema não-HTTP (acesso a arquivo local)
        "ftp://servicodados.ibge.gov.br/api",  # esquema não-HTTPS
        "not a url",  # malformada
        "",  # vazia
    ],
)
def test_is_allowed_url_rejeita_url_arbitraria(url: str):
    assert is_allowed_url(url) is False
    with pytest.raises(URLNotAllowedError):
        assert_allowed_url(url)


@respx.mock
async def test_get_json_bloqueia_url_fora_da_allowlist_antes_da_requisicao(monkeypatch):
    """Verificação em profundidade: mesmo que `api_base_url` seja válido, uma
    allowlist diferente em tempo de execução impede a requisição HTTP."""
    monkeypatch.setattr("mcp_ibge.security.ALLOWED_HOSTS", frozenset({"example.com"}))

    route = respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(200, json={"ok": True}))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEClientError) as exc_info:
        await client.get_json("/teste")

    assert not route.called
    assert exc_info.value.status_code is None
    assert "não permitida" in str(exc_info.value)


# --- limite de tamanho de resposta ------------------------------------------


def test_response_size_guard_aceita_tamanho_dentro_do_limite():
    response_size_guard(100, max_size=1000)  # não levanta
    response_size_guard(1000, max_size=1000)  # limite é inclusivo


def test_response_size_guard_rejeita_tamanho_acima_do_limite():
    with pytest.raises(ResponseTooLargeError) as exc_info:
        response_size_guard(1001, max_size=1000, url="https://servicodados.ibge.gov.br/api/teste")

    assert "1000 bytes" in str(exc_info.value)
    assert "https://servicodados.ibge.gov.br/api/teste" in str(exc_info.value)


def test_response_size_guard_usa_limite_padrao_das_settings(monkeypatch):
    settings = get_settings().model_copy(update={"max_response_size_bytes": 10})
    monkeypatch.setattr("mcp_ibge.security.get_settings", lambda: settings)

    response_size_guard(10)  # não levanta
    with pytest.raises(ResponseTooLargeError):
        response_size_guard(11)


@respx.mock
async def test_get_json_aborta_resposta_maior_que_o_limite(monkeypatch):
    settings = get_settings().model_copy(update={"max_response_size_bytes": 10})
    monkeypatch.setattr("mcp_ibge.clients.base.get_settings", lambda: settings)

    respx.get(f"{BASE_URL}/teste").mock(return_value=httpx.Response(200, json={"dados": "x" * 1000}))

    client = AsyncIBGEClient()
    with pytest.raises(IBGEServerError) as exc_info:
        await client.get_json("/teste")

    assert exc_info.value.status_code is None
    assert "excede o limite de 10 bytes" in str(exc_info.value)


# --- erros sem stack trace ---------------------------------------------------


def test_safe_error_response_retorna_mensagem_da_excecao():
    assert safe_error_response(ValueError("parâmetro inválido")) == "parâmetro inválido"


def test_safe_error_response_nao_expoe_traceback():
    try:
        raise RuntimeError("falha interna")
    except RuntimeError as exc:
        mensagem = safe_error_response(exc)

    assert mensagem == "falha interna"
    assert "Traceback" not in mensagem
    assert "test_security.py" not in mensagem


@pytest.mark.parametrize("exc", [Exception(), Exception("   ")])
def test_safe_error_response_usa_nome_da_classe_quando_sem_mensagem(exc: Exception):
    assert safe_error_response(exc) == "Exception"


# --- validação de entrada (incluindo entradas maliciosas) ------------------


@pytest.mark.parametrize(
    "valor",
    [
        "'; DROP TABLE municipios; --",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "RJ; rm -rf /",
        "99",
        "ZZ",
    ],
)
def test_validate_uf_rejeita_entrada_maliciosa(valor: str):
    with pytest.raises(IBGEValidationError):
        validate_uf(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "../../etc/passwd",
        "'; DROP TABLE municipios; --",
        "<script>alert(1)</script>",
        "330455a",
        "33045570",
        "abc",
    ],
)
def test_validate_municipality_code_rejeita_entrada_maliciosa(valor: str):
    with pytest.raises(IBGEValidationError):
        validate_municipality_code(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "6579; DROP TABLE x",
        "<script>alert(1)</script>",
        "-1",
        "../etc/passwd",
        "",
    ],
)
def test_validate_agregado_id_rejeita_entrada_maliciosa(valor: str):
    with pytest.raises(IBGEValidationError):
        validate_agregado_id(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "N3[<script>alert(1)</script>]",
        "N3[33] OR 1=1",
        "../../etc/passwd",
        "N999999",
        "",
    ],
)
def test_validate_niveis_rejeita_entrada_maliciosa(valor: str):
    with pytest.raises(IBGEValidationError):
        validate_niveis(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "2020; DROP TABLE x",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "",
        "20201301",
    ],
)
def test_validate_periodos_rejeita_entrada_maliciosa(valor: str):
    with pytest.raises(IBGEValidationError):
        validate_periodos(valor)


@pytest.mark.parametrize(
    "valor",
    [
        "93; DROP TABLE x",
        "<script>alert(1)</script>",
        "../../etc/passwd",
        "",
        "all; rm -rf",
    ],
)
def test_validate_variaveis_rejeita_entrada_maliciosa(valor: str):
    with pytest.raises(IBGEValidationError):
        validate_variaveis(valor)


@pytest.mark.parametrize("valor", ["100; DROP TABLE x", "<script>alert(1)</script>", 0, 101, True, 3.5])
def test_validate_limit_rejeita_entrada_maliciosa(valor):
    with pytest.raises(IBGEValidationError):
        validate_limit(valor)
