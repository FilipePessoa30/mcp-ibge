# Receita: Atividade Didática (`education_activity`)

## Objetivo

Criar uma atividade didática (ex.: para uma aula de Geografia do ensino
fundamental/médio) que combine dados de identificação, população e mapas de
três municípios — São Paulo (SP), Rio de Janeiro (RJ) e Belo Horizonte (MG) —
usando apenas dados oficiais do IBGE.

## Quando usar

Quando o usuário pede material para uma aula, gincana, quiz ou exercício que
envolva comparar municípios/capitais brasileiras (população, localização,
mapas), sem inventar números ou geometrias.

## Fluxo

1. [`comparar_municipios`](../../../packages/mcp_ibge/docs/tools.md#23-comparar_municipios)
   — obtém nome, UF, região e população estimada das três capitais em uma
   única chamada.
2. [`gerar_geojson_municipios`](../../../packages/mcp_ibge/docs/tools.md#27-gerar_geojson_municipios)
   — gera uma `FeatureCollection` GeoJSON com a malha simplificada dos três
   municípios, para o professor plotar em um mapa (ex.: geojson.io,
   QGIS, Folium).
3. (Opcional) [`obter_bbox_municipio`](../../../packages/mcp_ibge/docs/tools.md#26-obter_bbox_municipio)
   — para cada município, obtém a caixa delimitadora (bounding box), útil
   para centralizar o mapa em cada cidade individualmente (ex.: em um
   exercício "identifique a cidade pelo contorno").

Veja [`prompt.md`](prompt.md), [`expected_tools.md`](expected_tools.md) e
[`example_output.md`](example_output.md).

## Limitações

- A população retornada é uma **estimativa** (agregado SIDRA `6579`), não o
  resultado do último Censo — explique essa diferença para os alunos.
- As geometrias retornadas por `gerar_geojson_municipios` e
  `obter_bbox_municipio` são **simplificadas** (qualidade `"minima"`): boas
  para visualização, mas não para medir área/perímetro com precisão.
- `gerar_geojson_municipios` aceita no máximo 10 municípios por chamada.
- Município com código IBGE inválido ou sem malha disponível aparece em
  `data.codigos_nao_resolvidos` (no GeoJSON) ou em
  `data.municipios_nao_resolvidos` (na comparação) — não use um contorno ou
  valor "aproximado" no lugar.
- Não há, nesta versão, indicadores educacionais (ex.: matrículas, IDEB) —
  apenas identificação geográfica e população.

## Como verificar a fonte

- `data.fontes` (de `comparar_municipios`) e `metadata.source_url`/
  `metadata.endpoint` (de `gerar_geojson_municipios` e
  `obter_bbox_municipio`) apontam para os endpoints oficiais do IBGE
  (API de Localidades, Agregados/SIDRA e Malhas).
- A malha completa de cada município pode ser conferida em
  `https://servicodados.ibge.gov.br/api/v3/malhas/municipios/<codigo_ibge>?formato=application/vnd.geo+json&qualidade=minima`.
- Sempre repasse aos alunos/professor o aviso de "geometria simplificada" —
  é importante para entender o que o mapa gerado representa (e não
  representa).
