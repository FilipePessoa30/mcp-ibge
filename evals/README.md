# Evals

Este diretório contém um framework de avaliação para checar se um agente (ex.:
um LLM com acesso às tools do `mcp-data-br`) usa corretamente as tools MCP
expostas pelo `mcp_ibge` — escolhendo a tool certa, lendo os campos certos da
resposta, citando a fonte e reagindo apropriadamente a `warnings`/`errors`.

Tudo aqui é **stdlib-only** (`json`, `argparse`, `html`, `pathlib`, `typing`):
não há dependência de nenhuma API paga nem de um modelo de linguagem para
rodar os evals. Quem produz as respostas do agente (e portanto pode envolver
um LLM) é responsabilidade de quem gera o arquivo de `--results`; o runner
apenas compara esse arquivo com os datasets.

## Layout

```
evals/
  README.md
  datasets/
    localidades_basic.json   # tools de localidades (municípios, regiões, distritos)
    ambiguity_cases.json      # nomes ambíguos (ex.: "São José") e como o agente deve lidar com eles
    sidra_basic.json          # tools de agregados/SIDRA
  metrics.py                  # implementação das métricas
  runner.py                   # CLI que roda os evals e gera o relatório HTML
  example_results.json        # exemplo de arquivo de resultados (formato de entrada do runner)
  reports/
    example_report.html       # relatório gerado a partir de example_results.json
```

## Dataset: schema de cada caso

Cada arquivo em `datasets/*.json` contém uma lista de casos. Todos os
arquivos são carregados e concatenados pelo runner (ordenados por `id`), então
o nome do arquivo é só uma forma de organização por assunto.

Cada caso tem os seguintes campos:

| Campo | Tipo | Descrição |
| --- | --- | --- |
| `id` | `string` | Identificador único do caso (ex.: `"loc_001"`). |
| `user_question` | `string` | Pergunta em linguagem natural que seria feita ao agente. |
| `expected_tools` | `list[string]` | Tools MCP que o agente deveria chamar. O **primeiro** item é a "tool primária": é o `result` dessa chamada que é usado pelas métricas de campo, fonte, warnings e validade do envelope. |
| `expected_fields` | `list[object]` | Verificações sobre o envelope de resposta da tool primária (ver sintaxe abaixo). |
| `expected_answer_contains` | `list[string]` | Substrings que deveriam aparecer na resposta final do agente (`final_answer`), comparação *case-insensitive*. |
| `should_warn` | `boolean` | Se a resposta da tool primária deveria conter `warnings` (ex.: nome ambíguo, ano não informado). |
| `difficulty` | `string` | `"easy"`, `"medium"` ou `"hard"` — apenas informativo, não afeta as métricas. |
| `category` | `string` | Categoria do caso (ex.: `"localidades"`, `"ambiguity"`, `"sidra"`) — usada para agrupar métricas por categoria no relatório. |

### Sintaxe de `expected_fields`

Cada item de `expected_fields` tem um campo `"path"` e **exatamente um** dos
seguintes operadores:

| Operador | Significado |
| --- | --- |
| `"equals": <valor>` | O valor no `path` deve ser igual a `<valor>`. |
| `"contains": <valor>` | `<valor>` deve estar contido no valor do `path` (string, lista, etc.). |
| `"min_length": <n>` | `len(valor)` deve ser `>= n`. |
| `"not_null": true/false` | O `path` deve existir e ser (ou não) `None`. |
| `"in": [<valores>]` | O valor no `path` deve estar entre `<valores>`. |

`path` é uma string com segmentos separados por `.`, resolvida sobre o
envelope de resposta (`{ok, data, metadata, warnings, errors}`) da tool
primária. Segmentos puramente numéricos indexam listas. Exemplos:

- `"data"` → o campo `data` do envelope.
- `"data.0.localidade_nome"` → o campo `localidade_nome` do primeiro item de `data`.
- `"metadata.params.uf"` → `metadata["params"]["uf"]`.
- `"errors"` com `"min_length": 1` → pelo menos um erro foi retornado.

