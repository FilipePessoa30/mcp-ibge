"""Cache simples em memória, com expiração por tempo (TTL) e tamanho máximo.

Não há dependências externas: o cache vive apenas durante o processo do
servidor MCP e é apropriado para reduzir chamadas repetidas à API do
dados.gov.br durante uma mesma sessão.
"""

from __future__ import annotations

import time
from collections.abc import Hashable
from typing import Any

from ..config import get_settings


class TTLCache:
    """Cache chave -> valor com expiração relativa (TTL) e limite de entradas."""

    def __init__(self, ttl_seconds: float, max_size: int) -> None:
        self._ttl_seconds = ttl_seconds
        self._max_size = max_size
        self._store: dict[Hashable, tuple[float, Any]] = {}

    def get(self, key: Hashable) -> Any | None:
        """Retorna o valor associado a `key`, ou None se ausente/expirado."""
        entry = self._store.get(key)
        if entry is None:
            return None

        expires_at, value = entry
        if time.monotonic() > expires_at:
            del self._store[key]
            return None
        return value

    def set(self, key: Hashable, value: Any) -> None:
        """Armazena `value` em `key`, removendo a entrada mais antiga se necessário."""
        if self._ttl_seconds <= 0:
            return

        if key not in self._store and len(self._store) >= self._max_size:
            oldest_key = min(self._store, key=lambda k: self._store[k][0])
            del self._store[oldest_key]

        self._store[key] = (time.monotonic() + self._ttl_seconds, value)

    def clear(self) -> None:
        """Remove todas as entradas do cache."""
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)


_cache: TTLCache | None = None


def get_cache() -> TTLCache | None:
    """Retorna o cache global (singleton), ou None se o cache estiver desabilitado."""
    global _cache

    settings = get_settings()
    if not settings.cache_enabled:
        return None

    if _cache is None:
        _cache = TTLCache(ttl_seconds=settings.cache_ttl_seconds, max_size=settings.cache_max_size)
    return _cache


def clear_cache() -> None:
    """Limpa o cache global. Útil em testes e para depuração."""
    global _cache
    if _cache is not None:
        _cache.clear()
