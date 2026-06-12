# Receita: Encontrar datasets públicos (`find-public-datasets`)

## Objetivo

Encontrar conjuntos de dados públicos relevantes para uma pergunta ou tema no
**Portal Brasileiro de Dados Abertos** (dados.gov.br), e detalhar um dataset
específico — incluindo os arquivos/links (recursos) disponíveis para download.

## Quando usar

Quando o usuário pergunta algo como "quais dados existem sobre X?", "onde
encontro dados sobre Y publicados pelo governo?", ou pede para buscar/detalhar
um dataset, organização, grupo temático ou tag no `mcp-dados-gov-br`.

## Fluxo

1. Se o usuário fizer uma **pergunta em linguagem natural** (ex.: "Quais dados
   existem sobre desmatamento na Amazônia?"), use
   [`sugerir_datasets_para_pergunta`](../../../docs/modules/dados-gov-br.md#sugerir_datasets_para_pergunta).
   A tool extrai palavras-chave da pergunta (sem usar nenhum modelo de
   linguagem — apenas tokenização e remoção de stopwords em português) e busca
   essas palavras no catálogo.
2. Se o usuário já informar **termos de busca diretos** (ex.: "busque datasets
   sobre vacinação covid-19"), use
   [`buscar_datasets`](../../../docs/modules/dados-gov-br.md) diretamente com
   esses termos.
3. Para detalhar um dataset específico encontrado no passo 1 ou 2, use
   [`obter_dataset`](../../../docs/modules/dados-gov-br.md) com o `id`
   retornado.
4. Para listar apenas os arquivos/links (CSV, JSON, API, PDF, XLSX, ...) de um
   dataset, use
   [`listar_recursos_dataset`](../../../docs/modules/dados-gov-br.md).
5. Opcionalmente, para saber mais sobre o órgão publicador de um dataset, use
   `buscar_organizacoes`/`obter_organizacao` com o campo `organization` do
   dataset.

Veja [`prompt.md`](prompt.md), [`expected_tools.md`](expected_tools.md) e
[`example_output.md`](example_output.md).

## Limitações

- **Não inventa datasets.** Toda lista vem diretamente de uma resposta da API
  CKAN do dados.gov.br — se nada corresponder à busca, a tool retorna `data:
  []` (lista vazia), nunca um exemplo fictício.
- `sugerir_datasets_para_pergunta` depende das palavras-chave extraídas da
  pergunta coincidirem com termos usados nos títulos/descrições/tags dos
  datasets no catálogo. Se a pergunta for composta só de palavras genéricas
  (ex.: "o que tem disponível?"), nenhuma palavra-chave sobra e a tool
  retorna `data: []` com um aviso em `warnings`, em vez de adivinhar.
- Algumas organizações/datasets podem exigir um token de consumidor
  (`DADOS_GOV_BR_API_TOKEN`). Se não configurado, a tool correspondente
  retorna `ok: false` com uma mensagem explicando como configurá-lo — veja
  [Autenticação](../../../docs/modules/dados-gov-br.md#authentication).

## Como verificar a fonte

- `metadata.endpoint` e `metadata.params` mostram exatamente qual ação CKAN
  (`package_search`, `package_show`, ...) e quais parâmetros foram usados.
- Para `sugerir_datasets_para_pergunta`, `metadata.params["keywords"]` mostra
  as palavras-chave extraídas da pergunta — útil para entender por que um
  dataset foi (ou não) sugerido.
- Para conferir um dataset diretamente, acesse
  `https://dados.gov.br/dados/conjuntos-dados/<name>` usando o campo `name`
  retornado por `buscar_datasets`/`obter_dataset`.
