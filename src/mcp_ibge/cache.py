"""Cache simples em memória, com expiração por tempo (TTL) e tamanho máximo.

Não há dependências externas: o cache vive apenas durante o processo do
servidor MCP e é apropriado para reduzir chamadas repetidas às APIs públicas
do IBGE durante uma mesma sessão.
"""

from __future__ import annotations

import time
from collections.abc import Hashable
from typing import Any


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
