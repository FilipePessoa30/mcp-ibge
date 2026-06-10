# Tools disponíveis

Todas as tools retornam um envelope JSON com `metadata` e (`data` ou
`error`) — veja [data_sources.md](data_sources.md) para o formato completo.
As tools de Localidades também podem incluir um campo opcional `warnings`
(lista de strings) quando o resultado é ambíguo (ex.: mais de um município
corresponde ao nome buscado).

## Localidades

### `listar_regioes`

Lista as 5 grandes regiões geográficas do Brasil (Norte, Nordeste, Sudeste,
Sul, Centro-Oeste).

- **Argumentos**: nenhum.
- **Endpoint**: `GET /localidades/regioes`.

### `listar_estados`

Lista os 26 estados e o Distrito Federal, ordenados por nome.

- **Argumentos**: nenhum.
- **Endpoint**: `GET /localidades/estados`.

### `obter_estado`

Detalhes de um estado (UF).

- **Argumentos**:
  - `uf` (obrigatório): sigla (ex.: `"SP"`) ou código IBGE (ex.: `"35"`).
- **Endpoint**: `GET /localidades/estados/{uf}`.

### `listar_municipios`

Lista os municípios de uma UF, com UF e região resolvidas em cada item
(`uf_sigla`, `uf_nome`, `regiao_nome`).

- **Argumentos**:
  - `uf` (obrigatório): sigla (ex.: `"SP"`) ou código IBGE da UF.
- **Endpoint**: `GET /localidades/estados/{uf}/municipios`.

### `buscar_municipio`

Busca municípios por nome com correspondência aproximada (fuzzy), ignorando
acentos e maiúsculas/minúsculas. Tenta, nesta ordem: correspondência exata,
"contém" e, por fim, similaridade textual. Sem `uf`, busca em todo o Brasil.

- **Argumentos**:
  - `nome` (obrigatório): nome (ou parte do nome) do município.
  - `uf` (opcional): restringe a busca a uma UF (sigla ou código).
  - `limite` (opcional, padrão `10`, entre 1 e 50): número máximo de
    candidatos retornados.
- **Endpoint**: `GET /localidades/estados/{uf}/municipios` ou
  `GET /localidades/municipios`, com filtro aplicado localmente.
- Quando há mais de um candidato, a resposta inclui `warnings` sugerindo
  refinar a busca (ex.: informar `uf`).

### `obter_codigo_municipio`

Obtém o código IBGE de 7 dígitos de um município pelo nome e UF.

- **Argumentos**:
  - `nome` (obrigatório): nome do município.
  - `uf` (obrigatório): sigla ou código IBGE da UF.
- **Endpoint**: mesmo de `listar_municipios`, com filtro aplicado localmente.
- Retorna erro se nenhum município corresponder ou se o nome for ambíguo
  dentro da UF informada.

### `obter_municipio_por_codigo`

Detalhes de um município pelo código IBGE, com UF e região resolvidas
(`uf_sigla`, `uf_nome`, `regiao_nome`).

- **Argumentos**:
  - `codigo_ibge` (obrigatório): código IBGE com 7 dígitos (ex.: `3550308`).
- **Endpoint**: `GET /localidades/municipios/{codigo_ibge}`.

### `listar_distritos`

Lista os distritos de um município.

- **Argumentos**:
  - `codigo_municipio` (obrigatório): código IBGE do município com 7 dígitos
    (ex.: `3550308`).
- **Endpoint**: `GET /localidades/municipios/{codigo_municipio}/distritos`.

## Agregados / SIDRA

### `listar_agregados`

Lista os agregados (tabelas estatísticas) disponíveis no SIDRA, cada um com
`id` e `nome`. Use para descobrir o ID de um agregado antes de chamar
`obter_metadados_agregado`, `listar_variaveis_agregado` ou
`consultar_agregado`.

- **Argumentos**:
  - `pesquisa` (opcional): nome/sigla da pesquisa de origem (ex.: `"Censo
    Demográfico"`).
  - `assunto` (opcional): nome do assunto (ex.: `"População"`).
  - `texto` (opcional): filtro textual adicional aplicado ao nome dos
    agregados (substring, sem distinção de caixa).
- **Endpoint**: `GET /agregados`.

### `obter_metadados_agregado`

Metadados de um agregado: `pesquisa`, `assunto` e `periodicidade`. O JSON
completo (incluindo `variaveis`, `classificacoes` e `nivelTerritorial`) fica
disponível em `raw`. Use o resultado para escolher os parâmetros de
`consultar_agregado`.

- **Argumentos**:
  - `agregado_id` (obrigatório): ID do agregado (ex.: `"6579"`).
