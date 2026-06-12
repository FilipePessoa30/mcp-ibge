# Receita: Descoberta de Consulta SIDRA (`sidra_query_discovery`)

## Objetivo

Ensinar um agente a **descobrir** a tabela (agregado), variável,
classificação, período e localidade corretos no SIDRA antes de chamar
[`consultar_agregado`](../../../packages/mcp_ibge/docs/tools.md#13-consultar_agregado)
— em vez de "adivinhar" IDs, usando o exemplo do IPCA (variação mensal do
índice de preços ao consumidor).

## Quando usar

Sempre que o usuário pedir um indicador do SIDRA que **não** é coberto pelas
tools de alto nível (`gerar_perfil_municipal`, `comparar_municipios`,
`consultar_populacao_municipio`) — ex.: inflação (IPCA), desemprego, PIB,
preços agrícolas, etc. Esta receita é o caminho recomendado em vez de
chamar `consultar_agregado` com IDs inventados.

## Fluxo

O fluxo segue
[Como descobrir agregado, variável, período e localidade](../../../packages/mcp_ibge/docs/tools.md#como-descobrir-agregado-variável-período-e-localidade)
do `docs/tools.md`, usando o conjunto "SIDRA Query Builder":

1. [`buscar_tabelas_sidra`](../../../packages/mcp_ibge/docs/tools.md#15-buscar_tabelas_sidra)
   (`tema="IPCA inflação"`) — encontra candidatos a agregado por
   palavra-chave.
2. [`explicar_tabela_sidra`](../../../packages/mcp_ibge/docs/tools.md#16-explicar_tabela_sidra)
   (`agregado_id="7060"`) — confirma nome, período disponível, níveis
   territoriais e classificações do agregado escolhido.
3. [`listar_variaveis_tabela_sidra`](../../../packages/mcp_ibge/docs/tools.md#17-listar_variaveis_tabela_sidra)
   e [`listar_classificacoes_tabela_sidra`](../../../packages/mcp_ibge/docs/tools.md#18-listar_classificacoes_tabela_sidra)
   (`agregado_id="7060"`) — identificam a variável (`"63"` = "IPCA -
   Variação mensal") e a classificação/categoria (`"315[7169]"` = "Índice
   geral").
4. (Opcional) [`sugerir_consulta_sidra`](../../../packages/mcp_ibge/docs/tools.md#19-sugerir_consulta_sidra)
   — sugestão heurística (sem LLM) de `agregado_id`/`variaveis`/`localidades`
   a partir de uma pergunta em linguagem natural; **sempre revise** o
   resultado com `validar_consulta_sidra` antes de executar.
5. [`validar_consulta_sidra`](../../../packages/mcp_ibge/docs/tools.md#20-validar_consulta_sidra)
   — confirma que `variaveis`, `localidades`, `periodos` e `classificacao`
   existem de fato no agregado, **sem** consultar os dados.
6. [`executar_consulta_sidra_validada`](../../../packages/mcp_ibge/docs/tools.md#21-executar_consulta_sidra_validada)
   — só executa a consulta se `data.valido=true`; caso contrário, retorna
   `ok=false` sem fazer requisições adicionais.

Veja [`prompt.md`](prompt.md), [`expected_tools.md`](expected_tools.md) e
[`example_output.md`](example_output.md).

## Limitações

- [`sugerir_consulta_sidra`](../../../packages/mcp_ibge/docs/tools.md#19-sugerir_consulta_sidra)
  usa **busca por palavras-chave em metadados, sem modelo de linguagem** — o
  agregado/variável sugeridos podem não ser os mais adequados. O próprio
  retorno inclui o aviso: *"Sugestão gerada por busca de palavras-chave em
  metadados (sem uso de modelos de linguagem); revise os parâmetros antes de
  executar, com `validar_consulta_sidra` ou `explicar_tabela_sidra`."*
- [`validar_consulta_sidra`](../../../packages/mcp_ibge/docs/tools.md#20-validar_consulta_sidra)
  valida **formato e existência** dos IDs, mas não garante que a
  combinação retorne dados não-vazios — isso só é confirmado ao executar.
- [`executar_consulta_sidra_validada`](../../../packages/mcp_ibge/docs/tools.md#21-executar_consulta_sidra_validada)
  não faz nenhuma requisição de dados se a validação falhar (`ok=false`,
  `data=[]`) — o agente não deve tentar `consultar_agregado` diretamente
  como alternativa nesse caso, e sim corrigir os parâmetros e revalidar.
- `consultar_agregado`/`executar_consulta_sidra_validada` retornam
  `valor: null` quando o SIDRA marca o dado como ausente/sigiloso — **sem**
  warning explícito; o agente deve checar `valor` antes de apresentar o
  número.
- Nem todo indicador citado pelo usuário tem um agregado pronto no SIDRA —
  se `buscar_tabelas_sidra` não encontrar nada relevante, informe isso ao
  usuário em vez de escolher o agregado "mais próximo".

## Como verificar a fonte

- Cada passo retorna `metadata.endpoint`, que pode ser aberto diretamente no
  navegador (`GET /agregados`, `GET /agregados/{id}/metadados`).
- O endpoint final de dados é
  `https://servicodados.ibge.gov.br/api/v3/agregados/<agregado_id>/periodos/<periodos>/variaveis/<variaveis>?localidades=<localidades>&classificacao=<classificacao>`.
- `data.limitacoes` (de `explicar_tabela_sidra`) resume o intervalo de
  períodos e os níveis territoriais suportados — cite isso ao apresentar o
  resultado.
