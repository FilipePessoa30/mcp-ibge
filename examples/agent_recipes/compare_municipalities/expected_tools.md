# Tools esperadas

1. **`comparar_municipios`** — única chamada necessária:

```python
comparar_municipios(
    municipios=[
        {"nome": "Rio de Janeiro", "uf": "RJ"},
        {"nome": "Niterói", "uf": "RJ"},
        {"nome": "Maricá", "uf": "RJ"},
    ],
    indicadores=["populacao_estimada"],
)
```

> `indicadores` é opcional — sem ele, `comparar_municipios` já usa os
> indicadores básicos disponíveis (`["populacao"]`).

## Internamente (não precisa ser chamado de novo pelo agente)

Para cada município, `comparar_municipios` chama internamente:

- `obter_codigo_municipio(nome=..., uf="RJ")` → código IBGE.
- `obter_municipio_por_codigo(codigo_ibge=...)` → nome, UF, região.
- `consultar_populacao_municipio(nome=..., uf="RJ")` → população estimada.

## Se o usuário pedir um indicador não suportado (ex.: "PIB")

O agente **não deve** chamar `consultar_agregado` "adivinhando" um agregado
de PIB sem antes descobrir o agregado correto — veja a receita
[`sidra_query_discovery`](../sidra_query_discovery/).
`comparar_municipios` já sinaliza isso em `data.indicadores_nao_implementados`
com um `warning`; o agente deve repassar essa limitação ao usuário em vez de
estimar um valor de PIB.

## Se o usuário pedir mais de 10 municípios

`comparar_municipios` retorna `ok=false` com o erro
`"No máximo 10 municípios por chamada (recebidos N)."` — o agente deve pedir
ao usuário para reduzir a lista, e não dividir automaticamente em várias
chamadas sem avisar (cada chamada já cobre até 10 municípios).
