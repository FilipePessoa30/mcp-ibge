# Data sources & response format

## Shared response envelope

Every tool in every `mcp-data-br` module returns the same JSON envelope, on
success or failure:
`{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`.

```json
{
  "ok": true,
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {},
    "retrieved_at": "2026-06-10T12:00:00Z",
    "period": null,
    "territorial_level": "N2",
    "license_note": "Dados públicos do IBGE ...",
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [],
  "errors": []
}
```

```json
{
  "ok": false,
  "data": null,
  "metadata": { "...": "..." },
  "warnings": [],
  "errors": [
    { "message": "Erro HTTP 404 ao consultar ...", "code": null }
  ]
}
```

| Field | Description |
| --- | --- |
| `ok` | `true` on success, `false` on failure. |
| `data` | The tool's data on success (list, object or `null`); usually `null` on failure. |
| `metadata` | Provenance metadata (see table below). |
| `warnings` | List of `{"message": ..., "code": ...}` non-fatal warnings, preserved even when `ok` is `false`. |
| `errors` | List of `{"message": ..., "code": ...}` errors, with no stack traces. Empty when `ok` is `true`. |

| Field (`metadata`) | Description |
| --- | --- |
| `source_name` | Human-readable name of the official data source. |
| `source_url` / `endpoint` | The upstream URL actually queried. |
| `official_source` | Institutional URL of the official data source (distinct from `source_url`/`endpoint`). |
| `params` | Parameters used for the query, after alias/filter resolution. |
| `retrieved_at` | ISO 8601 (UTC) timestamp of the query. |
| `period` | Reference period(s) of the data (e.g. `"2024"`, `"-1"`), or `null` when not applicable. |
| `territorial_level` | Territorial level(s) (SIDRA/IBGE, e.g. `"N6"`) of the data, or `null` when not applicable. |
| `license_note` | License/usage note for the data. |
| `version` | Version of the package that produced the response. |
| `cache_hit` | `true` if the response came from the in-memory cache. |

This format lets agents (and humans) **trace any value back to its official
source**, with the exact time and parameters used — important for auditing
and for verifying data before relying on it in reports or decisions.

## Data sources by module

| Module | Source | Base URL | API docs |
| --- | --- | --- | --- |
| [`mcp-ibge`](https://github.com/FilipePessoa30/mcp-ibge/tree/main/packages/mcp_ibge) | IBGE — Instituto Brasileiro de Geografia e Estatística (Localidades, Agregados/SIDRA) | `https://servicodados.ibge.gov.br/api` | <https://servicodados.ibge.gov.br/api/docs> |

Future modules (see [roadmap.md](roadmap.md)) will add their own rows here
as they're implemented, each with its own base URL allowlist as described in
[security.md](security.md).

For IBGE-specific endpoint details, see
[packages/mcp_ibge/docs/data_sources.md](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/docs/data_sources.md).
