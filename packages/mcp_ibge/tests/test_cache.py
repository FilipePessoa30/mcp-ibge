"""Testes do cache TTL em memória (`utils/cache.py`)."""

from __future__ import annotations

from dataclasses import dataclass

import httpx
import respx

from mcp_ibge.clients.base import AsyncIBGEClient
from mcp_ibge.clients.localidades import LOCALIDADES_PATH, LocalidadesClient
from mcp_ibge.config import get_settings
from mcp_ibge.utils.cache import TTLCache, clear_cache, get_cache
from mcp_ibge.utils.metrics import get_metrics

BASE_URL = f"{get_settings().api_base_url}{LOCALIDADES_PATH}"


@dataclass
class _FakeSettings:
    cache_enabled: bool
    cache_ttl_seconds: float = 60.0
    cache_max_size: int = 10


def test_set_e_get_retornam_valor_armazenado():
    cache = TTLCache(ttl_seconds=60, max_size=10)

    cache.set("municipio:3550308", {"nome": "São Paulo"})

    assert cache.get("municipio:3550308") == {"nome": "São Paulo"}
    assert len(cache) == 1


def test_get_chave_ausente_retorna_none():
    cache = TTLCache(ttl_seconds=60, max_size=10)

    assert cache.get("inexistente") is None


def test_entrada_expira_apos_ttl(monkeypatch):
    tempo = [0.0]
    monkeypatch.setattr("mcp_ibge.utils.cache.time.monotonic", lambda: tempo[0])

    cache = TTLCache(ttl_seconds=10, max_size=10)
    cache.set("a", "valor")

    tempo[0] = 11.0

    assert cache.get("a") is None
    assert len(cache) == 0


def test_ttl_zero_nao_armazena():
    cache = TTLCache(ttl_seconds=0, max_size=10)

    cache.set("a", "valor")

    assert cache.get("a") is None
    assert len(cache) == 0


def test_max_size_remove_entrada_mais_antiga(monkeypatch):
    tempo = [0.0]
    monkeypatch.setattr("mcp_ibge.utils.cache.time.monotonic", lambda: tempo[0])

    cache = TTLCache(ttl_seconds=100, max_size=2)
    cache.set("a", 1)
    tempo[0] = 1.0
    cache.set("b", 2)
    tempo[0] = 2.0
    cache.set("c", 3)

    assert len(cache) == 2
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_clear_remove_todas_entradas():
    cache = TTLCache(ttl_seconds=60, max_size=10)
    cache.set("a", 1)
    cache.set("b", 2)

    cache.clear()

    assert len(cache) == 0


def test_get_cache_retorna_none_se_desabilitado(monkeypatch):
    monkeypatch.setattr(
        "mcp_ibge.utils.cache.get_settings", lambda: _FakeSettings(cache_enabled=False)
    )
    clear_cache()

    assert get_cache() is None


def test_get_cache_retorna_singleton(monkeypatch):
    monkeypatch.setattr(
        "mcp_ibge.utils.cache.get_settings", lambda: _FakeSettings(cache_enabled=True)
    )
    clear_cache()

    assert get_cache() is get_cache()


@respx.mock
async def test_cliente_usa_cache_para_estado_rj(estado_rj):
    route = respx.get(f"{BASE_URL}/estados/RJ").mock(
        return_value=httpx.Response(200, json=estado_rj)
    )

    client = LocalidadesClient()
    primeira = await client.get_estado("RJ")
    segunda = await client.get_estado("RJ")

    assert primeira.data == estado_rj
    assert segunda.data == estado_rj
    assert route.call_count == 1


@respx.mock
async def test_get_json_cache_miss_depois_cache_hit():
    """A primeira chamada é um cache miss (faz requisição); a segunda, com a
    mesma URL + params, é um cache hit (não faz requisição) — chave baseada
    em endpoint + params."""
    route = respx.get(f"{BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[{"id": 33, "sigla": "RJ"}])
    )

    client = AsyncIBGEClient(LOCALIDADES_PATH)

    dados_1, cache_hit_1 = await client.get_json("/estados", params={"orderBy": "nome"})
    dados_2, cache_hit_2 = await client.get_json("/estados", params={"orderBy": "nome"})

    assert dados_1 == dados_2
    assert cache_hit_1 is False
    assert cache_hit_2 is True
    assert route.call_count == 1

    metricas = get_metrics().snapshot()
    assert metricas["total_requests"] == 2
    assert metricas["cache_misses"] == 1
    assert metricas["cache_hits"] == 1
    assert metricas["cache_hit_rate"] == 0.5
    assert metricas["errors"] == 0


@respx.mock
async def test_get_json_chave_de_cache_distingue_params_diferentes():
    """Endpoints iguais com `params` diferentes são entradas de cache
    distintas — cada combinação endpoint + params gera uma chave própria."""
    route = respx.get(f"{BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[{"id": 33, "sigla": "RJ"}])
    )

    client = AsyncIBGEClient(LOCALIDADES_PATH)

    await client.get_json("/estados", params={"orderBy": "nome"})
    await client.get_json("/estados", params={"orderBy": "id"})

    assert route.call_count == 2
    assert get_metrics().snapshot()["cache_misses"] == 2


@respx.mock
async def test_get_json_apos_ttl_expirado_e_cache_miss(monkeypatch):
    """Após o TTL expirar, a entrada de cache é descartada e a próxima
    chamada faz uma nova requisição (cache miss)."""
    tempo = [0.0]
    monkeypatch.setattr("mcp_ibge.utils.cache.time.monotonic", lambda: tempo[0])

    settings = get_settings().model_copy(update={"cache_ttl_seconds": 10.0})
    monkeypatch.setattr("mcp_ibge.utils.cache.get_settings", lambda: settings)
    # Força a recriação do singleton para que o novo `cache_ttl_seconds` seja aplicado.
    monkeypatch.setattr("mcp_ibge.utils.cache._cache", None)

    route = respx.get(f"{BASE_URL}/estados").mock(
        return_value=httpx.Response(200, json=[{"id": 33, "sigla": "RJ"}])
    )

    client = AsyncIBGEClient(LOCALIDADES_PATH)

    _, cache_hit_1 = await client.get_json("/estados")
    assert cache_hit_1 is False
    assert route.call_count == 1

    tempo[0] = 11.0  # avança além do TTL de 10s

    _, cache_hit_2 = await client.get_json("/estados")
    assert cache_hit_2 is False
    assert route.call_count == 2

    metricas = get_metrics().snapshot()
    assert metricas["total_requests"] == 2
    assert metricas["cache_misses"] == 2
    assert metricas["cache_hits"] == 0
