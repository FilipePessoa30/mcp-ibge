# Exemplo de resposta

## 1. Resposta da tool `comparar_municipios(...)`

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

## 2. Resposta da tool `gerar_geojson_municipios(codigos_ibge=[3550308, 3304557, 3106200])`

```json
{
  "ok": true,
  "data": {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3550308 },
        "geometry": { "type": "Polygon", "coordinates": [["...geometria simplificada de São Paulo..."]] }
      },
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3304557 },
        "geometry": { "type": "Polygon", "coordinates": [["...geometria simplificada do Rio de Janeiro..."]] }
      },
      {
        "type": "Feature",
        "properties": { "codigo_ibge": 3106200 },
        "geometry": { "type": "Polygon", "coordinates": [["...geometria simplificada de Belo Horizonte..."]] }
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

> As geometrias acima foram abreviadas (`"...geometria simplificada..."`)
> apenas para este exemplo. Na resposta real, `coordinates` contém a lista
> completa de pares `[longitude, latitude]` da malha simplificada.

## Resposta final do agente ao usuário

> **Atividade: capitais do Sudeste**
>
> | Cidade | UF | Região | População estimada (2024) |
> | --- | --- | --- | --- |
> | São Paulo | SP | Sudeste | 11.451.245 |
> | Rio de Janeiro | RJ | Sudeste | 6.211.423 |
> | Belo Horizonte | MG | Sudeste | 2.315.560 |
>
> Em anexo, um arquivo GeoJSON (`FeatureCollection`) com o contorno
> simplificado das três cidades, identificadas por `properties.codigo_ibge`
> (3550308 = São Paulo, 3304557 = Rio de Janeiro, 3106200 = Belo Horizonte).
> Você pode abrir esse GeoJSON em ferramentas como
> [geojson.io](https://geojson.io) ou QGIS para visualizar no mapa.
>
> **Fonte**: IBGE — API de Localidades, Agregados/SIDRA (agregado 6579 —
> Estimativas de População, período 2024) e API de Malhas.
>
> **Limitações**: a população é uma estimativa (não o Censo); os contornos
> são geometrias **simplificadas**, adequadas para visualização, mas não para
> medir área/perímetro com precisão.

## Exemplo: bounding box individual (opcional)

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

> Exemplo ilustrativo para `obter_bbox_municipio(codigo_ibge=3550308)` (São
> Paulo). Repita para `3304557` (Rio de Janeiro) e `3106200` (Belo Horizonte).

## Como verificar a fonte

- `data.fontes` (de `comparar_municipios`) lista os endpoints de Localidades
  e Agregados/SIDRA usados para identificação e população.
- `metadata.endpoint` (de `gerar_geojson_municipios` e
  `obter_bbox_municipio`) aponta para o endpoint de Malhas do município
  correspondente; a malha completa pode ser conferida em
  `https://servicodados.ibge.gov.br/api/v3/malhas/municipios/<codigo_ibge>?formato=application/vnd.geo+json&qualidade=minima`.
- Sempre inclua o aviso de "geometria simplificada" ao compartilhar o mapa
  com os alunos.
