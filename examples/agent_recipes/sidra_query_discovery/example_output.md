# Exemplo de resposta

## 1. `buscar_tabelas_sidra(tema="IPCA inflação variação mensal")`

```json
{
  "ok": true,
  "data": [
    { "id": "7060", "nome": "IPCA - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços", "pontuacao": 2 },
    { "id": "1419", "nome": "IPCA - Série histórica com número-índice, variação mensal e variações acumuladas em 3 meses, em 6 meses, no ano e em 12 meses (a partir de janeiro/1991)", "pontuacao": 2 }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados",
    "params": { "tema": "IPCA inflação variação mensal", "limite": 10 },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> Escolhido `agregado_id="7060"` (IPCA - Variação mensal...) por ser a tabela
> "atual" do IPCA (a `1419` é uma série histórica mais ampla, mas com a mesma
> variável de variação mensal).

## 2. `explicar_tabela_sidra(agregado_id="7060")`

```json
{
  "ok": true,
  "data": {
    "id": "7060",
    "nome": "IPCA - Variação mensal, acumulada no ano, acumulada em 12 meses e peso mensal, para o índice geral, grupos, subgrupos, itens e subitens de produtos e serviços",
    "pesquisa": "Índice Nacional de Preços ao Consumidor Amplo",
    "assunto": "Índices de preços ao consumidor",
    "periodicidade": { "frequencia": "mensal", "inicio": 202001, "fim": 202505 },
    "niveis_territoriais": ["N1", "N7"],
    "variaveis": [
      { "id": "63", "nome": "IPCA - Variação mensal", "unidade": "%" },
      { "id": "2265", "nome": "IPCA - Variação acumulada no ano", "unidade": "%" },
      { "id": "69", "nome": "IPCA - Variação acumulada em 12 meses", "unidade": "%" },
      { "id": "66", "nome": "IPCA - Peso mensal", "unidade": "%" }
    ],
    "classificacoes": [
      {
        "id": "315",
        "nome": "Geral, grupo, subgrupo, item e subitem",
        "categorias": [
          { "id": "7169", "nome": "Índice geral" },
          { "id": "7170", "nome": "1.Alimentação e bebidas" }
        ]
      }
    ],
    "limitacoes": [
      "Dados disponíveis de 202001 a 202505 (mensal).",
      "Níveis territoriais disponíveis: N1, N7.",
      "Esta tabela possui classificações adicionais: 315 (Geral, grupo, subgrupo, item e subitem)."
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "params": { "agregado_id": "7060" },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> O agregado real possui muito mais categorias na classificação `315` (grupos,
> subgrupos, itens, subitens) — apenas as relevantes para este exemplo foram
> incluídas. `N7` = "Região metropolitana" — note que `N1[all]` (Brasil) está
> disponível, mas `N3` (estados) e `N6` (municípios) **não** estão.

## 3. `listar_variaveis_tabela_sidra(agregado_id="7060")`

```json
{
  "ok": true,
  "data": [
    { "id": "63", "nome": "IPCA - Variação mensal", "unidade": "%" },
    { "id": "2265", "nome": "IPCA - Variação acumulada no ano", "unidade": "%" },
    { "id": "69", "nome": "IPCA - Variação acumulada em 12 meses", "unidade": "%" },
    { "id": "66", "nome": "IPCA - Peso mensal", "unidade": "%" }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "params": { "agregado_id": "7060" },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> Escolhida `variaveis="63"` ("IPCA - Variação mensal", `%`) — é a que
> corresponde diretamente à pergunta do usuário.

## 4. `listar_classificacoes_tabela_sidra(agregado_id="7060")`

```json
{
  "ok": true,
  "data": [
    {
      "id": "315",
      "nome": "Geral, grupo, subgrupo, item e subitem",
      "categorias": [
        { "id": "7169", "nome": "Índice geral" },
        { "id": "7170", "nome": "1.Alimentação e bebidas" }
      ]
    }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "params": { "agregado_id": "7060" },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> Escolhida `classificacao="315[7169]"` ("Índice geral") — sem isso, a
> consulta retornaria a variação para **todos** os grupos/subgrupos/itens,
> não apenas o índice geral.

## 5. `validar_consulta_sidra(agregado_id="7060", variaveis="63", localidades="N1[all]", periodos="-1", classificacao="315[7169]")`

```json
{
  "ok": true,
  "data": {
    "valido": true,
    "agregado_id": "7060",
    "variaveis_validas": ["63"],
    "variaveis_invalidas": [],
    "niveis_territoriais": ["N1"],
    "niveis_invalidos": [],
    "classificacao_valida": "315[7169]",
    "erros": [],
    "avisos": []
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/metadados",
    "params": {
      "agregado_id": "7060",
      "variaveis": "63",
      "localidades": "N1[all]",
      "periodos": "-1",
      "classificacao": "315[7169]"
    },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

## 6. `executar_consulta_sidra_validada(agregado_id="7060", variaveis="63", localidades="N1[all]", periodos="-1", classificacao="315[7169]")`

```json
{
  "ok": true,
  "data": [
    {
      "agregado_id": "7060",
      "variavel_id": "63",
      "localidade_id": "1",
      "localidade_nome": "Brasil",
      "periodo": "202505",
      "valor": 0.26,
      "unidade": "%",
      "raw": { "...": "..." }
    }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63",
    "endpoint": "https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63",
    "params": {
      "agregado_id": "7060",
      "variaveis": "63",
      "localidades": "N1[all]",
      "periodos": "-1",
      "classificacao": "315[7169]"
    },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "license_note": null
  },
  "warnings": [],
  "errors": []
}
```

> O valor `0.26` (%) para o período `"202505"` é ilustrativo. Execute a tool
> para obter o valor atual e o período mais recente disponível.

## Resposta final do agente ao usuário

> A variação mensal do IPCA no Brasil em maio/2025 (período `202505`, o mais
> recente disponível) foi de **0,26%** (Índice geral).
>
> **Como cheguei nesse número**:
> 1. `buscar_tabelas_sidra` → agregado `7060` (IPCA - Variação mensal...).
> 2. `explicar_tabela_sidra` → confirmei período (até 202505), nível
>    territorial `N1` (Brasil) e classificação `315` disponíveis.
> 3. `listar_variaveis_tabela_sidra` → variável `63` ("IPCA - Variação
>    mensal", %).
> 4. `listar_classificacoes_tabela_sidra` → classificação `315[7169]`
>    ("Índice geral").
> 5. `validar_consulta_sidra` → `valido=true`, sem avisos.
> 6. `executar_consulta_sidra_validada` → valor `0,26%` para `202505`.
>
> **Fonte**: IBGE — Agregados/SIDRA, agregado 7060 (IPCA), variável 63,
> classificação 315[7169] (Índice geral), localidade Brasil (N1), período
> 202505.

## Exemplo: validação falha (variável inexistente)

Para `validar_consulta_sidra(agregado_id="7060", variaveis="99999", localidades="N1[all]", periodos="-1")`:

```json
{
  "ok": false,
  "data": {
    "valido": false,
    "agregado_id": "7060",
    "variaveis_validas": [],
    "variaveis_invalidas": ["99999"],
    "niveis_territoriais": ["N1"],
    "niveis_invalidos": [],
    "classificacao_valida": null,
    "erros": [
      "Nenhuma das variáveis \"99999\" existe no agregado \"7060\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis."
    ],
    "avisos": []
  },
  "warnings": [],
  "errors": [
    {
      "message": "Nenhuma das variáveis \"99999\" existe no agregado \"7060\". Use `listar_variaveis_tabela_sidra` para ver as variáveis disponíveis.",
      "code": null
    }
  ]
}
```

Nesse caso, `executar_consulta_sidra_validada` com os mesmos parâmetros
retornaria o mesmo `errors`, `data=[]` e **não faria nenhuma requisição** ao
endpoint de dados — o agente deve corrigir `variaveis` (voltando ao passo 3)
e tentar de novo, em vez de chamar `consultar_agregado` diretamente.

## Como verificar a fonte

- `metadata.endpoint` de cada passo aponta para o endpoint correspondente da
  API de Agregados/SIDRA (`/agregados`, `/agregados/{id}/metadados`,
  `/agregados/{id}/periodos/{periodos}/variaveis/{variaveis}`).
- Endpoint final de dados:
  `https://servicodados.ibge.gov.br/api/v3/agregados/7060/periodos/-1/variaveis/63?localidades=N1[all]&classificacao=315[7169]`
- `data.limitacoes` (de `explicar_tabela_sidra`, passo 2) resume o intervalo
  de períodos e os níveis territoriais — cite isso ao apresentar o resultado
  (ex.: "dados mensais de 202001 a 202505, disponíveis para Brasil e regiões
  metropolitanas").
