# Exemplos de uso das tools

Exemplos de chamadas às tools do `mcp-ibge`, com os argumentos esperados.
Em um cliente MCP (Claude Desktop, Cursor, etc.) basta pedir em linguagem
natural — o modelo escolhe a tool e os argumentos. Os exemplos abaixo
mostram o `name` da tool e o `arguments` equivalente, úteis para depuração
ou para chamadas diretas via `mcp.call_tool`.

## Perguntas de teste (linguagem natural)

Após configurar o servidor em um cliente MCP (veja
[docs/client_setup.md](../../packages/mcp_ibge/docs/client_setup.md)), use estas perguntas para
verificar se a integração está funcionando. Cada uma deve levar o modelo a
chamar uma ou mais das tools listadas abaixo.

- "Liste os estados brasileiros." → `listar_estados`
- "Qual é o código IBGE de Niterói, RJ?" → `obter_codigo_municipio`
- "Liste os municípios do Rio de Janeiro." → `listar_municipios` (`uf="RJ"`)
- "Busque municípios chamados São José." → `buscar_municipio` (deve incluir
  `warnings` com vários candidatos)
- "Consulte os metadados do agregado 6579 do SIDRA." →
  `obter_metadados_agregado`
- "Liste as variáveis do agregado 6579." → `listar_variaveis_agregado`
- "Compare a população do Rio de Janeiro e de Niterói." →
  `consultar_populacao_municipio` para cada município (e idealmente o prompt
  `comparar_municipios`)

## Localidades

### Listar as grandes regiões do Brasil

```json
{ "name": "listar_regioes", "arguments": {} }
```

### Listar todos os estados (ordenados por nome)

```json
{ "name": "listar_estados", "arguments": {} }
```

### Detalhes de um estado

```json
{ "name": "obter_estado", "arguments": { "uf": "SP" } }
```

### Listar municípios de um estado

```json
{ "name": "listar_municipios", "arguments": { "uf": "SP" } }
```

### Buscar municípios pelo nome (ignora acentos/caixa, fuzzy)

```json
{
  "name": "buscar_municipio",
  "arguments": { "nome": "sao jose", "uf": "SP", "limite": 5 }
}
```

> Sem `uf`, a busca considera todos os municípios do Brasil. Se houver mais
> de um candidato, a resposta inclui um campo `warnings` listando os
> candidatos encontrados.

### Obter o código IBGE de um município pelo nome e UF

```json
{ "name": "obter_codigo_municipio", "arguments": { "nome": "Florianópolis", "uf": "SC" } }
```

### Detalhes de um município pelo código IBGE

```json
{ "name": "obter_municipio_por_codigo", "arguments": { "codigo_ibge": 3550308 } }
```

### Listar os distritos de um município

```json
{ "name": "listar_distritos", "arguments": { "codigo_municipio": 3550308 } }
```

## Agregados / SIDRA

Veja também [docs/tools.md](../../packages/mcp_ibge/docs/tools.md#como-descobrir-agregado-variável-período-e-localidade)
para o guia completo de como descobrir agregado, variável, período e
localidade antes de chamar `consultar_agregado`.

### Listar agregados disponíveis com filtro textual

```json
{
  "name": "listar_agregados",
  "arguments": { "assunto": "População", "texto": "estimada" }
}
```

### Metadados de um agregado (pesquisa, assunto, periodicidade)

```json
{ "name": "obter_metadados_agregado", "arguments": { "agregado_id": "6579" } }
```

### Variáveis, períodos e localidades disponíveis em um agregado

```json
{ "name": "listar_variaveis_agregado", "arguments": { "agregado_id": "6579" } }
```

```json
{ "name": "listar_periodos_agregado", "arguments": { "agregado_id": "6579" } }
```

```json
{ "name": "listar_localidades_agregado", "arguments": { "agregado_id": "6579", "niveis": "N6" } }
```

### Consultar dados de um agregado para o Brasil

```json
{
  "name": "consultar_agregado",
  "arguments": {
    "agregado_id": "6579",
    "variaveis": "9324",
    "periodos": "-1",
    "localidades": "BR"
  }
}
```

### Consultar dados de um agregado para um município específico

```json
{
  "name": "consultar_agregado",
  "arguments": {
    "agregado_id": "6579",
    "variaveis": "9324",
    "localidades": "N6[3550308]"
  }
}
```

### Fluxo de descoberta completo: variação mensal do IPCA (agregado `7060`)

Exemplo real de ponta a ponta — do agregado `1419` em diante o IBGE
descontinua tabelas e abre novas (a tabela `7060` é a vigente desde
janeiro/2020). Use `listar_agregados` para confirmar qual está ativa caso
estes IDs mudem no futuro.

```json
{
  "name": "listar_agregados",
  "arguments": {
    "pesquisa": "Índice Nacional de Preços ao Consumidor Amplo",
    "texto": "a partir de janeiro/2020"
  }
}
```

```json
{ "name": "obter_metadados_agregado", "arguments": { "agregado_id": "7060" } }
```

```json
{ "name": "listar_variaveis_agregado", "arguments": { "agregado_id": "7060" } }
```

```json
{ "name": "listar_periodos_agregado", "arguments": { "agregado_id": "7060" } }
```

```json
{ "name": "listar_localidades_agregado", "arguments": { "agregado_id": "7060", "niveis": "N1" } }
```

A consulta final usa a variável `63` ("IPCA - Variação mensal", em `%`), a
classificação `315` com a categoria `7169` ("Índice geral"), e o nível
territorial `N1` (Brasil):

```json
{
  "name": "consultar_agregado",
  "arguments": {
    "agregado_id": "7060",
    "variaveis": "63",
    "localidades": "N1[all]",
    "periodos": "-1",
    "classificacao": "315[7169]"
  }
}
```

## Indicadores

### População estimada de um município (por nome e UF)

```json
{ "name": "consultar_populacao_municipio", "arguments": { "nome": "São Paulo", "uf": "SP" } }
```

### População de um município em um ano específico

```json
{
  "name": "consultar_populacao_municipio",
  "arguments": { "nome": "São Paulo", "uf": "SP", "ano": 2010 }
}
```
