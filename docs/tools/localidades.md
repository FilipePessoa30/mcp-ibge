# Tools: Localidades

Tools for Brazil's administrative geography — regions, states, municipalities
and districts — backed by the
[IBGE Localidades API](https://servicodados.ibge.gov.br/api/docs/localidades).
All tools return the standard envelope
(`{"ok", "data", "metadata", "warnings", "errors"}`) — see
[Data Sources & Response Format](../data_sources.md).

> 🇧🇷 **Nota**: os nomes das *tools* e dos campos de dados (`nome`, `sigla`,
> `uf_sigla`, ...) permanecem em português, seguindo a API do IBGE.

## Common errors

In addition to the per-tool errors below, every tool in this module can
return:

| Situation | Error message |
| --- | --- |
| Network/timeout failure calling the IBGE API | `Falha ao conectar à API do IBGE: <detail>` / `Timeout ao consultar a API do IBGE.` |
| IBGE API returns HTTP 4xx/5xx | `IBGE retornou HTTP <status> para <url>` |
| Response exceeds the size limit (`MCP_IBGE_MAX_RESPONSE_SIZE_BYTES`) | `Resposta da API do IBGE excede o limite de tamanho permitido.` |

## 1. `listar_regioes`

List Brazil's 5 geographic regions (Norte, Nordeste, Sudeste, Sul,
Centro-Oeste).

**Parameters**: none.

```python
listar_regioes()
```

```json
{
  "ok": true,
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" },
    { "id": 2, "sigla": "NE", "nome": "Nordeste" },
    { "id": 3, "sigla": "SE", "nome": "Sudeste" },
    { "id": 4, "sigla": "S", "nome": "Sul" },
    { "id": 5, "sigla": "CO", "nome": "Centro-Oeste" }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {},
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00"
  },
  "warnings": [],
  "errors": []
}
```

**Source**: `GET /localidades/regioes`.

---

## 2. `listar_estados`

List the 26 states and the Federal District, sorted by name (locale-aware,
accent/case-insensitive). Each item includes `id` (IBGE state code), `sigla`,
`nome` and the `regiao` (`id`, `sigla`, `nome`) it belongs to.

**Parameters**: none.

```python
listar_estados()
```

```json
{
  "ok": true,
  "data": [
    {
      "id": 12, "sigla": "AC", "nome": "Acre",
      "regiao": { "id": 1, "sigla": "N", "nome": "Norte" }
    },
    {
      "id": 33, "sigla": "RJ", "nome": "Rio de Janeiro",
      "regiao": { "id": 3, "sigla": "SE", "nome": "Sudeste" }
    }
  ]
}
```

**Source**: `GET /localidades/estados`.

---

## 3. `listar_municipios`

List the municipalities of a state (UF), with the state and region resolved
on each item (`uf_sigla`, `uf_nome`, `regiao_nome`). The original IBGE JSON
for each municipality is available in `raw`.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `uf` | `string` | yes | State abbreviation (e.g. `"RJ"`, `"SP"`, `"MG"`) or IBGE state code (e.g. `"33"`). |

```python
listar_municipios(uf="RJ")
```

```json
{
  "ok": true,
  "data": [
    {
      "id": 3303302,
      "nome": "Niterói",
      "uf_id": 33,
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "raw": { "...": "original IBGE JSON, with microrregiao/mesorregiao/UF" }
    }
  ]
}
```

**Errors**:

| Situation | Error message |
| --- | --- |
| `uf` doesn't match any valid abbreviation/code | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |

**Source**: `GET /localidades/estados/{uf}/municipios`.

---

## 4. `buscar_municipio`

Fuzzy, accent/case-insensitive municipality search. The search tries, in
order: (1) exact match on the normalized name, (2) names that "contain" the
search term, and finally (3) text similarity (`difflib`). Without `uf`,
searches all municipalities in Brazil; with `uf`, restricts to that state.
When more than one candidate is found, the response includes a `warnings`
entry listing the candidates and suggesting a more specific search.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `nome` | `string` | yes | — | Name (or part of the name) of the municipality to search for. |
| `uf` | `string \| null` | no | `null` | Restrict the search to this state (abbreviation or code). |
| `limite` | `integer` | no | `10` | Maximum number of candidates returned (1–50). |

```python
buscar_municipio(nome="São José")
```

