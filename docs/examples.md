# Exemplos de uso por agentes / Agent usage examples

Este documento mostra exemplos **reais** (dados verificados contra a API do
IBGE) de como um agente de IA (Claude Desktop, Cursor, etc.) usa as tools do
`mcp-ibge` para responder perguntas em linguagem natural — incluindo a
chamada de tool, o JSON retornado e como o agente transforma esse JSON em uma
resposta final para o usuário.

This document shows **real** (IBGE-verified) examples of how an AI agent
(Claude Desktop, Cursor, etc.) uses `mcp-ibge` tools to answer natural
language questions — including the tool call, the returned JSON, and how the
agent turns that JSON into a final answer for the user.

> **Nota / Note**: os valores de `retrieved_at` abaixo são ilustrativos
> (`"2026-06-10T15:30:00.000000+00:00"`); na prática cada chamada tem seu
> próprio timestamp. Campos `raw` (JSON original da API do IBGE) foram
> omitidos ou truncados por brevidade — eles sempre estão presentes na
> resposta real.
>
> The `retrieved_at` values below are illustrative
> (`"2026-06-10T15:30:00.000000+00:00"`); in practice each call has its own
> timestamp. `raw` fields (the original IBGE API JSON) were omitted or
> truncated for brevity — they are always present in the real response.

## 1. Código IBGE de um município / Municipality IBGE code

**Pergunta (PT)**: "Qual é o código IBGE de Maricá, RJ?"

**Question (EN)**: "What is the IBGE code for Maricá, RJ?"

### Chamada 1 — `obter_codigo_municipio`

```python
obter_codigo_municipio(nome="Maricá", uf="RJ")
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "params": { "uf": "RJ" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": 3302700
}
```

### Chamada 2 (opcional) — confirmar nome normalizado e UF com `obter_municipio_por_codigo`

Para responder com o **nome normalizado** e a **UF** além do código, o agente
faz uma segunda chamada com o código obtido:

```python
obter_municipio_por_codigo(codigo_ibge=3302700)
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700",
    "params": { "municipio_id": 3302700 },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": {
    "id": 3302700,
    "nome": "Maricá",
    "uf_id": 33,
    "uf_sigla": "RJ",
    "uf_nome": "Rio de Janeiro",
    "regiao_nome": "Sudeste",
    "raw": "(omitido aqui — contém o JSON original do IBGE com microrregião, mesorregião e região imediata)"
  }
}
```

### Resposta do agente (PT)

> O código IBGE do município de **Maricá (RJ)** é **3302700**.
>
> - **Nome normalizado**: Maricá
> - **UF**: RJ — Rio de Janeiro (região Sudeste)
> - **Fonte**: IBGE - Instituto Brasileiro de Geografia e Estatística
> - **Endpoint**: `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700`

### Agent's final answer (EN)

> The IBGE code for **Maricá (RJ)** is **3302700**.
>
> - **Normalized name**: Maricá
> - **State (UF)**: RJ — Rio de Janeiro (Southeast region)
> - **Source**: IBGE - Instituto Brasileiro de Geografia e Estatística
> - **Endpoint**: `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3302700`

---

## 2. Municípios de uma UF / Municipalities of a state

**Pergunta (PT)**: "Liste os municípios do estado do Rio de Janeiro."

**Question (EN)**: "List the municipalities of Rio de Janeiro state."

### Chamada — `listar_municipios`

```python
listar_municipios(uf="RJ")
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios",
    "params": { "uf": "RJ" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": 3300100,
      "nome": "Angra dos Reis",
      "uf_id": 33,
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "raw": "(omitido)"
    },
    {
      "id": 3300159,
      "nome": "Aperibé",
      "uf_id": 33,
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "raw": "(omitido)"
    },
    {
      "id": 3300209,
      "nome": "Araruama",
      "uf_id": 33,
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "raw": "(omitido)"
    }
    // ... mais 89 municípios (total: 92)
  ]
}
```

### Resposta do agente (PT)

> O Rio de Janeiro tem **92 municípios**. Alguns deles: Angra dos Reis
> (3300100), Aperibé (3300159), Araruama (3300209), ... (lista completa
> disponível sob pedido).
>
> **Fonte**: IBGE - Instituto Brasileiro de Geografia e Estatística —
> `https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios`.

### Agent's final answer (EN)

> Rio de Janeiro state has **92 municipalities**. A few of them: Angra dos
> Reis (3300100), Aperibé (3300159), Araruama (3300209), ... (full list
> available on request).
>
> **Source**: IBGE - Instituto Brasileiro de Geografia e Estatística —
> `https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios`.

