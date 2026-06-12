# Tools esperadas

## 1. Pergunta em linguagem natural

Para "Quais dados existem sobre desmatamento na Amazônia no Portal Brasileiro
de Dados Abertos?":

```python
sugerir_datasets_para_pergunta(
    pergunta="Quais dados existem sobre desmatamento na Amazônia no Portal Brasileiro de Dados Abertos?",
    limite=5,
)
```

A tool extrai palavras-chave (ex.: `["desmatamento", "amazônia", "portal",
"brasileiro", "abertos"]` — sem usar nenhum modelo de linguagem) e busca esses
termos via `package_search`. As palavras-chave usadas ficam em
`metadata.params["keywords"]`.

> O agente **não deve** chamar `buscar_datasets` "adivinhando" os termos de
> busca quando o usuário fez uma pergunta em linguagem natural —
> `sugerir_datasets_para_pergunta` já faz essa extração de forma determinística
> e rastreável.

## 2. Termos de busca diretos

Para "Busque datasets sobre vacinação contra covid-19":

```python
buscar_datasets(query="vacinação covid-19", limite=10)
```

## 3. Detalhar um dataset encontrado

Usando o `id` (ou `name`) de um dataset retornado pelos passos 1 ou 2:

```python
obter_dataset(dataset_id="<id-do-dataset>")
```

## 4. Listar apenas os recursos (arquivos/links) de um dataset

```python
listar_recursos_dataset(dataset_id="<id-do-dataset>")
```

> Se o usuário já pediu `obter_dataset` (que inclui `resources`), não é
> necessário chamar `listar_recursos_dataset` de novo — use
> `data.resources` da resposta de `obter_dataset`.

## 5. Descobrir organizações publicadoras

Para "Quais órgãos publicam dados sobre educação?":

```python
buscar_organizacoes(query="educação", limite=10)
```

Para detalhar uma organização específica encontrada:

```python
obter_organizacao(organization_id="<id-ou-name-da-organizacao>")
```

## Se nenhuma palavra-chave relevante for encontrada

Para "O que tem disponível?", `sugerir_datasets_para_pergunta` retorna
`ok=true`, `data=[]` e um `warning` explicando que nenhuma palavra-chave
relevante foi extraída. O agente deve repassar essa limitação ao usuário e
sugerir que ele especifique um tema (ex.: "educação", "saúde",
"meio-ambiente"), em vez de chamar outra tool "adivinhando" um tema.
