"""Tipos compartilhados entre os clientes de API do IBGE."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class IBGEResult:
    """Resultado de uma chamada a uma API do IBGE, com dados para rastreabilidade.

    Attributes:
        data: Corpo da resposta já decodificado (lista ou dicionário JSON).
        endpoint: URL completa do endpoint consultado (sem query string).
        params: Parâmetros relevantes da consulta, usados nos metadados de
            rastreabilidade da resposta da tool.
    """

    data: Any
    endpoint: str
    params: dict[str, Any] = field(default_factory=dict)