---

## 3. Ambiguidade na busca por nome / Name search ambiguity

**Pergunta (PT)**: "Busque São José."

**Question (EN)**: "Search for São José."

Esta é uma pergunta interessante porque ilustra dois comportamentos
diferentes da busca fuzzy, dependendo de haver ou não uma `uf`:

This question is interesting because it illustrates two different fuzzy
search behaviors, depending on whether a `uf` is given:

### Caso A — sem UF: correspondência exata única / Case A — no UF: single exact match

`"São José"` é, ele mesmo, o nome **exato** de um único município (em Santa
Catarina). Quando há correspondência exata, ela tem prioridade — então a
busca **não** é ambígua neste caso:

```python
buscar_municipio(nome="São José")
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios",
    "params": {},
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "id": 4216602,
      "nome": "São José",
      "uf_id": 42,
      "uf_sigla": "SC",
      "uf_nome": "Santa Catarina",
      "regiao_nome": "Sul",
      "raw": "(omitido)"
    }
  ]
}
```

### Caso B — com UF: várias correspondências por substring / Case B — with UF: multiple substring matches

Se o agente já sabe que o usuário quer um "São José" em **São Paulo** (por
exemplo, porque a conversa mencionou SP), e usa `obter_codigo_municipio` —
que exige um resultado único — a API retorna **erro com a lista de
candidatos**, pois "São José" não é o nome exato de nenhum município de SP
(mas é substring de vários):

```python
obter_codigo_municipio(nome="São José", uf="SP")
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios",
    "params": { "uf": "SP" },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "error": "Encontrados 5 municípios para \"São José\": São José da Bela Vista, São José do Barreiro, São José do Rio Pardo, São José do Rio Preto, São José dos Campos. Refine a busca com \"uf\" ou um nome mais específico."
}
```

O agente também pode chamar `buscar_municipio(nome="São José", uf="SP")`
diretamente, que retorna os mesmos 5 candidatos em `data` (com `ok=true`) e o
mesmo texto em `warnings`, para apresentá-los como opções ao usuário.

The agent can also call `buscar_municipio(nome="São José", uf="SP")`
directly, which returns the same 5 candidates in `data` (with `ok=true`) and
the same text in `warnings`, to present them as options to the user.

### Resposta do agente (PT)

> Encontrei **um** município chamado exatamente "São José": **São José/SC**
> (código 4216602, região Sul).
>
> Se você quis dizer um dos municípios de **São Paulo** que começam com "São
> José", há 5 opções: São José da Bela Vista, São José do Barreiro, São José
> do Rio Pardo, São José do Rio Preto e São José dos Campos. **Qual deles você
> quer dizer?**

### Agent's final answer (EN)

> I found **one** municipality named exactly "São José": **São José, SC**
> (code 4216602, South region).
>
> If you meant one of the municipalities in **São Paulo** starting with "São
> José", there are 5 options: São José da Bela Vista, São José do Barreiro,
> São José do Rio Pardo, São José do Rio Preto and São José dos Campos.
> **Which one did you mean?**

---

## 4. Consulta genérica SIDRA / Generic SIDRA query

**Pergunta (PT)**: "Consulte o agregado 7060 (IPCA), variável 63 (variação
mensal), para o Brasil, no último período disponível."

**Question (EN)**: "Query aggregate 7060 (IPCA), variable 63 (monthly
variation), for Brazil, for the latest available period."

