# Receita: Comparação de Municípios (`compare_municipalities`)

## Objetivo

Comparar Rio de Janeiro, Niterói e Maricá (RJ) com dados oficiais do IBGE —
neste exemplo, população residente estimada — em uma única tabela, com fonte
e período citados.

## Quando usar

Quando o usuário pede para comparar 2 a 10 municípios em um ou mais
indicadores (ex.: "qual cidade é maior, Niterói ou Maricá?").

## Fluxo

A tool [`comparar_municipios`](../../../packages/mcp_ibge/docs/tools.md#23-comparar_municipios)
resolve cada município (nome + UF) independentemente e consulta os
indicadores suportados (hoje, apenas população estimada). Municípios não
encontrados/ambíguos e indicadores não suportados não interrompem a
comparação — aparecem em listas separadas (`municipios_nao_resolvidos`,
`indicadores_nao_implementados`).

Veja [`prompt.md`](prompt.md), [`expected_tools.md`](expected_tools.md) e
[`example_output.md`](example_output.md).

## Limitações

- Apenas o indicador `"populacao_estimada"` está implementado hoje. Outros
  indicadores pedidos (ex.: `"pib"`, `"idh"`) entram em
  `data.indicadores_nao_implementados` — apenas o nome, **nunca** um valor
  inventado.
- Sem o parâmetro `ano`, cada município retorna o período mais recente
  disponível no SIDRA — se algum município não tiver dados para o período
  mais recente, os períodos podem **divergir entre municípios** (verifique o
  campo `periodo` de cada indicador antes de comparar).
- O indicador de população usa o agregado SIDRA `6579`, que pode ser
  descontinuado/renomeado pelo IBGE após um novo Censo.
- Município não encontrado ou nome ambíguo na UF informada não interrompe a
  comparação dos demais — aparece em `data.municipios_nao_resolvidos`, com o
  `motivo`.
- No máximo 10 municípios por chamada (`MAX_MUNICIPIOS = 10`).

## Como verificar a fonte

- `data.fontes` lista, sem duplicatas, todos os endpoints do IBGE usados
  (Localidades, para resolver cada município, e Agregados/SIDRA, para a
  população).
- `data.limitacoes` resume as limitações acima em texto, pronto para incluir
  na resposta ao usuário.
- Para conferir um valor específico, acesse
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/<periodo>/variaveis/9324?localidades=N6[<codigo_ibge>]`
  usando o `codigo_ibge` e o `periodo` de `data.municipios[].indicadores[]`.
