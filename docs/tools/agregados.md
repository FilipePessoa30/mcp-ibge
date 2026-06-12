# Tools: Agregados / SIDRA

Tools for [SIDRA](https://sidra.ibge.gov.br/) (Sistema IBGE de Recuperação
Automática) — generic discovery and query of **any** SIDRA aggregate
(table), backed by the
[IBGE Agregados (SIDRA) API](https://servicodados.ibge.gov.br/api/docs/agregados).
All tools return the standard envelope — see
[Data Sources & Response Format](../data_sources.md).

As of v0.2.0, the 6 core tools below (`listar_agregados` ...
`consultar_agregado`) are **stable**. The population indicator
(`consultar_populacao_municipio`) remains **experimental** — see
[Module: mcp-ibge](../modules/ibge.md).

## How to discover an aggregate, variable, period and location

SIDRA has thousands of aggregates (tables), each with its own variables,
periods, classifications and territorial levels. Before calling
[`consultar_agregado`](#13-consultar_agregado), use the metadata tools in
this order:

1. **Find the aggregate** — [`listar_agregados`](#8-listar_agregados) with
   `pesquisa` (e.g. `"Índice Nacional de Preços ao Consumidor Amplo"`),
   `assunto` (e.g. `"Índices de preços"`) and/or `texto` (local name filter)
   to discover the `agregado_id`.
2. **Confirm the aggregate** —
   [`obter_metadados_agregado`](#9-obter_metadados_agregado) returns
   `pesquisa`, `assunto`, `periodicidade`, and the full `variaveis`,
   `classificacoes` and `nivelTerritorial` in `raw`.
3. **Pick the variable(s)** —
   [`listar_variaveis_agregado`](#10-listar_variaveis_agregado) returns
   `id`, `nome` and `unidade` of each variable. The `id` goes into the
   `variaveis` parameter of `consultar_agregado` (one ID, comma-separated
   list, or `"all"`).
4. **Pick the period(s)** —
   [`listar_periodos_agregado`](#11-listar_periodos_agregado) returns
   available periods (e.g. `"202604"` for April/2026 in a monthly aggregate,
   `"2024"` for an annual one). The `id` goes into `periodos` — which also
   accepts a range (`"2010-2020"`), a list (`"2019,2021"`) or a relative
   value (`"-1"` = most recent period, `"-6"` = last 6 periods).
5. **Pick the location(s)** —
   [`listar_localidades_agregado`](#12-listar_localidades_agregado) with a
   `niveis` (e.g. `"N1"` = Brazil, `"N3"` = states, `"N6"` = municipalities,
   as seen in `nivelTerritorial` in step 2) returns `id` and `nome` of each
   location available **for that aggregate**. The `id` goes into
   `localidades` of `consultar_agregado`, as `N<nivel>[<id1>,<id2>,...]` (or
   `N<nivel>[all]` for all).
6. **Query the data** —
   [`consultar_agregado`](#13-consultar_agregado) with `agregado_id`,
   `variaveis`, `localidades` and `periodos` resolved above. If the
   aggregate has classifications (visible in `raw.classificacoes` from step
   2), use the `classificacao` parameter as
   `"<id_classificacao>[<id_categoria>]"`.

### Worked example: monthly IPCA variation (aggregate `7060`)

```python
# 1. Find the aggregate
listar_agregados(pesquisa="Índice Nacional de Preços ao Consumidor Amplo", texto="a partir de janeiro/2020")
# -> agregado_id = "7060"

# 2. Confirm metadata (variables, classifications, territorial levels)
obter_metadados_agregado(agregado_id="7060")
# -> variable "63" = "IPCA - Variação mensal" (%)
# -> classification "315" has category "7169" = "Índice geral"
# -> nivelTerritorial.Administrativo = ["N1", "N6", "N7"]

# 3. Available variables
listar_variaveis_agregado(agregado_id="7060")

# 4. Available periods (e.g. "202604" = April/2026)
listar_periodos_agregado(agregado_id="7060")

# 5. Available locations at the Brazil level
listar_localidades_agregado(agregado_id="7060", niveis="N1")

# 6. Query the monthly IPCA variation (overall index) for Brazil, latest period
consultar_agregado(
    agregado_id="7060",
    variaveis="63",
    localidades="N1[all]",
    periodos="-1",
    classificacao="315[7169]",
)
```

Step 6 returns, for example, `valor: 0.67` (0.67% monthly variation in
April/2026), with `unidade: "%"`, `localidade_nome: "Brasil"` and
`periodo: "202604"`.

## Common errors

In addition to the per-tool errors below, every tool in this module can
return:

| Situation | Error message |
| --- | --- |
| Network/timeout failure calling the IBGE API | `Falha ao conectar à API do IBGE: <detail>` / `Timeout ao consultar a API do IBGE.` |
| IBGE API returns HTTP 4xx/5xx | `IBGE retornou HTTP <status> para <url>` |
| Response exceeds the size limit | `Resposta da API do IBGE excede o limite de tamanho permitido.` |

## 8. `listar_agregados`

List SIDRA aggregates (tables), each with `id` and `nome`. `pesquisa` and
`assunto` are filters applied by the API itself; `texto` is an additional
local filter on the aggregate `nome` (case-insensitive substring).

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `pesquisa` | `string \| null` | no | Filter by source survey (e.g. `"Censo Demográfico"`). |
| `assunto` | `string \| null` | no | Filter by subject name (e.g. `"População"`). |
| `texto` | `string \| null` | no | Additional local text filter on aggregate names. |

```python
listar_agregados(assunto="População")
```

```json
{
  "ok": true,
  "data": [
    { "id": "6579", "nome": "População residente estimada" },
    { "id": "9514", "nome": "População residente, por sexo, situação e grupos de idade" }
  ]
}
```

Filters that match nothing return `data: []`, not an error.

**Source**: `GET /agregados`.

---

## 9. `obter_metadados_agregado`

Get metadata for a SIDRA aggregate. `pesquisa`, `assunto` and `periodicidade`
(`"anual"`, `"mensal"`, ...) are available directly; the full API JSON —
including `variaveis`, `classificacoes` and `nivelTerritorial` — is in `raw`.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agregado_id` | `string` | yes | SIDRA aggregate ID (e.g. `"6579"` = "População residente estimada"). |

```python
obter_metadados_agregado(agregado_id="6579")
```

```json
{
  "ok": true,
  "data": {
    "id": "6579",
    "nome": "População residente estimada",
    "pesquisa": "Estimativas de População",
    "assunto": "População",
    "periodicidade": "anual",
    "raw": {
      "periodicidade": { "frequencia": "anual", "inicio": 2001, "fim": 2024 },
      "nivelTerritorial": { "Administrativo": ["N1", "N2", "N3", "N6"], "Especial": [], "IBGE": [] },
      "variaveis": [
        { "id": 9324, "nome": "População residente estimada", "unidade": "Pessoas", "sumarizacao": [] }
      ],
      "classificacoes": []
    }
  }
}
```

**Errors**: `Parâmetro "agregado_id" não pode ser vazio.` /
`Agregado "<agregado_id>" não encontrado.`

**Source**: `GET /agregados/{agregado_id}/metadados`.

---

## 10. `listar_variaveis_agregado`

List the variables available in an aggregate — `id`, `nome`, `unidade` (e.g.
`"Pessoas"`, `"Reais"`), plus the original JSON in `raw`. Use a variable's
`id` in the `variaveis` parameter of [`consultar_agregado`](#13-consultar_agregado).

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agregado_id` | `string` | yes | SIDRA aggregate ID. |

```python
listar_variaveis_agregado(agregado_id="6579")
```

```json
{
  "ok": true,
  "data": [
    { "id": "9324", "nome": "População residente estimada", "unidade": "Pessoas", "raw": { "...": "..." } }
  ]
}
```

**Errors**: same as `obter_metadados_agregado`.

**Source**: `GET /agregados/{agregado_id}/variaveis`.

---

## 11. `listar_periodos_agregado`

List the periods available for an aggregate — `id` (e.g. `"2024"`) and
`nome`. Use a period's `id` in `periodos` of `consultar_agregado`.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agregado_id` | `string` | yes | SIDRA aggregate ID. |

```python
listar_periodos_agregado(agregado_id="6579")
```

```json
{
  "ok": true,
  "data": [
    { "id": "2023", "nome": "2023" },
    { "id": "2024", "nome": "2024" }
  ]
}
```

**Errors**: same as `obter_metadados_agregado`.

**Source**: `GET /agregados/{agregado_id}/periodos`.

---

## 12. `listar_localidades_agregado`

List the locations available for an aggregate at one or more territorial
levels (e.g. `"N1"` = Brazil, `"N2"` = regions, `"N3"` = states, `"N6"` =
municipalities). **No typed schema** for this endpoint — each item is
returned as-is from the API (`id`, `nome`, `nivel`, ...).

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `agregado_id` | `string` | yes | SIDRA aggregate ID. |
| `niveis` | `string` | yes | Territorial level (e.g. `"N6"`) or multiple levels separated by `"\|"` (e.g. `"N1\|N3"`). |

```python
listar_localidades_agregado(agregado_id="6579", niveis="N6")
```

```json
{
  "ok": true,
  "data": [
    { "id": "3303302", "nome": "Niterói", "nivel": { "id": "N6", "nome": "Município" } },
    { "id": "3304557", "nome": "Rio de Janeiro", "nivel": { "id": "N6", "nome": "Município" } }
  ]
}
```

**Errors**: empty `agregado_id`/`niveis`, or
`Nenhuma localidade encontrada para o agregado "<agregado_id>" no(s) nível(is) "<niveis>".`

**Source**: `GET /agregados/{agregado_id}/localidades/{niveis}`.

---

## 13. `consultar_agregado`

Query an aggregate's values for given variables, periods and locations.
Returns a **flattened** list — one item per (variable, location, period)
combination — each with `agregado_id`, `variavel_id`, `localidade_id`,
`localidade_nome`, `periodo`, `valor` (number, or `null` when SIDRA marks the
data as missing/confidential — markers `"-"`, `".."`, `"..."`, `"X"`) and
`unidade`. The original series item is in `raw`.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `agregado_id` | `string` | yes | — | SIDRA aggregate ID (e.g. `"6579"`). |
| `variaveis` | `string` | yes | — | Variable ID, comma-separated list (e.g. `"9324,9325"`), or `"all"`. |
| `localidades` | `string` | yes | — | Territorial unit as `N<nivel>[<ids>]`, e.g. `"N1[all]"` (Brazil), `"N3[all]"` (all states), `"N6[3303302]"` (Niterói). `"BR"` is a shortcut for `"N1[all]"`. |
| `periodos` | `string` | no | `"-6"` | A year (`"2021"`), range (`"2010-2020"`), list (`"2019,2021"`) or relative (`"-6"` = last 6 periods, `"-1"` = most recent). |
| `classificacao` | `string \| null` | no | `null` | Optional classification, `"<id_classificacao>[<id_categoria>]"`. |
| `view` | `string \| null` | no | `null` | Alternative API response format (e.g. `"flat"`). |

```python
consultar_agregado(
    agregado_id="6579",
    variaveis="9324",
    localidades="N6[3303302]",
    periodos="2024",
)
```

```json
{
  "ok": true,
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3303302",
      "localidade_nome": "Niterói",
      "periodo": "2024",
      "valor": 516981.0,
      "unidade": "Pessoas",
      "raw": {
        "localidade": { "id": "3303302", "nome": "Niterói", "nivel": { "id": "N6", "nome": "Município" } },
        "serie": { "2024": "516981" }
      }
    }
  ]
}
```

`valor` can be `null` for missing/confidential SIDRA data — this does **not**
generate a warning here (unlike `consultar_populacao_municipio`, which adds
an explicit warning).

**Errors**:

| Situation | Error message |
| --- | --- |
| Any required parameter is empty | `Parâmetro "<nome>" não pode ser vazio.` |
| No data for the given combination (often HTTP 200 + empty body) | `Nenhum dado encontrado para o agregado "<agregado_id>", variável(is) "<variaveis>" em "<localidades>" no(s) período(s) "<periodos>".` |

**Source**: `GET /agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}`
(with `localidades`, `classificacao`, `view` as query string).

---

## 14. `consultar_populacao_municipio`

_Experimental._ Estimated resident population of a municipality, by `nome`
and `uf`. Internally: (1) resolves the IBGE code via
[`obter_codigo_municipio`](../tools/localidades.md#5-obter_codigo_municipio);
(2) queries SIDRA aggregate `6579` ("Estimativas de população residente"),
variable `9324`, via [`consultar_agregado`](#13-consultar_agregado).

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `nome` | `string` | yes | Municipality name. |
| `uf` | `string` | yes | State abbreviation or IBGE code. |
| `ano` | `integer \| null` | no | Reference year. Without it, uses the most recent period available (`periodos="-1"`). |

```python
consultar_populacao_municipio(nome="Niterói", uf="RJ")
```

```json
{
  "ok": true,
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3303302",
      "localidade_nome": "Niterói",
      "periodo": "2024",
      "valor": 516981.0,
      "unidade": "Pessoas",
      "raw": { "...": "..." }
    }
  ],
  "warnings": [
    {
      "message": "Nenhum \"ano\" foi informado: retornado o período mais recente disponível no SIDRA (\"2024\"), que pode não ser o ano corrente.",
      "code": null
    }
  ]
}
```

**Possible warnings**:

- `Nenhum "ano" foi informado: ...` — when `ano` is omitted.
- `O valor de população não está disponível (dado ausente ou sigiloso no SIDRA) ...` — when an item has `valor: null`.
- Warnings from `obter_codigo_municipio` (e.g. ambiguous name) on error.

**Errors**: same as `obter_codigo_municipio`, plus:

`Não foi possível obter a população do município <codigo_municipio> usando o
agregado 6579 (variável 9324) do SIDRA: <detail>. Essa tabela pode ter sido
descontinuada ou renomeada pelo IBGE. Use \`consultar_agregado\` diretamente,
após localizar os IDs corretos com \`listar_agregados\`,
\`obter_metadados_agregado\` e \`listar_variaveis_agregado\`.`

**Source**: IBGE Localidades API (code resolution) +
`GET /agregados/6579/periodos/{periodos}/variaveis/9324`
([SIDRA table 6579](https://sidra.ibge.gov.br/tabela/6579)).

---

## SIDRA Query Builder

The Agregados/SIDRA API requires parameters that are hard to discover
(`agregado_id`, `variaveis`, `periodos`, `localidades`, `classificacao`,
`view`). These 7 tools form a **discovery, suggestion and validation** layer
on top of the tools above, helping an agent build a correct query for
[`consultar_agregado`](#13-consultar_agregado) without guessing IDs.

!!! note "No LLM involved"
    `sugerir_consulta_sidra` is a simple heuristic: it extracts keywords from
    the question (removing accents, case and Portuguese stopwords) and
    scores aggregates/variables by keyword matches against the `nome`
    returned by the API, plus a small keyword → territorial-level dictionary.
    The result is always a **proposal** — it never executes a query — and
    always includes `warnings` explaining the heuristic and any alternative
    aggregates.

Recommended flow:

1. **Discover the aggregate** —
   [`buscar_tabelas_sidra`](#example-buscar_tabelas_sidra) (by topic) or
   [`sugerir_consulta_sidra`](#example-sugerir_consulta_sidra) (by
   natural-language question, returns a full proposal).
2. **Understand the aggregate** — `explicar_tabela_sidra`,
   `listar_variaveis_tabela_sidra` and `listar_classificacoes_tabela_sidra`
   (see table below).
3. **Validate before spending a data request** —
   [`validar_consulta_sidra`](#example-validar_consulta_sidra-invalid-variable)
   checks the proposed parameters against the aggregate's real metadata.
4. **Execute safely** — `executar_consulta_sidra_validada` repeats step 3's
   validation and only calls
   [`consultar_agregado`](#13-consultar_agregado) if it passes.

| # | Tool | Description |
| --- | --- | --- |
| 15 | `buscar_tabelas_sidra` | Find aggregates related to a `tema`, ranked by keyword match against `listar_agregados`. Returns `id`, `nome`, `pontuacao`. |
| 16 | `explicar_tabela_sidra` | Structured explanation of an aggregate: `periodicidade`, `niveis_territoriais`, `variaveis`, `classificacoes`, and a `limitacoes` text summary. |
| 17 | `listar_variaveis_tabela_sidra` | Variables of an aggregate, from `/metadados` (equivalent to `listar_variaveis_agregado`). |
| 18 | `listar_classificacoes_tabela_sidra` | Classifications of an aggregate (`id`, `nome`, `categorias`); empty list = no extra classifications. |
| 19 | `sugerir_consulta_sidra` | Propose `agregado_id`/`variaveis`/`localidades`/`periodos` for a natural-language `pergunta`, **without executing**. Includes up to 5 `alternativas`. |
| 20 | `validar_consulta_sidra` | Validate `variaveis`/`localidades`/`periodos`/`classificacao` for an `agregado_id` against real metadata — format + existence checks. |
| 21 | `executar_consulta_sidra_validada` | Validate (as #20), then call `consultar_agregado` only if `data.valido` is `true`. |

### Example: `buscar_tabelas_sidra`

```python
buscar_tabelas_sidra(tema="população dos municípios")
```

```json
{
  "ok": true,
  "data": [
    { "id": "6579", "nome": "População residente estimada", "pontuacao": 1 },
    { "id": "9514", "nome": "População residente, por sexo, situação e grupos de idade", "pontuacao": 1 }
  ]
}
```

If no keyword matches, `data: []` with a warning suggesting different
keywords or `listar_agregados`.

### Example: `sugerir_consulta_sidra`

```python
sugerir_consulta_sidra(pergunta="qual a população estimada dos municípios em 2024?")
```

```json
{
  "ok": true,
  "data": {
    "agregado_id": "6579",
    "agregado_nome": "População residente estimada",
    "variaveis": "9324",
    "variavel_nome": "População residente estimada",
    "localidades": "N6[all]",
    "periodos": "-1",
    "classificacao": null,
    "alternativas": [
      { "id": "9514", "nome": "População residente, por sexo, situação e grupos de idade", "pontuacao": 1 }
    ]
  },
  "warnings": [
    {
      "message": "Sugestão gerada por busca de palavras-chave em metadados (sem uso de modelos de linguagem); revise os parâmetros antes de executar, com `validar_consulta_sidra` ou `explicar_tabela_sidra`.",
      "code": null
    }
  ]
}
```

### Example: `validar_consulta_sidra` (invalid variable)

```python
validar_consulta_sidra(
    agregado_id="6579",
    variaveis="99999",
    localidades="N6[3550308]",
    periodos="2024",
)
```

```json
{
  "ok": false,
  "data": {
    "valido": false,
    "agregado_id": "6579",
    "variaveis_validas": [],
    "variaveis_invalidas": ["99999"],
    "niveis_territoriais": ["N6"],
    "niveis_invalidos": [],
    "classificacao_valida": null,
    "erros": [
      "Nenhuma das variáveis \"99999\" existe no agregado \"6579\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis."
    ],
    "avisos": []
  },
  "errors": [
    {
      "message": "Nenhuma das variáveis \"99999\" existe no agregado \"6579\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis.",
      "code": null
    }
  ]
}
```

`executar_consulta_sidra_validada` would return the same `errors` here and
make **no additional request** — it only calls `consultar_agregado` when
`data.valido` is `true`.

---

## Perfil Municipal & Comparação

Two higher-level tools combine Localidades + Agregados/SIDRA into a single
call:

- **`gerar_perfil_municipal(nome, uf)`** — basic municipality profile
  (identification + estimated population). See
  [Municipal Profile example](../examples/municipal-profile.md).
- **`comparar_municipios(municipios, indicadores)`** — compare up to 10
  municipalities on implemented indicators (currently
  `"populacao_estimada"`). See
  [Compare Municipalities example](../examples/compare-municipalities.md).

For the full reference (every parameter, error message and edge case), see
[`packages/mcp_ibge/docs/tools.md`](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_ibge/docs/tools.md).