- **Endpoint**: `GET /agregados/{agregado_id}/metadados`.

### `listar_variaveis_agregado`

Lista as variáveis disponíveis em um agregado, cada uma com `id`, `nome` e
`unidade`. Use o `id` de uma variável no parâmetro `variaveis` de
`consultar_agregado`.

- **Argumentos**:
  - `agregado_id` (obrigatório): ID do agregado.
- **Endpoint**: `GET /agregados/{agregado_id}/variaveis`.

### `listar_periodos_agregado`

Lista os períodos disponíveis para consulta em um agregado, cada um com `id`
(ex.: `"2024"`) e `nome`. Use o `id` de um período no parâmetro `periodos` de
`consultar_agregado`.

- **Argumentos**:
  - `agregado_id` (obrigatório): ID do agregado.
- **Endpoint**: `GET /agregados/{agregado_id}/periodos`.

### `listar_localidades_agregado`

Lista as localidades disponíveis para um agregado em um ou mais níveis
territoriais, cada uma com `id`, `nome` e `nivel` (sem schema tipado: os
itens são devolvidos como vieram da API). Use o `id` de uma localidade no
parâmetro `localidades` de `consultar_agregado` (ex.: `"N6[3550308]"`).

- **Argumentos**:
  - `agregado_id` (obrigatório): ID do agregado.
  - `niveis` (obrigatório): nível territorial (ex.: `"N6"`) ou múltiplos
    separados por `"|"` (ex.: `"N1|N3"`).
- **Endpoint**: `GET /agregados/{agregado_id}/localidades/{niveis}`.

### `consultar_agregado`

Consulta valores de um agregado do SIDRA para variáveis, períodos e
localidades específicas. Retorna uma lista "achatada" de valores, um por
combinação de (variável, localidade, período), cada um com `agregado_id`,
`variavel_id`, `localidade_id`, `localidade_nome`, `periodo`, `valor`
(número, ou `null` quando o dado é ausente/sigiloso no SIDRA) e `unidade`.

- **Argumentos**:
  - `agregado_id` (obrigatório): ID do agregado.
  - `variaveis` (obrigatório): ID de variável, lista separada por vírgula, ou
    `"all"`.
  - `localidades` (obrigatório): unidade territorial no formato
    `N<nivel>[<ids>]`, ex.: `"N1[all]"` (Brasil), `"N3[all]"` (todos os
    estados), `"N6[3550308]"` (município de São Paulo). `"BR"` é aceito como
    atalho para `"N1[all]"`.
  - `periodos` (opcional, padrão `"-6"`): um ano (`"2021"`), intervalo
    (`"2010-2020"`), lista (`"2019,2021"`) ou relativo (`"-6"` = últimos 6
    períodos, `"-1"` = último período disponível).
  - `classificacao` (opcional): filtro de classificação, formato
    `"<id_classificacao>[<id_categoria>]"`.
  - `view` (opcional): formato alternativo de resposta da API (ex.:
    `"flat"`).
- **Endpoint**: `GET /agregados/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}`.

> Para descobrir IDs válidos de variáveis, períodos e localidades, use
> `listar_variaveis_agregado`, `listar_periodos_agregado` e
> `listar_localidades_agregado`.

## Indicadores

### `consultar_populacao_municipio`

População residente estimada de um município, identificado por `nome` e
`uf`. Resolve o código IBGE do município via o serviço de Localidades (mesma
busca fuzzy de `obter_codigo_municipio`) e consulta o agregado SIDRA
"Estimativas de população residente" (ver `AGREGADO_POPULACAO_ESTIMADA` /
`VARIAVEL_POPULACAO_ESTIMADA` em `agregados_service`). Retorna o mesmo
formato "achatado" de `consultar_agregado`.

- **Argumentos**:
  - `nome` (obrigatório): nome do município.
  - `uf` (obrigatório): sigla ou código IBGE da UF.
  - `ano` (opcional): ano de referência. Sem este parâmetro, usa o período
    mais recente disponível.
- **Endpoint**: `GET /agregados/6579/periodos/{periodos}/variaveis/9324`.

> Se o nome for ambíguo dentro da UF, ou se nenhum município for encontrado, a
> tool retorna erro com os candidatos encontrados. Se a tabela de população
> tiver sido descontinuada ou renomeada pelo IBGE, retorna erro orientando a
> usar `consultar_agregado` diretamente, após localizar os IDs corretos com
> `listar_agregados`, `obter_metadados_agregado` e `listar_variaveis_agregado`.
>
> A resposta de sucesso pode incluir `warnings` adicionais sobre incertezas
> metodológicas: dado ausente/sigiloso no SIDRA para o período, ou qual
> período foi efetivamente retornado quando `ano` não é informado.
