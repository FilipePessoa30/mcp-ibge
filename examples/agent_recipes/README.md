# Receitas de agentes (agent recipes)

Receitas prontas — prompt + tools esperadas + exemplo de resposta — para usar
os módulos do **mcp-data-br** (`mcp-ibge`, `mcp-dados-gov-br`, ...) com um
agente de IA (Claude Desktop, Cursor, etc.). Cada receita é uma pasta com 4
arquivos:

- `README.md` — objetivo, fluxo de tools, limitações e como verificar a
  fonte.
- `prompt.md` — prompt(s) de exemplo, em linguagem natural.
- `expected_tools.md` — sequência de tools que um agente bem-comportado deve
  chamar (com argumentos), e por quê.
- `example_output.md` — exemplo de resposta das tools e da resposta final do
  agente ao usuário.

## Receitas disponíveis

| Receita | Módulo | Objetivo |
| --- | --- | --- |
| [`municipal_profile/`](municipal_profile/) | `mcp-ibge` | Gerar o perfil básico de um município brasileiro (identificação, região, população). |
| [`compare_municipalities/`](compare_municipalities/) | `mcp-ibge` | Comparar Rio de Janeiro, Niterói e Maricá com dados oficiais de população. |
| [`education_activity/`](education_activity/) | `mcp-ibge` | Criar uma atividade didática (geografia) usando dados e mapas de municípios. |
| [`public_policy_brief/`](public_policy_brief/) | `mcp-ibge` | Gerar um resumo (briefing) de política pública com dados municipais. |
| [`sidra_query_discovery/`](sidra_query_discovery/) | `mcp-ibge` | Descobrir tabela, variável, período e localidade no SIDRA antes de consultar dados. |
| [`find-public-datasets/`](find-public-datasets/) | `mcp-dados-gov-br` | Encontrar e detalhar datasets, organizações e recursos no Portal Brasileiro de Dados Abertos. |

Para chamadas de tool isoladas (sem o fluxo completo de uma receita), veja
[`mcp_ibge_queries.md`](mcp_ibge_queries.md).

## Convenções comuns a todas as receitas

- Toda tool do `mcp-ibge` retorna o mesmo envelope:
  `{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`.
  Veja [docs/data_sources.md](../../packages/mcp_ibge/docs/data_sources.md).
- **Nunca invente dados.** Se uma tool retornar `ok=false`,
  `data.*_nao_resolvidos`/`*_nao_implementados`, ou um `warning` informando
  que um valor não está disponível, a resposta final ao usuário deve
  refletir isso explicitamente — nunca preencher a lacuna com um valor
  estimado.
- Sempre cite a fonte: `metadata.source_name`/`metadata.source_url` (ou
  `data.fontes`, quando presente) e o período/ano (`metadata.period` ou o
  campo `periodo` de cada indicador).
- Os exemplos de resposta em `example_output.md` usam valores **ilustrativos**
  (mesmo formato das respostas reais, mas os números podem estar
  desatualizados). Execute as tools para obter os valores atuais.
