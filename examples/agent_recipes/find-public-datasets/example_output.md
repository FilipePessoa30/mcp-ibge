# Exemplo de resposta

## Resposta da tool `sugerir_datasets_para_pergunta(...)`

```json
{
  "ok": true,
  "data": [
    {
      "id": "PDA0001-monitoramento-do-desmatamento-na-amazonia-legal",
      "name": "monitoramento-do-desmatamento-na-amazonia-legal",
      "title": "Monitoramento do Desmatamento na Amazônia Legal (PRODES)",
      "notes": "Taxas anuais de desmatamento por corte raso na Amazônia Legal, por município.",
      "organization": {
        "id": "inpe",
        "name": "inpe",
        "title": "Instituto Nacional de Pesquisas Espaciais"
      },
      "tags": ["desmatamento", "amazonia", "meio-ambiente", "prodes"],
      "groups": ["meio-ambiente"],
      "num_resources": 3,
      "license_id": "cc-by",
      "license_title": "Creative Commons Attribution",
      "metadata_created": "2019-03-12T10:00:00",
      "metadata_modified": "2025-08-01T14:30:00"
    }
  ],
  "metadata": {
    "source_name": "dados.gov.br - Portal Brasileiro de Dados Abertos",
    "source_url": "https://dados.gov.br/",
    "endpoint": "https://dados.gov.br/api/3/action/package_search",
    "params": {
      "pergunta": "Quais dados existem sobre desmatamento na Amazônia no Portal Brasileiro de Dados Abertos?",
      "keywords": ["desmatamento", "amazônia", "portal", "brasileiro", "abertos"],
      "q": "desmatamento amazônia portal brasileiro abertos",
      "rows": 5
    },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "cache_hit": false
  },
  "warnings": [],
  "errors": []
}
```

> Os valores acima são ilustrativos. Execute a tool para obter os datasets
> atuais — o catálogo do dados.gov.br muda com frequência.

## Resposta da tool `listar_recursos_dataset(dataset_id="monitoramento-do-desmatamento-na-amazonia-legal")`

```json
{
  "ok": true,
  "data": [
    {
      "id": "a1b2c3d4-0001",
      "name": "Taxas de desmatamento por município (CSV)",
      "description": "Série histórica de taxas anuais de desmatamento por município da Amazônia Legal.",
      "format": "CSV",
      "url": "https://dados.gov.br/dataset/monitoramento-do-desmatamento-na-amazonia-legal/resource/a1b2c3d4-0001",
      "mimetype": "text/csv",
      "size": 245760,
      "created": "2019-03-12T10:00:00",
      "last_modified": "2025-08-01T14:30:00"
    },
    {
      "id": "a1b2c3d4-0002",
      "name": "API de consulta (JSON)",
      "description": "Endpoint para consulta programática dos dados de desmatamento.",
      "format": "API",
      "url": "https://terrabrasilis.dpi.inpe.br/api/...",
      "mimetype": "application/json",
      "size": null,
      "created": "2020-01-15T09:00:00",
      "last_modified": "2025-08-01T14:30:00"
    }
  ],
  "metadata": {
    "source_name": "dados.gov.br - Portal Brasileiro de Dados Abertos",
    "source_url": "https://dados.gov.br/",
    "endpoint": "https://dados.gov.br/api/3/action/package_show",
    "params": {"id": "monitoramento-do-desmatamento-na-amazonia-legal"},
    "retrieved_at": "2026-06-12T12:00:05.000000+00:00",
    "cache_hit": false
  },
  "warnings": [],
  "errors": []
}
```

## Resposta final do agente ao usuário

> Encontrei pelo menos um dataset relevante no Portal Brasileiro de Dados
> Abertos:
>
> **Monitoramento do Desmatamento na Amazônia Legal (PRODES)** — publicado
> pelo **INPE** (Instituto Nacional de Pesquisas Espaciais). Contém taxas
> anuais de desmatamento por corte raso, por município, com 3 recursos
> disponíveis, incluindo:
>
> - CSV: série histórica de taxas por município.
> - API: endpoint para consulta programática.
>
> **Fonte**: dados.gov.br — Portal Brasileiro de Dados Abertos
> (`https://dados.gov.br/api/3/action/package_search`, palavras-chave usadas:
> "desmatamento", "amazônia", "portal", "brasileiro", "abertos").
>
> Quer que eu detalhe outro dataset ou liste mais resultados (`limite` maior)?

## Exemplo sem palavras-chave relevantes

Para `sugerir_datasets_para_pergunta(pergunta="O que tem disponível?", limite=5)`:

```json
{
  "ok": true,
  "data": [],
  "metadata": {
    "source_name": "dados.gov.br - Portal Brasileiro de Dados Abertos",
    "source_url": "https://dados.gov.br/",
    "endpoint": "https://dados.gov.br/api/3/action/package_search",
    "params": {"pergunta": "O que tem disponível?", "keywords": []},
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "cache_hit": false
  },
  "warnings": [
    {
      "message": "Não foi possível extrair palavras-chave da pergunta; nenhuma sugestão de dataset foi feita.",
      "code": null
    }
  ],
  "errors": []
}
```

O agente deve explicar que a pergunta é muito genérica e pedir um tema mais
específico (ex.: "educação", "saúde", "meio-ambiente"), em vez de chamar outra
tool tentando adivinhar um tema.

## Como verificar a fonte

- `metadata.endpoint` mostra a ação CKAN consultada
  (`package_search`/`package_show`/...); `metadata.params` mostra os
  parâmetros exatos usados.
- Para abrir um dataset no navegador, use
  `https://dados.gov.br/dados/conjuntos-dados/<name>`, onde `<name>` é o
  campo `name` retornado (ex.: `monitoramento-do-desmatamento-na-amazonia-legal`).