### Exemplo de caso

```json
{
  "id": "loc_001",
  "user_question": "Qual é o código IBGE de Niterói, RJ?",
  "expected_tools": ["obter_codigo_municipio"],
  "expected_fields": [
    { "path": "data", "equals": 3303302 }
  ],
  "expected_answer_contains": ["3303302"],
  "should_warn": false,
  "difficulty": "easy",
  "category": "localidades"
}
```

## Arquivo de resultados (`--results`)

O runner **não chama o agente** — ele lê um arquivo JSON com os resultados já
produzidos por uma execução do agente contra os casos do dataset. O arquivo é
uma lista de objetos, um por caso avaliado:

```json
[
  {
    "id": "loc_001",
    "tool_calls": [
      {
        "name": "obter_codigo_municipio",
        "arguments": { "nome": "Niterói", "uf": "RJ" },
        "result": { "ok": true, "data": 3303302, "metadata": { ... }, "warnings": [], "errors": [] }
      }
    ],
    "final_answer": "O código IBGE de Niterói (RJ) é 3303302."
  }
]
```

- `id`: deve corresponder ao `id` de um caso do dataset.
- `tool_calls`: lista das tools chamadas pelo agente para responder a
  `user_question`, na ordem em que foram chamadas. Cada item tem `name`
  (nome da tool), `arguments` (argumentos usados) e `result` (o envelope de
  resposta retornado pela tool, no formato `{ok, data, metadata, warnings,
  errors}`).
- `final_answer`: a resposta final em linguagem natural dada ao usuário.

Casos do dataset sem um item correspondente no arquivo de resultados são
tratados como **não tentados** (`attempted=False`) e pontuam `0`/`✗` em todas
as métricas — isso penaliza lacunas de cobertura do agente.

Veja [`example_results.json`](example_results.json) para um exemplo completo
(incluindo um caso com a tool errada e três casos não tentados).

## Métricas

Para cada caso, a tool primária é `expected_tools[0]`; seu `result` (se a
tool foi chamada) é o "resultado primário" usado pelas métricas abaixo.

| Métrica | Tipo | O que mede |
| --- | --- | --- |
| `tool_selection_accuracy` | fração 0–1 | Quantas das `expected_tools` foram chamadas pelo agente (em qualquer ordem). |
| `field_accuracy` | fração 0–1 | Quantas verificações de `expected_fields` passaram contra o resultado primário. |
| `source_presence` | booleano | Se `metadata.source_url` está presente e `metadata.source_name` menciona "IBGE" no resultado primário. |
| `warning_correctness` | booleano | Se a presença de `warnings` no resultado primário corresponde a `should_warn`. |
| `structured_output_validity` | booleano | Se o resultado primário segue o contrato de envelope `{ok, data, metadata, warnings, errors}`, com os 11 campos de `metadata` e `warnings`/`errors` como listas de `{message, code}`. |
| `answer_contains_accuracy` | fração 0–1 | Quantas strings de `expected_answer_contains` aparecem em `final_answer` (case-insensitive). Métrica extra, além das 5 solicitadas originalmente. |

Casos não tentados pontuam `0`/`false` em todas as métricas. O relatório
mostra a média geral, a média por `category` e o detalhe por caso.

## Como rodar

```bash
python evals/runner.py --results path/to/results.json
```

Opções:

- `--results PATH` (obrigatório): arquivo JSON com os resultados do agente.
- `--datasets DIR` (padrão: `evals/datasets`): diretório com os datasets `*.json`.
- `--output PATH` (padrão: `evals/reports/report.html`): caminho do relatório HTML gerado.

Exemplo com o resultado de exemplo incluído neste diretório:

```bash
cd evals
python runner.py --results example_results.json --output reports/example_report.html
```

Isso imprime um resumo no terminal (geral e por categoria) e escreve um
relatório HTML autocontido (sem dependências externas, CSS embutido) em
`reports/example_report.html`, com uma tabela por caso mostrando tools
esperadas vs. chamadas e o resultado de cada métrica.
