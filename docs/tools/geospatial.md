# Tools: Geospatial

Tools in this section query the
[IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas) and
return `data` as a valid [GeoJSON](https://geojson.org/) object (RFC 7946) —
a `FeatureCollection`, `Feature`, or a geometry directly.

!!! warning "New / experimental"
    These tools are new in v0.2.0 and considered an **experimental preview**
    — see [Module: mcp-ibge](../modules/ibge.md) and [Roadmap](../roadmap.md).

> 🇧🇷 **Nota**: os parâmetros (`codigo_ibge`, `uf`, `simplificado`,
> `codigos_ibge`) e as mensagens de erro/aviso permanecem em português.

## Mesh quality: `simplificado`

Each mesh can be requested in two qualities:

- **`simplificado=true` (default)** — `"minima"` quality mesh. Much smaller
  response, suitable for map visualization. The response always includes a
  warning that the geometry has been simplified.
- **`simplificado=false`** — `"maxima"` quality. More detailed geometry,
  which can be much larger and, for large municipalities/states, may exceed
  the [response size limit](#common-errors)
  (`Settings.max_response_size_bytes`, 5 MB by default), returning a server
  error in that case.

## Common errors

In addition to the per-tool errors below, every tool in this module can
return:

| Situation | Error message |
| --- | --- |
| Network/timeout failure calling the IBGE API | `Falha ao conectar à API do IBGE: <detail>` / `Timeout ao consultar a API do IBGE.` |
| IBGE API returns HTTP 4xx/5xx | `IBGE retornou HTTP <status> para <url>` |
| Response exceeds the size limit (relevant with `simplificado=false`) | `Resposta da API do IBGE excede o limite de tamanho permitido.` |

## 24. `obter_malha_municipio`

Return the geographic mesh (GeoJSON) of a municipality, by IBGE code.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `codigo_ibge` | `integer` | yes | — | 7-digit IBGE municipality code (e.g. `3304557`). |
| `simplificado` | `boolean` | no | `true` | If `true`, returns the simplified mesh (`"minima"` quality); if `false`, the more detailed mesh (`"maxima"` quality). |

```python
obter_malha_municipio(codigo_ibge=3303302)
```

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codarea": "3303302" },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-43.13, -22.92], [-43.13, -22.86], [-43.05, -22.86], [-43.05, -22.92], [-43.13, -22.92]]]
        }
      }
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "params": { "codigo_ibge": 3303302, "qualidade": "minima" },
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

The geometry above is simplified for illustration; real responses contain
many more coordinate pairs.

**Possible warnings**:

- `Geometria simplificada (qualidade "minima" da malha do IBGE): ...` —
  emitted whenever `simplificado=true` (the default).

**Errors**:

| Situation | Error message |
| --- | --- |
| `codigo_ibge` doesn't have 7 digits | `Código de município inválido: "<valor>". Deve ser o código IBGE de 7 dígitos (ex.: 3550308).` |
| API doesn't return a valid GeoJSON for the given code | `A malha do município <codigo_ibge> não retornou um GeoJSON válido.` |

**Source**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/municipios/{id}?formato=application/vnd.geo+json&qualidade=...`.

---

## 25. `obter_malha_uf`

Return the geographic mesh (GeoJSON) of a state.

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `uf` | `string` | yes | — | State abbreviation (e.g. `"RJ"`) or IBGE state code (e.g. `"33"`). |
| `simplificado` | `boolean` | no | `true` | If `true`, returns the simplified mesh (`"minima"` quality); if `false`, the more detailed mesh (`"maxima"` quality). |

```python
obter_malha_uf(uf="RJ")
```

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codarea": "33" },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-44.9, -23.4], [-44.9, -20.8], [-40.9, -20.8], [-40.9, -23.4], [-44.9, -23.4]]]
        }
      }
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/RJ",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/estados/RJ",
    "params": { "uf": "RJ", "qualidade": "minima" },
    "territorial_level": "N3",
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

**Possible warnings**: the same simplified-geometry warning as
[`obter_malha_municipio`](#24-obter_malha_municipio), emitted whenever
`simplificado=true` (the default).

**Errors**:

| Situation | Error message |
| --- | --- |
| `uf` doesn't match any valid abbreviation/code | `UF inválida: "XX". Use a sigla (ex.: "RJ") ou o código IBGE (ex.: "33").` |
| API doesn't return a valid GeoJSON for the given state | `A malha da UF "<uf>" não retornou um GeoJSON válido.` |

**Source**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/estados/{uf}?formato=application/vnd.geo+json&qualidade=...`.

---

## 26. `obter_bbox_municipio`