```json
{
  "ok": true,
  "data": [
    {
      "id": 3548807, "nome": "São José dos Campos",
      "uf_id": 35, "uf_sigla": "SP", "uf_nome": "São Paulo", "regiao_nome": "Sudeste",
      "raw": { "...": "..." }
    },
    {
      "id": 4125506, "nome": "São José dos Pinhais",
      "uf_id": 41, "uf_sigla": "PR", "uf_nome": "Paraná", "regiao_nome": "Sul",
      "raw": { "...": "..." }
    }
  ],
  "warnings": [
    {
      "message": "Encontrados 2 municípios para \"São José\": São José dos Campos, São José dos Pinhais. Refine a busca com \"uf\" ou um nome mais específico.",
      "code": null
    }
  ]
}
```

**Possible warnings**: a `"Encontrados N municípios para ..."` warning
whenever more than one candidate is found (the name list is truncated to
`limite` items, but `N` is the total before truncation).

**Errors**: same `uf` validation as `listar_municipios`, plus the
[common errors](#common-errors). No result is **not** an error — `data` is
`[]` with no `warnings`.

**Source**: `GET /localidades/municipios` (without `uf`) or
`GET /localidades/estados/{uf}/municipios` (with `uf`), filtered locally by
name.

---

## 5. `obter_codigo_municipio`

Get the 7-digit IBGE code for a **single** municipality, from its name and
state. Internally reuses the same fuzzy search as
[`buscar_municipio`](#4-buscar_municipio) (limited to 5 candidates), but
requires **exactly one** match — otherwise it returns an error.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `nome` | `string` | yes | Municipality name. |
| `uf` | `string` | yes | State abbreviation (e.g. `"SP"`) or IBGE state code. |

```python
obter_codigo_municipio(nome="Niterói", uf="RJ")
```

```json
{
  "ok": true,
  "data": 3303302,
  "metadata": {
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "params": { "nome": "Niterói", "limite": 5, "uf": "RJ" }
  }
}
```

**Errors**:

| Situation | Error message |
| --- | --- |
| No municipality matches `nome` in `uf` | `Nenhum município encontrado para "<nome>" na UF "<uf>".` |
| More than one municipality matches | `Encontrados N municípios para "<nome>": <nomes>. Refine a busca com "uf" ou um nome mais específico.` |
| `uf` doesn't match any valid abbreviation/code | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |

**Source**: `GET /localidades/estados/{uf}/municipios`, filtered locally by
name.

---

## 6. `obter_municipio_por_codigo`

Get municipality details from its 7-digit IBGE code, with state and region
resolved (`uf_sigla`, `uf_nome`, `regiao_nome`) — same item shape as
[`listar_municipios`](#3-listar_municipios) and
[`buscar_municipio`](#4-buscar_municipio).

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `codigo_ibge` | `integer` | yes | 7-digit IBGE municipality code (e.g. `3550308` = São Paulo). |

```python
obter_municipio_por_codigo(codigo_ibge=3303302)
```

```json
{
  "ok": true,
  "data": {
    "id": 3303302,
    "nome": "Niterói",
    "uf_id": 33,
    "uf_sigla": "RJ",
    "uf_nome": "Rio de Janeiro",
    "regiao_nome": "Sudeste",
    "raw": { "...": "original IBGE JSON" }
  }
}
```

**Errors**:

| Situation | Error message |
| --- | --- |
| `codigo_ibge` doesn't match any municipality | `IBGE retornou HTTP 404 para https://servicodados.ibge.gov.br/api/v1/localidades/municipios/<codigo_ibge>` |

**Source**: `GET /localidades/municipios/{codigo_ibge}`.

---

## 7. `listar_distritos`

List the districts of a municipality, identified by its 7-digit IBGE code.
Each item includes `id`, `nome`, `municipio_id` and `municipio_nome`
(resolved from the API's nested JSON), plus the original JSON in `raw`.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `codigo_municipio` | `integer` | yes | 7-digit IBGE municipality code (e.g. `3550308` = São Paulo). |

```python
listar_distritos(codigo_municipio=3304557)
```

```json
{
  "ok": true,
  "data": [
    {
      "id": 330455705,
      "nome": "Rio de Janeiro",
      "municipio_id": 3304557,
      "municipio_nome": "Rio de Janeiro",
      "raw": { "...": "..." }
    }
  ]
}
```

**Errors**:

| Situation | Error message |
| --- | --- |
| `codigo_municipio` doesn't match any municipality | `IBGE retornou HTTP 404 para https://servicodados.ibge.gov.br/api/v1/localidades/municipios/<codigo_municipio>/distritos` |

**Source**: `GET /localidades/municipios/{codigo_municipio}/distritos`.

---

For the full reference (including parameter validation details and every
error message), see
[`packages/mcp_ibge/docs/tools.md`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/docs/tools.md#localidades).
