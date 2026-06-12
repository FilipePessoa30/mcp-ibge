"""Métricas internas simples, em memória, para observabilidade do servidor.

Cada chamada a `AsyncIBGEClient.get_json` (`clients/base.py`) registra um
ponto de métrica via `get_metrics().record_request(...)`. O snapshot agregado
é exposto pelo resource `mcp-data-br://status` (ver `server.py`). As métricas
vivem apenas em memória do processo, não persistem entre execuções e não
contêm dados sensíveis — apenas contadores agregados e latência média.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Metrics:
    """Contadores agregados de chamadas ao(s) cliente(s) HTTP do IBGE."""

    total_requests: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    errors: int = 0
    _total_latency_ms: float = field(default=0.0, repr=False)

    def record_request(self, *, cache_hit: bool, latency_ms: float, error: bool) -> None:
        """Registra uma chamada a `get_json`, com seu resultado e latência."""
        self.total_requests += 1
        if cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
        if error:
            self.errors += 1
        self._total_latency_ms += latency_ms

    @property
    def cache_hit_rate(self) -> float:
        """Proporção de requisições servidas pelo cache (0.0 a 1.0)."""
        if self.total_requests == 0:
            return 0.0
        return self.cache_hits / self.total_requests

    @property
    def average_latency_ms(self) -> float:
        """Latência média (ms) de todas as chamadas a `get_json` registradas."""
        if self.total_requests == 0:
            return 0.0
        return self._total_latency_ms / self.total_requests

    def snapshot(self) -> dict[str, int | float]:
        """Retorna os contadores e taxas derivadas, prontos para serialização JSON."""
        return {
            "total_requests": self.total_requests,
            "cache_hits": self.cache_hits,
            "cache_misses": self.cache_misses,
            "errors": self.errors,
            "cache_hit_rate": round(self.cache_hit_rate, 4),
            "average_latency_ms": round(self.average_latency_ms, 3),
        }

    def reset(self) -> None:
        """Zera todos os contadores. Útil em testes para isolar medições."""
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        self.errors = 0
        self._total_latency_ms = 0.0


_metrics = Metrics()


def get_metrics() -> Metrics:
    """Retorna a instância global (singleton) de métricas do processo."""
    return _metrics


def reset_metrics() -> None:
    """Zera as métricas globais. Útil em testes para isolar medições."""
    _metrics.reset()
