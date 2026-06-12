# Example: Education Activity

Build a teaching activity (e.g. for a middle/high school Geography class)
that combines identification, population and map data for three
municipalities — São Paulo (SP), Rio de Janeiro (RJ) and Belo Horizonte (MG)
— using only official IBGE data.

## When to use

When the user asks for material for a class, game, quiz or exercise that
involves comparing Brazilian municipalities/state capitals (population,
location, maps), without making up numbers or geometries.

## The prompt

> *I'm preparing a Geography class about the capitals São Paulo, Rio de
> Janeiro and Belo Horizonte. Give me the estimated population of each (with
> the source) and generate a GeoJSON with the outline of the three cities for
> me to show on a map.*

**Variations**:

- *"I want a quiz: for each city, give the name, state, region and
  population — students need to guess which outline on the map corresponds
  to which city."*
- *"Can you give me the bounding box of each of the three cities, so I can
  center the map on each one separately?"*
- *"Add Salvador (BA) to the comparison."* — exercises the
  `gerar_geojson_municipios`/`comparar_municipios` limit, which continues to
  work normally up to 10 municipalities.
- *"I also want the IDEB (education quality index) of each city."* — an
  unimplemented indicator; the agent should say this information is not
  available in this version, without making up values.

## Expected tool calls

1. [`comparar_municipios`](../tools/agregados.md#perfil-municipal-comparacao)
   — gets name, state, region and estimated population for the three
   capitals in a single call:

```python
comparar_municipios(
    municipios=[
        {"nome": "São Paulo", "uf": "SP"},
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Belo Horizonte", "uf": "MG"},
    ],
    indicadores=["populacao_estimada"],
)
```

2. [`gerar_geojson_municipios`](../tools/geospatial.md#27-gerar_geojson_municipios)
   — generates a GeoJSON `FeatureCollection` with the simplified mesh of the
   three municipalities, for the teacher to plot on a map (e.g. geojson.io,
   QGIS, Folium). The IBGE codes (`codigo_ibge`) come from the
   `comparar_municipios` response (`data.municipios[].codigo_ibge`):

```python
gerar_geojson_municipios(codigos_ibge=[3550308, 3304557, 3106200])
```

`3550308` = São Paulo, `3304557` = Rio de Janeiro, `3106200` = Belo
Horizonte.

3. (Optional) [`obter_bbox_municipio`](../tools/geospatial.md#26-obter_bbox_municipio)
   — for each municipality, gets the bounding box, useful for centering the
   map on each city individually (e.g. for a "identify the city by its
   outline" exercise):

```python
obter_bbox_municipio(codigo_ibge=3550308)   # São Paulo
obter_bbox_municipio(codigo_ibge=3304557)   # Rio de Janeiro
obter_bbox_municipio(codigo_ibge=3106200)   # Belo Horizonte
```

!!! note "If the user asks for more municipalities (up to 10)"
    Both `comparar_municipios` and `gerar_geojson_municipios` accept up to 10
    municipalities per call — just add the new municipality/code to the same
    list. Above 10, both return `ok=false` with `"No máximo 10 municípios por
    chamada (recebidos N)."`; the agent should ask the user to shorten the
    list.

!!! note "If the user asks for an unavailable indicator (e.g. IDEB)"
    Don't call `consultar_agregado` guessing at an IDEB aggregate. State that
    this indicator isn't implemented (it will appear in
    `data.indicadores_nao_implementados` if passed to `comparar_municipios`)
    — see [Tools → Agregados/SIDRA](../tools/agregados.md#sidra-query-builder)
    if the user wants to investigate whether this data exists in SIDRA.

## Example response

### 1. `comparar_municipios(...)`

```json
{
  "ok": true,
  "data": {
    "municipios": [
      {
        "codigo_ibge": 3550308,
        "nome": "São Paulo",
        "uf_sigla": "SP",
        "uf_nome": "São Paulo",
        "regiao_nome": "Sudeste",
        "indicadores": [
          {
            "indicador": "populacao_estimada",
            "valor": 11451245.0,
            "unidade": "Pessoas",
            "periodo": "2024",
            "agregado_id": "6579",
            "variavel_id": "9324"
          }
        ]
      },
      {
        "codigo_ibge": 3304557,
        "nome": "Rio de Janeiro",
        "uf_sigla": "RJ",
        "uf_nome": "Rio de Janeiro",
        "regiao_nome": "Sudeste",
        "indicadores": [
          {
            "indicador": "populacao_estimada",
            "valor": 6211423.0,
            "unidade": "Pessoas",
            "periodo": "2024",
            "agregado_id": "6579",
            "variavel_id": "9324"
          }
        ]
      },
      {
        "codigo_ibge": 3106200,
        "nome": "Belo Horizonte",
        "uf_sigla": "MG",
        "uf_nome": "Minas Gerais",
        "regiao_nome": "Sudeste",
        "indicadores": [
          {
            "indicador": "populacao_estimada",
            "valor": 2315560.0,
            "unidade": "Pessoas",
            "periodo": "2024",
            "agregado_id": "6579",
            "variavel_id": "9324"
          }
        ]
      }
    ],
    "municipios_nao_resolvidos": [],
    "indicadores_consultados": ["populacao_estimada"],
    "indicadores_nao_implementados": [],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP/municipios",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3550308",
      "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3304557",
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3106200"
    ],
    "limitacoes": [
      "Esta comparação cobre apenas os indicadores listados em `indicadores_consultados`; indicadores em `indicadores_nao_implementados` são apenas sugestões de nomes, não dados.",
      "O indicador de população usa o agregado SIDRA 6579 (Estimativas de população residente), que pode ser descontinuado ou renomeado pelo IBGE após um novo Censo.",
      "Sem o parâmetro \"ano\", cada município retorna o período mais recente disponível no SIDRA para esse indicador, que pode diferir entre municípios se algum não tiver dados para o período mais recente."
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324",
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

### 2. `gerar_geojson_municipios(codigos_ibge=[3550308, 3304557, 3106200])`

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3550308 },
        "geometry": { "type": "Polygon", "coordinates": [["...simplified geometry for São Paulo..."]] }
      },
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3304557 },
        "geometry": { "type": "Polygon", "coordinates": [["...simplified geometry for Rio de Janeiro..."]] }
      },
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3106200 },
        "geometry": { "type": "Polygon", "coordinates": [["...simplified geometry for Belo Horizonte..."]] }
      }
    ],
    "codigos_nao_resolvidos": []
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3550308",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3550308",
    "params": {
      "codigos_ibge": [3550308, 3304557, 3106200],
      "endpoints": [
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3550308",
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3106200"
      ]
    },
    "territorial_level": "N6",
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [
    {
      "message": "Geometria simplificada (qualidade \"minima\" da malha do IBGE): adequada para visualização em mapas, mas não para análises que exigem precisão geométrica/cartográfica.",
      "code": null
    }
  ],
  "errors": []
}
```

> The geometries above are abbreviated (`"...simplified geometry..."`) for
> this example only. In a real response, `coordinates` contains the full
> list of `[longitude, latitude]` pairs of the simplified mesh.

## Suggested final answer to the user

> **Activity: Southeast capitals**
>
> | City | State | Region | Estimated population (2024) |
> | --- | --- | --- | --- |
> | São Paulo | SP | Sudeste | 11,451,245 |
> | Rio de Janeiro | RJ | Sudeste | 6,211,423 |
> | Belo Horizonte | MG | Sudeste | 2,315,560 |
>
> Attached is a GeoJSON file (`FeatureCollection`) with the simplified
> outline of the three cities, identified by `properties.codigo_ibge`
> (3550308 = São Paulo, 3304557 = Rio de Janeiro, 3106200 = Belo Horizonte).
> You can open this GeoJSON in tools like [geojson.io](https://geojson.io) or
> QGIS to view it on a map.
>
> **Source**: IBGE — Localidades API, Agregados/SIDRA (aggregate 6579 —
> Population Estimates, period 2024) and Malhas API.
>
> **Limitations**: the population is an estimate (not the Census); the
> outlines are **simplified** geometries, suitable for visualization but not
> for precise area/perimeter measurements.

## Example: individual bounding box (optional)

```json
{
  "ok": true,
  "data": {
    "min_longitude": -46.83,
    "min_latitude": -24.01,
    "max_longitude": -46.36,
    "max_latitude": -23.36,
    "bbox": [-46.83, -24.01, -46.36, -23.36]
  },
  "warnings": [
    {
      "message": "Geometria simplificada (qualidade \"minima\" da malha do IBGE): adequada para visualização em mapas, mas não para análises que exigem precisão geométrica/cartográfica.",
      "code": null
    }
  ]
}
```

> Illustrative example for `obter_bbox_municipio(codigo_ibge=3550308)` (São
> Paulo). Repeat for `3304557` (Rio de Janeiro) and `3106200` (Belo
> Horizonte).

## Limitations

- The returned population is an **estimate** (SIDRA aggregate `6579`), not
  the result of the latest Census — explain this difference to students.
- The geometries returned by `gerar_geojson_municipios` and
  `obter_bbox_municipio` are **simplified** (`"minima"` quality): good for
  visualization, but not for precisely measuring area/perimeter.
- `gerar_geojson_municipios` accepts at most 10 municipalities per call.
- A municipality with an invalid IBGE code or no available mesh appears in
  `data.codigos_nao_resolvidos` (in the GeoJSON) or
  `data.municipios_nao_resolvidos` (in the comparison) — don't substitute an
  "approximate" outline or value.
- This version has no education-specific indicators (e.g. enrollment, IDEB)
  — only geographic identification and population.

## Checking the source

- `data.fontes` (from `comparar_municipios`) and `metadata.source_url`/
  `metadata.endpoint` (from `gerar_geojson_municipios` and
  `obter_bbox_municipio`) point to the official IBGE endpoints (Localidades
  API, Agregados/SIDRA, and Malhas API).
- The full mesh of each municipality can be checked at
  `https://servicodados.ibge.gov.br/api/v3/malhas/municipios/<codigo_ibge>?formato=application/vnd.geo+json&qualidade=minima`.
- Always pass on the "simplified geometry" warning to students/teachers — it
  matters for understanding what the generated map does (and does not)
  represent.
