# Prompt do usuário

> Quais dados existem sobre desmatamento na Amazônia no Portal Brasileiro de
> Dados Abertos?

## Variações

- "Busque datasets sobre vacinação contra covid-19 no dados.gov.br." — termos
  de busca diretos; use `buscar_datasets` em vez de
  `sugerir_datasets_para_pergunta`.
- "Me mostra os detalhes desse dataset e quais arquivos posso baixar." —
  segue a sugestão anterior com `obter_dataset` e/ou
  `listar_recursos_dataset` usando o `id` de um dataset já encontrado.
- "Quais órgãos publicam dados sobre educação?" — use
  `buscar_organizacoes(query="educação")`.
- "O que tem disponível?" — pergunta composta só de palavras genéricas; testa
  o caminho em que `sugerir_datasets_para_pergunta` não encontra
  palavras-chave e retorna `data: []` com um aviso.
