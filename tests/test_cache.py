"""Testes do cache TTL em memória."""

from __future__ import annotations

import time

from mcp_ibge.cache import TTLCache


def test_get_set_basico():
    cache = TTLCache(ttl_seconds=60, max_size=10)
    cache.set("a", 1)
    assert cache.get("a") == 1
    assert cache.get("b") is None


def test_expiracao_por_ttl():
    cache = TTLCache(ttl_seconds=0.01, max_size=10)
    cache.set("a", 1)
    assert cache.get("a") == 1
    time.sleep(0.02)
    assert cache.get("a") is None


def test_ttl_zero_nao_armazena():
    cache = TTLCache(ttl_seconds=0, max_size=10)
    cache.set("a", 1)
    assert cache.get("a") is None
    assert len(cache) == 0


def test_evicao_por_tamanho_maximo():
    cache = TTLCache(ttl_seconds=60, max_size=2)
    cache.set("a", 1)
    time.sleep(0.001)
    cache.set("b", 2)
    time.sleep(0.001)
    cache.set("c", 3)

    assert len(cache) == 2
    # "a" foi a entrada mais antiga e deve ter sido removida.
    assert cache.get("a") is None
    assert cache.get("b") == 2
    assert cache.get("c") == 3


def test_clear():
    cache = TTLCache(ttl_seconds=60, max_size=10)
    cache.set("a", 1)
    cache.clear()
    assert cache.get("a") is None
    assert len(cache) == 0
