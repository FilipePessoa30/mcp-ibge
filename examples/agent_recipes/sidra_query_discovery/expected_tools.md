# Tools esperadas

Ordem recomendada (fluxo de descoberta completo):

1. **`buscar_tabelas_sidra`** — encontrar o agregado do IPCA:

```python
buscar_tabelas_sidra(tema="IPCA inflação variação mensal")
```

> Da resposta, identifique `agregado_id="7060"` ("IPCA - Variação mensal").

2. **`explicar_tabela_sidra`** — confirmar período, níveis territoriais e
   classificações disponíveis:

```python
explicar_tabela_sidra(agregado_id="7060")
```

3. **`listar_variaveis_tabela_sidra`** — identificar a variável:

```python
listar_variaveis_tabela_sidra(agregado_id="7060")
```

> Identifique `variaveis="63"` ("IPCA - Variação mensal", unidade `%`).

4. **`listar_classificacoes_tabela_sidra`** — identificar a classificação
   "Índice geral" (para não misturar com grupos/subitens específicos):

```python
listar_classificacoes_tabela_sidra(agregado_id="7060")
```

> Identifique `classificacao="315[7169]"` ("Geral, grupo, subgrupo, item e
> subitem" → categoria "Índice geral").

5. **`validar_consulta_sidra`** — validar a combinação antes de executar:

```python
validar_consulta_sidra(
    agregado_id="7060",
    variaveis="63",
    localidades="N1[all]",
    periodos="-1",
    classificacao="315[7169]",
)
```

6. **`executar_consulta_sidra_validada`** — só executa se `data.valido=true`
   no passo anterior:

```python
executar_consulta_sidra_validada(
    agregado_id="7060",
    variaveis="63",
    localidades="N1[all]",
    periodos="-1",
    classificacao="315[7169]",
)
```

## Passo opcional: `sugerir_consulta_sidra`

Pode ser usado **antes** do passo 1, como ponto de partida, para perguntas em
linguagem natural:

```python
sugerir_consulta_sidra(pergunta="qual foi a variação mensal do IPCA no Brasil no último mês?")
```

A sugestão retornada **ainda deve passar por `validar_consulta_sidra`**
(passo 5) antes de ser executada — o próprio retorno inclui o aviso de que é
uma heurística sem LLM.

## Se a validação falhar (`data.valido=false`)

Não chame `executar_consulta_sidra_validada` esperando que ele "tente mesmo
assim" — ele também retorna `ok=false` e `data=[]` sem fazer requisições de
dados. Em vez disso:

- Releia `data.erros`/`errors` para entender o que está errado (variável,
  nível territorial ou classificação inexistente).
- Volte a `listar_variaveis_tabela_sidra`/`listar_classificacoes_tabela_sidra`
  para escolher um ID válido, e revalide.

## Quando NÃO usar esta receita

- Para população de municípios: use
  [`gerar_perfil_municipal`](../municipal_profile/) ou
  [`compare_municipalities`](../compare_municipalities/) — já encapsulam o
  agregado/variável corretos (`6579`/`9324`).
- Se o usuário já souber `agregado_id`, `variaveis`, `localidades` e
  `periodos` corretos (ex.: de uma consulta anterior já validada), pode-se
  chamar `executar_consulta_sidra_validada` diretamente — a validação roda de
  qualquer forma, então não há necessidade de repetir os passos 1-4 a cada
  consulta.
