# Data sources & response format

## Shared response envelope

Every tool in every `mcp-data-br` module returns a JSON object with a
`metadata` field plus either `data` (success) or `error` (failure), and an
optional `warnings` list:

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "retrieved_at": "2026-06-10T12:00:00Z",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {}
  },
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" }
  ]
}
```

```json
{
  "metadata": { "...": "..." },
  "error": "Erro HTTP 404 ao consultar ..."
}
```

| Field (`metadata`) | Description |
| --- | --- |
| `source_name` | Human-readable name of the official data source. |
| `source_url` / `endpoint` | The upstream URL actually queried. |
| `retrieved_at` | ISO 8601 (UTC) timestamp of the query. |
| `params` | Parameters used for the query, after alias/filter resolution. |

This format lets agents (and humans) **trace any value back to its official
source**, with the exact time and parameters used — important for auditing
and for verifying data before relying on it in reports or decisions.

`warnings` (optional, list of strings) signals ambiguities — e.g. a
fuzzy-search tool matching multiple candidates.

## Data sources by module

| Module | Source | Base URL | API docs |
| --- | --- | --- | --- |
| [`mcp-ibge`](../packages/mcp_ibge/) | IBGE — Instituto Brasileiro de Geografia e Estatística (Localidades, Agregados/SIDRA) | `https://servicodados.ibge.gov.br/api` | <https://servicodados.ibge.gov.br/api/docs> |

Future modules (see [roadmap.md](roadmap.md)) will add their own rows here
as they're implemented, each with its own base URL allowlist as described in
[security.md](security.md).

For IBGE-specific endpoint details, see
[packages/mcp_ibge/docs/data_sources.md](../packages/mcp_ibge/docs/data_sources.md).
