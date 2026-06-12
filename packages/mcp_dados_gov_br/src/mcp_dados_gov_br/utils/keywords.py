"""Extração simples de palavras-chave de uma pergunta em português.

Usado por `sugerir_datasets_para_pergunta` para transformar uma pergunta em
linguagem natural em uma consulta textual (`q`) para `package_search`, sem
nenhum modelo de linguagem: apenas tokenização e remoção de stopwords.
"""

from __future__ import annotations

import re

_TOKEN_RE = re.compile(r"[^\W\d_]+", re.UNICODE)

# Tamanho mínimo de um token para ser considerado palavra-chave.
_TAMANHO_MINIMO = 3

# Stopwords em português (artigos, preposições, pronomes, conectivos) e
# termos genéricos demais para refinar uma busca de datasets (ex.: "dados",
# "informações"). Mantida deliberadamente pequena e sem dependências
# externas — não é um analisador linguístico completo.
STOPWORDS_PT: frozenset[str] = frozenset(
    {
        "a",
        "ao",
        "aos",
        "aquela",
        "aquelas",
        "aquele",
        "aqueles",
        "aquilo",
        "as",
        "até",
        "com",
        "como",
        "da",
        "das",
        "de",
        "dela",
        "delas",
        "dele",
        "deles",
        "depois",
        "do",
        "dos",
        "e",
        "ela",
        "elas",
        "ele",
        "eles",
        "em",
        "entre",
        "era",
        "essa",
        "essas",
        "esse",
        "esses",
        "esta",
        "estas",
        "este",
        "estes",
        "eu",
        "foi",
        "for",
        "há",
        "isso",
        "isto",
        "já",
        "lhe",
        "lhes",
        "mais",
        "mas",
        "me",
        "mesmo",
        "meu",
        "meus",
        "minha",
        "minhas",
        "muito",
        "na",
        "nas",
        "nem",
        "no",
        "nos",
        "nós",
        "nossa",
        "nossas",
        "nosso",
        "nossos",
        "num",
        "numa",
        "o",
        "os",
        "ou",
        "para",
        "pela",
        "pelas",
        "pelo",
        "pelos",
        "por",
        "qual",
        "quais",
        "quando",
        "quanto",
        "quantos",
        "quantas",
        "que",
        "quem",
        "se",
        "sem",
        "ser",
        "seu",
        "seus",
        "só",
        "sua",
        "suas",
        "também",
        "te",
        "tem",
        "ter",
        "teu",
        "teus",
        "tu",
        "tua",
        "tuas",
        "um",
        "uma",
        "umas",
        "uns",
        "você",
        "vocês",
        # Termos genéricos demais para refinar a busca de datasets.
        "existe",
        "existem",
        "gostaria",
        "preciso",
        "precisa",
        "quero",
        "queria",
        "onde",
        "encontrar",
        "achar",
        "buscar",
        "procurar",
        "dado",
        "dados",
        "dataset",
        "datasets",
        "informação",
        "informações",
        "sobre",
        "publico",
        "público",
        "publicos",
        "públicos",
    }
)


def extract_keywords(text: str, *, max_keywords: int = 8) -> list[str]:
    """Extrai até `max_keywords` palavras-chave de `text`.

    Tokeniza `text` em palavras (ignorando números e pontuação), remove
    stopwords e tokens muito curtos (< `_TAMANHO_MINIMO` caracteres), e
    preserva a ordem original sem repetições. Retorna uma lista vazia se
    nenhum token relevante for encontrado.
    """
    tokens = (token.lower() for token in _TOKEN_RE.findall(text))

    keywords: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if len(token) < _TAMANHO_MINIMO or token in STOPWORDS_PT or token in seen:
            continue
        seen.add(token)
        keywords.append(token)
        if len(keywords) >= max_keywords:
            break
    return keywords