Este é o padrão genérico **agregado X, variável Y, localidades Z, período
P** — válido para qualquer um dos milhares de agregados do SIDRA. Veja
[docs/tools.md](tools.md#como-descobrir-agregado-variável-período-e-localidade)
para o fluxo completo de descoberta (agregado → metadados → variáveis →
períodos → localidades).

This is the generic **aggregate X, variable Y, locations Z, period P**
pattern — valid for any of the thousands of SIDRA aggregates. See
[docs/tools.md](tools.md#como-descobrir-agregado-variável-período-e-localidade)
for the full discovery workflow (aggregate → metadata → variables → periods →
locations).

### Chamada — `consultar_agregado`

```python
consultar_agregado(
    agregado_id="7060",
    variaveis="63",
    localidades="N1[all]",
    periodos="-1",
    classificacao="315[7169]",
)
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63",
    "params": {
      "agregado_id": "7060",
      "variaveis": "63",
      "periodos": "-1",
      "localidades": "N1[all]",
      "classificacao": "315[7169]"
    },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "agregado_id": "7060",
      "variavel_id": "63",
      "localidade_id": "1",
      "localidade_nome": "Brasil",
      "periodo": "202604",
      "valor": 0.67,
      "unidade": "%",
      "raw": {
        "localidade": { "id": "1", "nivel": { "id": "N1", "nome": "Brasil" }, "nome": "Brasil" },
        "serie": { "202604": "0.67" }
      }
    }
  ]
}
```

### Resposta do agente (PT)

> A variação mensal do **IPCA** (índice geral) no **Brasil** em
> **abril/2026** foi de **0,67%**.
>
> - **Indicador**: IPCA - Variação mensal (agregado 7060, variável 63,
>   classificação "Geral, grupo, subgrupo, item e subitem" → "Índice geral")
> - **Unidade territorial**: Brasil
> - **Período**: abril de 2026 (`202604`)
> - **Fonte**: IBGE - Instituto Brasileiro de Geografia e Estatística —
>   `https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63`

### Agent's final answer (EN)

> The **IPCA** monthly variation (general index) in **Brazil** for
> **April/2026** was **0.67%**.
>
> - **Indicator**: IPCA - Monthly variation (aggregate 7060, variable 63,
>   classification "General, group, subgroup, item and subitem" → "General
>   index")
> - **Territorial unit**: Brazil
> - **Period**: April 2026 (`202604`)
> - **Source**: IBGE - Instituto Brasileiro de Geografia e Estatística —
>   `https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63`

---

## 5. Comparação entre municípios / Comparing municipalities

**Pergunta (PT)**: "Compare Rio de Janeiro, Niterói e Maricá usando um
indicador do IBGE."

**Question (EN)**: "Compare Rio de Janeiro, Niterói and Maricá using an IBGE
indicator."

Este caso é o que o **prompt `comparar_municipios`** orienta: resolver os
códigos de cada município (passo 1, ver exemplo 1), localizar um
agregado/variável adequados (passo 2 — para população, usar diretamente
`consultar_populacao_municipio` ou o agregado `6579`/variável `9324`) e
consultar todos no **mesmo período** (passo 3).

This is exactly what the **`comparar_municipios` prompt** guides: resolve
each municipality's code (step 1, see example 1), find a suitable
aggregate/variable (step 2 — for population, use
`consultar_populacao_municipio` directly, or aggregate `6579`/variable
`9324`) and query all of them for the **same period** (step 3).

### Chamada — `consultar_agregado`

```python
consultar_agregado(
    agregado_id="6579",
    variaveis="9324",
    localidades="N6[3304557,3303302,3302700]",  # Rio de Janeiro, Niterói, Maricá
    periodos="-1",
)
```

```json
{
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "params": {
      "agregado_id": "6579",
      "variaveis": "9324",
      "periodos": "-1",
      "localidades": "N6[3304557,3303302,3302700]"
    },
    "retrieved_at": "2026-06-10T15:30:00.000000+00:00",
    "license_note": null
  },
  "data": [
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3304557",
      "localidade_nome": "Rio de Janeiro (RJ)",
      "periodo": "2025",
      "valor": 6730729.0,
      "unidade": "Pessoas",
      "raw": "(omitido)"
    },
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3303302",
      "localidade_nome": "Niterói (RJ)",
      "periodo": "2025",
      "valor": 516787.0,
      "unidade": "Pessoas",
      "raw": "(omitido)"
    },
    {
      "agregado_id": "6579",
      "variavel_id": "9324",
      "localidade_id": "3302700",
      "localidade_nome": "Maricá (RJ)",
      "periodo": "2025",
      "valor": 212470.0,
      "unidade": "Pessoas",
      "raw": "(omitido)"
    }
  ]
}
```

### Resposta do agente (PT)

> Comparando a **população residente estimada (2025)**:
>
> | Município | População (2025) |
> | --- | --- |
> | Rio de Janeiro (RJ) | 6.730.729 |
> | Niterói (RJ) | 516.787 |
> | Maricá (RJ) | 212.470 |
>
> O Rio de Janeiro tem cerca de **13×** a população de Niterói e **32×** a de
> Maricá.
>
> - **Indicador**: população residente estimada (agregado SIDRA `6579`,
>   variável `9324`)
> - **Período**: 2025 (estimativa, não é o Censo)
> - **Fonte**: IBGE - Instituto Brasileiro de Geografia e Estatística —
>   `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324`
> - **Limitação**: são estimativas anuais, não os resultados do Censo mais
>   recente; para dados censitários use os agregados específicos do Censo.

### Agent's final answer (EN)

> Comparing **estimated resident population (2025)**:
>
> | Municipality | Population (2025) |
> | --- | --- |
> | Rio de Janeiro (RJ) | 6,730,729 |
> | Niterói (RJ) | 516,787 |
> | Maricá (RJ) | 212,470 |
>
> Rio de Janeiro has roughly **13×** the population of Niterói and **32×**
> that of Maricá.
>
> - **Indicator**: estimated resident population (SIDRA aggregate `6579`,
>   variable `9324`)
> - **Period**: 2025 (estimate, not the Census)
> - **Source**: IBGE - Instituto Brasileiro de Geografia e Estatística —
>   `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324`
> - **Limitation**: these are annual estimates, not the latest Census
>   results; for Census data use the dedicated Census aggregates.

---

## 6. Uso educacional / Educational use

**Pergunta (PT)**: "Monte uma atividade para alunos comparando população de
municípios do RJ."

**Question (EN)**: "Put together a classroom activity comparing the
population of RJ municipalities."

### Como o agente orquestra as tools / How the agent orchestrates the tools

1. `listar_municipios(uf="RJ")` (exemplo 2) — para o professor escolher (ou o
   agente sugerir) alguns municípios do RJ.
2. `consultar_agregado(agregado_id="6579", variaveis="9324",
   localidades="N6[<códigos>]", periodos="-1")` (exemplo 5) — população
   estimada mais recente dos municípios escolhidos.
3. Montar a atividade usando a tabela de resultados, com perguntas que
   incentivem os alunos a interpretar os dados e consultar a fonte original.

1. `listar_municipios(uf="RJ")` (example 2) — so the teacher can pick (or the
   agent can suggest) a few RJ municipalities.
2. `consultar_agregado(agregado_id="6579", variaveis="9324",
   localidades="N6[<codes>]", periodos="-1")` (example 5) — latest estimated
   population of the chosen municipalities.
3. Build the activity around the results table, with questions that encourage
   students to interpret the data and check the original source.

### Resposta do agente (PT)

> **Atividade: comparando a população de municípios do Rio de Janeiro**
>
> Usando a tabela abaixo (fonte: IBGE, estimativas de população residente
> 2025, agregado SIDRA `6579`):
>
> | Município | População (2025) |
> | --- | --- |
> | Rio de Janeiro (RJ) | 6.730.729 |
> | Niterói (RJ) | 516.787 |
> | Maricá (RJ) | 212.470 |
>
> 1. Calcule quantas vezes a população do Rio de Janeiro é maior que a de
>    Niterói e a de Maricá.
> 2. Pesquise (em `https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios`)
>    mais 2 municípios do RJ e compare suas populações com as da tabela.
> 3. Discuta: por que "estimativa de população" pode ser diferente do
>    resultado do último Censo?
>
> **Fonte de todos os dados**: IBGE - Instituto Brasileiro de Geografia e
> Estatística, agregado SIDRA `6579` (estimativas de população residente),
> ano de referência 2025.

### Agent's final answer (EN)

> **Activity: comparing the population of Rio de Janeiro municipalities**
>
> Using the table below (source: IBGE, 2025 resident population estimates,
> SIDRA aggregate `6579`):
>
> | Municipality | Population (2025) |
> | --- | --- |
> | Rio de Janeiro (RJ) | 6,730,729 |
> | Niterói (RJ) | 516,787 |
> | Maricá (RJ) | 212,470 |
>
> 1. Calculate how many times larger Rio de Janeiro's population is compared
>    to Niterói's and Maricá's.
> 2. Look up (at `https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios`)
>    2 more RJ municipalities and compare their populations with the table.
> 3. Discuss: why might a "population estimate" differ from the latest Census
>    result?
>
> **Source for all data**: IBGE - Instituto Brasileiro de Geografia e
> Estatística, SIDRA aggregate `6579` (resident population estimates),
> reference year 2025.

---

## 7. Uso em políticas públicas / Public policy use

**Pergunta (PT)**: "Liste municípios de uma UF para montar um pipeline de
indicadores sociais."

**Question (EN)**: "List the municipalities of a state to build a social
indicators pipeline."

### Como o agente orquestra as tools / How the agent orchestrates the tools

1. `listar_municipios(uf="RJ")` (exemplo 2) — obtém os 92 códigos IBGE de 7
   dígitos dos municípios do RJ, prontos para usar como `localidades` em
   `consultar_agregado` (ex.: `N6[3300100,3300159,...]`, em lotes se a lista
   for muito longa).
2. Para cada indicador desejado (ex.: população, PIB per capita,
   escolarização), seguir o
   [fluxo de descoberta](tools.md#como-descobrir-agregado-variável-período-e-localidade):
   `listar_agregados` → `obter_metadados_agregado` →
   `listar_variaveis_agregado` → `listar_periodos_agregado` →
   `consultar_agregado`.
3. Combinar os resultados de várias chamadas de `consultar_agregado` (uma por
   indicador/período) por `localidade_id`, preservando `metadata` (fonte,
   endpoint, parâmetros, `retrieved_at`) de cada chamada para auditoria.

1. `listar_municipios(uf="RJ")` (example 2) — get the 92 7-digit IBGE codes
   for RJ municipalities, ready to use as `localidades` in
   `consultar_agregado` (e.g. `N6[3300100,3300159,...]`, in batches if the
   list is too long).
2. For each desired indicator (e.g. population, GDP per capita, school
   enrollment), follow the
   [discovery workflow](tools.md#como-descobrir-agregado-variável-período-e-localidade):
   `listar_agregados` → `obter_metadados_agregado` →
   `listar_variaveis_agregado` → `listar_periodos_agregado` →
   `consultar_agregado`.
3. Combine the results of multiple `consultar_agregado` calls (one per
   indicator/period) by `localidade_id`, keeping each call's `metadata`
   (source, endpoint, params, `retrieved_at`) for auditing.

### Resposta do agente (PT)

> Para montar o pipeline:
>
> 1. **Lista de municípios e códigos** — obtida com `listar_municipios(uf="RJ")`
>    (92 municípios, fonte:
>    `https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios`).
>    Use o campo `id` de cada item como código IBGE de 7 dígitos.
> 2. **Para cada indicador social** (ex.: população residente estimada =
>    agregado `6579`/variável `9324`), chame `consultar_agregado` com
>    `localidades="N6[<códigos>]"` e o `periodo` desejado.
> 3. **Audite cada lote**: cada resposta traz `metadata.endpoint`,
>    `metadata.params` e `metadata.retrieved_at` — registre-os junto com os
>    dados para rastreabilidade.
>
> **Limitações a documentar no pipeline**: valores `null` indicam dado
> ausente/sigiloso no SIDRA (marcadores `"-"`, `".."`, `"..."`, `"X"`); o
> indicador `consultar_populacao_municipio` é experimental e depende de um
> agregado/variável fixos que o IBGE pode descontinuar após um novo Censo —
> prefira `consultar_agregado` com IDs confirmados via
> `obter_metadados_agregado`.

### Agent's final answer (EN)

> To build the pipeline:
>
> 1. **List of municipalities and codes** — obtained via
>    `listar_municipios(uf="RJ")` (92 municipalities, source:
>    `https://servicodados.ibge.gov.br/api/v1/localidades/estados/RJ/municipios`).
>    Use each item's `id` field as the 7-digit IBGE code.
> 2. **For each social indicator** (e.g. estimated resident population =
>    aggregate `6579`/variable `9324`), call `consultar_agregado` with
>    `localidades="N6[<codes>]"` and the desired `periodo`.
> 3. **Audit each batch**: every response includes `metadata.endpoint`,
>    `metadata.params` and `metadata.retrieved_at` — log these alongside the
>    data for traceability.
>
> **Limitations to document in the pipeline**: `null` values indicate
> missing/confidential data in SIDRA (markers `"-"`, `".."`, `"..."`, `"X"`);
> the `consultar_populacao_municipio` indicator is experimental and depends
> on a fixed aggregate/variable that the IBGE may discontinue after a new
> Census — prefer `consultar_agregado` with IDs confirmed via
> `obter_metadados_agregado`.

---

## Ver também / See also

- [docs/tools.md](tools.md) — referência completa de todas as tools / full
  tools reference.
- [docs/tools.md — Como descobrir agregado, variável, período e
  localidade](tools.md#como-descobrir-agregado-variável-período-e-localidade)
  — discovery workflow for SIDRA aggregates.
- [docs/data_sources.md](data_sources.md) — formato do envelope de resposta /
  response envelope format.
- [examples/queries.md](../examples/queries.md) — exemplos de chamadas MCP
  brutas (JSON) / raw MCP call examples (JSON).
