# Fontes de dados e formato de resposta

## APIs do IBGE utilizadas

Todas as fontes são públicas, gratuitas e **não exigem chave de API**. Os
clientes compartilham uma URL base comum (`MCP_IBGE_API_BASE_URL`, padrão
`https://servicodados.ibge.gov.br/api`) e cada um acrescenta seu próprio
prefixo de versão/recurso:

| API | Caminho | URL completa (padrão) | Usada por |
| --- | --- | --- | --- |
| Localidades | `/v1/localidades` | `https://servicodados.ibge.gov.br/api/v1/localidades` | `clients/localidades.py` |
| Agregados (SIDRA) | `/v3/agregados` | `https://servicodados.ibge.gov.br/api/v3/agregados` | `clients/agregados.py` |

Documentação oficial: <https://servicodados.ibge.gov.br/api/docs>.

## Formato do envelope de resposta

Toda tool retorna um objeto JSON com o mesmo formato, em sucesso ou erro:
`{"ok": ..., "data": ..., "metadata": {...}, "warnings": [...], "errors": [...]}`
(ver `mcp_ibge.schemas.common.ToolResponse`).

### Sucesso

```json
{
  "ok": true,
  "data": [
    { "id": 1, "sigla": "N", "nome": "Norte" }
  ],
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/regioes",
    "params": {},
    "retrieved_at": "2026-06-10T12:00:00Z",
    "period": null,
    "territorial_level": "N2",
    "license_note": "Dados públicos do IBGE (Instituto Brasileiro de Geografia e Estatística). Verifique a fonte oficial antes de uso em relatórios ou decisões.",
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [],
  "errors": []
}
```

### Erro

```json
{
  "ok": false,
  "data": null,
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/0000000",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/0000000",
    "params": { "municipio_id": 0 },
    "retrieved_at": "2026-06-10T12:00:00Z",
    "period": null,
    "territorial_level": "N6",
    "license_note": "Dados públicos do IBGE (Instituto Brasileiro de Geografia e Estatística). Verifique a fonte oficial antes de uso em relatórios ou decisões.",
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [],
  "errors": [
    {
      "message": "Erro HTTP 404 ao consultar https://servicodados.ibge.gov.br/api/v1/localidades/municipios/0000000",
      "code": null
    }
  ]
}
```

### Campos do envelope

| Campo | Descrição |
| --- | --- |
| `ok` | `true` se a consulta foi bem-sucedida, `false` caso contrário. |
| `data` | Dados retornados pela tool em caso de sucesso (lista, objeto ou `null`). Em caso de erro, normalmente `null`. |
| `metadata` | Metadados de proveniência da resposta (ver tabela abaixo). |
| `warnings` | Lista de avisos não fatais (`{"message": ..., "code": ...}`), preservados mesmo quando `ok` é `false`. |
| `errors` | Lista de erros (`{"message": ..., "code": ...}`), sem stack trace. Vazia quando `ok` é `true`. |

### Campos de `metadata`

| Campo | Descrição |
| --- | --- |
| `source_name` | Nome da fonte oficial dos dados (configurável via `MCP_IBGE_SOURCE_NAME`). |
| `source_url` | URL efetivamente consultada para obter os dados/erro. |
| `official_source` | URL institucional da fonte oficial (configurável via `MCP_IBGE_OFFICIAL_SOURCE_URL`), distinta do `endpoint` específico da consulta. |
| `endpoint` | URL do endpoint da API do IBGE utilizado. |
| `params` | Parâmetros usados na consulta (após resolução de aliases, filtros, etc.). |
| `retrieved_at` | Timestamp ISO 8601 (UTC, sufixo `Z`) do momento da consulta. |
| `period` | Período(s) de referência dos dados (ex.: `"2024"`, `"-1"`), ou `null` quando não se aplica. |
| `territorial_level` | Nível(is) territorial(is) (SIDRA/IBGE) dos dados, ex.: `"N6"` (município), ou `null` quando não se aplica. |
| `license_note` | Nota de licença/uso dos dados (configurável via `MCP_IBGE_LICENSE_NOTE`). |
| `version` | Versão do pacote `mcp-ibge` que gerou a resposta. |
| `cache_hit` | `true` se a resposta veio do cache em memória, `false` se foi obtida da API do IBGE. |

Esse formato garante que qualquer dado retornado por uma tool possa ser
**rastreado até a fonte oficial**, com data/hora da consulta e os parâmetros
exatos utilizados — importante para auditoria e para o usuário verificar a
informação na fonte original.

### Avisos (`warnings`)

As tools de Localidades que envolvem busca aproximada (ex.:
`buscar_municipio`, `obter_codigo_municipio`) podem incluir itens em
`warnings` na resposta de sucesso, sinalizando ambiguidades — por exemplo,
quando mais de um município corresponde ao nome buscado. Nesse caso, `data`
traz os candidatos encontrados e o aviso sugere refinar a busca (ex.,
informando `uf`).

## Cache

As respostas das APIs do IBGE são opcionalmente cacheadas em memória
(`utils/cache.py`, TTL configurável via `MCP_IBGE_CACHE_TTL_SECONDS`). O
cache é local ao processo, não persiste entre execuções e serve apenas para
evitar chamadas repetidas durante a mesma sessão.
