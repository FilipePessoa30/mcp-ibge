# Receita: Perfil Municipal (`municipal_profile`)

## Objetivo

Gerar o perfil básico de um município brasileiro: identificação (código
IBGE), UF, região, microrregião/região intermediária e população residente
estimada mais recente — em uma única chamada.

## Quando usar

Quando o usuário pede "um perfil", "uma ficha" ou "informações básicas" sobre
um município específico (ex.: "me conta sobre Niterói").

## Fluxo

A tool [`gerar_perfil_municipal`](../../../packages/mcp_ibge/docs/tools.md#22-gerar_perfil_municipal)
já combina:

1. Resolução do código IBGE (`obter_codigo_municipio`).
2. Identificação, UF, região e microrregião (`obter_municipio_por_codigo`).
3. População estimada mais recente (`consultar_populacao_municipio`).

Veja [`prompt.md`](prompt.md) para o prompt do usuário,
[`expected_tools.md`](expected_tools.md) para a chamada exata, e
[`example_output.md`](example_output.md) para o exemplo de resposta.

## Limitações

- O perfil cobre **apenas** identificação básica + população estimada — não
  inclui PIB, IDH, área territorial ou indicadores de saúde/educação (ver
  `data.proximos_indicadores_sugeridos` na resposta).
- O indicador de população usa o agregado SIDRA `6579` (Estimativas de
  População), que o IBGE pode descontinuar/renomear após um novo Censo.
- Se `ano` não for informado, cada execução usa o período mais recente
  disponível no SIDRA — o valor retornado pode mudar entre execuções em
  datas diferentes.
- Se o município não for encontrado, ou o nome for ambíguo dentro da UF
  informada (ex.: mais de um município com nome parecido), a tool retorna
  `ok=false` com `warnings`/`errors` explicando — o agente deve repassar isso
  ao usuário e pedir mais detalhes (ex.: confirmar a UF).

## Como verificar a fonte

- `metadata.source_url`/`metadata.endpoint` apontam para o endpoint exato da
  [API de Localidades do IBGE](https://servicodados.ibge.gov.br/api/docs/localidades)
  usado para identificar o município.
- `data.fontes` lista todos os endpoints usados (Localidades + Agregados/SIDRA).
- `data.limitacoes` resume as limitações conhecidas do indicador de
  população.
- Para conferir o número de população diretamente, acesse
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/<periodo>/variaveis/9324?localidades=N6[<codigo_ibge>]`
  no navegador (mesmo endpoint usado por `consultar_populacao_municipio`).
