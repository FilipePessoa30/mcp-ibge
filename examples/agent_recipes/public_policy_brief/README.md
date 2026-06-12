# Receita: Resumo de Política Pública (`public_policy_brief`)

## Objetivo

Gerar um resumo (*brief*) com dados oficiais para subsidiar discussão de
política pública em um município — neste exemplo, Maricá (RJ) — combinando
um perfil básico com a evolução recente da população estimada.

## Quando usar

Quando o usuário pede um documento de apoio (briefing, nota técnica, resumo
executivo) sobre um município, com dados demográficos atuais **e** uma série
histórica recente para contextualizar tendências (ex.: crescimento
populacional acelerado por conta de royalties do petróleo, em Maricá).

## Fluxo

1. [`gerar_perfil_municipal`](../../../packages/mcp_ibge/docs/tools.md#22-gerar_perfil_municipal)
   — identificação básica + população estimada do período mais recente.
2. [`listar_periodos_agregado`](../../../packages/mcp_ibge/docs/tools.md#11-listar_periodos_agregado)
   (`agregado_id="6579"`) — opcional, para confirmar quais períodos estão
   disponíveis antes de pedir uma série histórica.
3. [`consultar_agregado`](../../../packages/mcp_ibge/docs/tools.md#13-consultar_agregado)
   com `periodos="-5"` (ou um intervalo explícito, ex.: `"2020-2024"`) —
   série histórica da população estimada para o município, para mostrar a
   evolução nos últimos anos.

Veja [`prompt.md`](prompt.md), [`expected_tools.md`](expected_tools.md) e
[`example_output.md`](example_output.md).

## Limitações

- A série histórica vem do mesmo agregado SIDRA `6579` (Estimativas de
  população residente) — sujeita a metodologia que muda entre Censos, então
  **não é uma série "comparável" no sentido estrito** entre anos de Censo e
  anos de estimativa. Mencione essa ressalva no brief.
- `consultar_agregado` retorna `valor: null` quando o SIDRA marca o dado como
  ausente/sigiloso (`"-"`, `".."`, `"..."`, `"X"`) — **sem warning explícito**
  (diferente de `consultar_populacao_municipio`). O agente deve verificar
  manualmente se algum `valor` é `null` antes de montar a série/gráfico, e
  reportar a lacuna em vez de interpolar.
- Este brief não inclui indicadores socioeconômicos (PIB, IDH, orçamento
  municipal, indicadores de saúde/educação) — apenas população. Para outros
  indicadores, é necessário descobrir o agregado correto (veja
  [`sidra_query_discovery`](../sidra_query_discovery/)) antes de consultar.
- `gerar_perfil_municipal` não aceita lista de municípios — para comparar
  vários municípios no mesmo brief, combine com
  [`compare_municipalities`](../compare_municipalities/).

## Como verificar a fonte

- `data.fontes` (de `gerar_perfil_municipal`) e `metadata.endpoint` (de
  `consultar_agregado`) apontam para os endpoints oficiais do IBGE
  (Localidades e Agregados/SIDRA).
- Para a série histórica completa, acesse
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/<periodos>/variaveis/9324?localidades=N6[<codigo_ibge>]`
  com o `codigo_ibge` do município e o intervalo de `periodos` usado.
- `data.limitacoes` (de `gerar_perfil_municipal`) deve ser citado
  integralmente no brief, junto com a ressalva sobre `valor: null` acima.
