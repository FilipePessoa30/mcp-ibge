# Prompt do usuário

> Estou redigindo uma nota técnica sobre o crescimento populacional de Maricá
> (RJ) para uma discussão de planejamento urbano. Me dê um resumo com a
> identificação do município, a população estimada mais recente e a evolução
> da população nos últimos 5 anos, com as fontes.

## Variações

- "Mostre a evolução da população de Maricá entre 2020 e 2024, ano a ano."
  — usa `periodos="2020-2024"` em vez de `periodos="-5"`.
- "Esse dado de população é do último Censo ou é uma estimativa?" — o agente
  deve explicar a diferença, citando `data.limitacoes`.
- "Inclua também o PIB per capita de Maricá no resumo." — PIB não está
  disponível nesta versão; o agente deve explicar a limitação e, se o usuário
  insistir, sugerir a receita [`sidra_query_discovery`](../sidra_query_discovery/)
  para investigar se esse dado existe no SIDRA (sem garantia de que exista um
  agregado pronto para uso).
- "Faça o mesmo resumo, mas para Niterói." — mesmo fluxo, troque
  `nome`/`uf`/`codigo_ibge`.
