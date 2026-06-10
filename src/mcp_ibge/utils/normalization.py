"""Normalização textual usada nas buscas (ex.: por nome de município)."""

from __future__ import annotations

import unicodedata


def normalize_text(text: str) -> str:
    """Remove acentos e normaliza para minúsculas/sem espaços nas pontas.

    Ex.: "São José dos Campos" -> "sao jose dos campos".
    """
    decomposed = unicodedata.normalize("NFKD", text)
    without_accents = "".join(c for c in decomposed if not unicodedata.combining(c))
    return without_accents.lower().strip()
