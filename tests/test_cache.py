"""Testes do cache TTL em memória (`utils/cache.py`)."""

from __future__ import annotations

from dataclasses import dataclass

from mcp_ibge.utils.cache import TTLCache, clear_cache, get_cache


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
