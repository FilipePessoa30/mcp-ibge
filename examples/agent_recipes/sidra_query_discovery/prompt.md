# Prompt do usuário

> Qual foi a variação mensal do IPCA no Brasil no último mês com dado
> disponível? Me explique como você chegou nesse número (tabela, variável e
> período usados).

## Variações

- "Existe uma tabela do IBGE com a inflação por região metropolitana?" — o
  agente deve usar `buscar_tabelas_sidra` para procurar e relatar
  honestamente se não encontrar nada adequado.
- "Você pode simplesmente chamar `consultar_agregado` com o agregado do IPCA
  direto, sem validar?" — o agente deve explicar por que prefere validar
  primeiro (evitar IDs incorretos/inexistentes) e seguir o fluxo de
  descoberta.
- "Tente adivinhar a consulta certa para 'taxa de desemprego trimestral' e
  depois confirme se está certa." — usa `sugerir_consulta_sidra` seguido de
  `validar_consulta_sidra`, deixando claro que a sugestão é heurística e
  precisa de revisão.
- "E se a variável '63' não existir nesse agregado, o que acontece?" — mostra
  o caminho de `validar_consulta_sidra`/`executar_consulta_sidra_validada`
  com `ok=false`.
