# Tools esperadas

1. **`comparar_municipios`** — identificação + população das três capitais:

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

2. **`gerar_geojson_municipios`** — contorno dos três municípios para o mapa.
   Os códigos IBGE (`codigo_ibge`) vêm da resposta de `comparar_municipios`
   (`data.municipios[].codigo_ibge`):

```python
gerar_geojson_municipios(codigos_ibge=[3550308, 3304557, 3106200])
```

> `3550308` = São Paulo, `3304557` = Rio de Janeiro, `3106200` = Belo
> Horizonte.

## Opcional: bounding box individual por cidade

Se o usuário pedir para centralizar o mapa em cada cidade separadamente:

```python
obter_bbox_municipio(codigo_ibge=3550308)   # São Paulo
obter_bbox_municipio(codigo_ibge=3304557)   # Rio de Janeiro
obter_bbox_municipio(codigo_ibge=3106200)   # Belo Horizonte
```

## Internamente (não precisa ser chamado de novo pelo agente)

`comparar_municipios` já chama `obter_codigo_municipio`,
`obter_municipio_por_codigo` e `consultar_populacao_municipio` para cada
município — não repita essas chamadas manualmente.

## Se o usuário pedir mais municípios (até 10)

Tanto `comparar_municipios` quanto `gerar_geojson_municipios` aceitam até 10
municípios por chamada — basta adicionar o novo município/código à mesma
lista. Acima de 10, ambas retornam `ok=false` com
`"No máximo 10 municípios por chamada (recebidos N)."`; o agente deve pedir
para reduzir a lista.

## Se o usuário pedir um indicador não disponível (ex.: "IDEB")

Não chame `consultar_agregado` adivinhando um agregado de IDEB. Informe que
esse indicador não está implementado (vai aparecer em
`data.indicadores_nao_implementados` se for passado a `comparar_municipios`)
— veja a receita [`sidra_query_discovery`](../sidra_query_discovery/) caso o
usuário queira investigar se esse dado existe no SIDRA.