Return the bounding box of a municipality in WGS84 coordinates (decimal
degrees), computed locally from the municipality's simplified
(`"minima"`-quality) mesh. Useful for centering or framing a map without
processing the full geometry.

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `codigo_ibge` | `integer` | yes | 7-digit IBGE municipality code (e.g. `3304557`). |

```python
obter_bbox_municipio(codigo_ibge=3303302)
```

```json
{
  "ok": true,
  "data": {
    "min_longitude": -43.13,
    "min_latitude": -22.92,
    "max_longitude": -43.05,
    "max_latitude": -22.86,
    "bbox": [-43.13, -22.92, -43.05, -22.86]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302",
    "params": { "codigo_ibge": 3303302, "qualidade": "minima" },
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

`bbox` follows GeoJSON's `[west, south, east, north]` format (the `bbox`
field of a `FeatureCollection`/`Feature`), while `min_longitude`,
`min_latitude`, `max_longitude` and `max_latitude` repeat the same values by
name.

**Possible warnings**:

- The same simplified-geometry warning as
  [`obter_malha_municipio`](#24-obter_malha_municipio) — always present,
  since the bounding box is computed from the simplified mesh.

**Errors**:

| Situation | Error message |
| --- | --- |
| `codigo_ibge` doesn't have 7 digits | `Código de município inválido: "<valor>". Deve ser o código IBGE de 7 dígitos (ex.: 3550308).` |
| The returned mesh contains no valid geometry | `Não foi possível calcular o bounding box do município <codigo_ibge>: a malha retornada não contém geometria válida.` |

**Source**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/municipios/{id}?formato=application/vnd.geo+json&qualidade=minima`
(bounding box computed locally from the returned geometry).

---

## 27. `gerar_geojson_municipios`

Combine the simplified mesh of up to `MAX_MUNICIPIOS_GEOJSON = 10`
municipalities into a single GeoJSON `FeatureCollection`, with one `Feature`
per municipality (`properties.codigo_ibge` + the simplified mesh geometry).
Useful for building a multi-municipality map in a single call.

IBGE codes that don't return a valid mesh do not stop the generation — they
appear in `data.codigos_nao_resolvidos`, with the `motivo` (reason).

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `codigos_ibge` | `list[integer]` | yes | 7-digit IBGE municipality codes (1 to 10), e.g. `[3304557, 3303302]`. |

```python
gerar_geojson_municipios(codigos_ibge=[3304557, 3303302])
```

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3304557 },
        "geometry": { "type": "Polygon", "coordinates": [[["...", "..."]]] }
      },
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3303302 },
        "geometry": {
          "type": "Polygon",
          "coordinates": [[[-43.13, -22.92], [-43.13, -22.86], [-43.05, -22.86], [-43.05, -22.92], [-43.13, -22.92]]]
        }
      }
    ],
    "codigos_nao_resolvidos": []
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
    "params": {
      "codigos_ibge": [3304557, 3303302],
      "endpoints": [
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3304557",
        "https://servicodados.ibge.gov.br/api/v3/malhas/municipios/3303302"
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

`codigos_nao_resolvidos` is an additional GeoJSON member (a "foreign member",
allowed by RFC 7946) listing `{"codigo_ibge", "motivo"}` for codes that did
not return a valid mesh.

**Possible warnings**:

- The simplified-geometry warning from
  [`obter_malha_municipio`](#24-obter_malha_municipio) — always present,
  since this tool always uses the simplified (`"minima"`-quality) mesh to
  keep the combined response size under control.
- `Códigos IBGE sem malha válida (ver data.codigos_nao_resolvidos): <códigos>`
  — emitted when at least one code doesn't return a valid mesh, but at least
  one other code is resolved.

**Errors**:

| Situation | Error message |
| --- | --- |
| `codigos_ibge` empty | `Informe ao menos um código IBGE em "codigos_ibge".` |
| `codigos_ibge` with more than `MAX_MUNICIPIOS_GEOJSON` items | `No máximo 10 municípios por chamada (recebidos N).` |
| None of the given codes could be resolved | `Nenhum dos códigos IBGE informados pôde ser resolvido.` |
| `codigos_ibge` contains a code that doesn't have 7 digits | `Código de município inválido: "<valor>". Deve ser o código IBGE de 7 dígitos (ex.: 3550308).` |

**Source**: [IBGE API de Malhas](https://servicodados.ibge.gov.br/api/docs/malhas)
— `GET /malhas/municipios/{id}?formato=application/vnd.geo+json&qualidade=minima`
for each given municipality.

---

For the full reference, see
[`packages/mcp_ibge/docs/tools.md`](https://github.com/FilipePessoa30/mcp-ibge/blob/main/packages/mcp_ibge/docs/tools.md#geoespacial).
