# Segurança

Este documento descreve o modelo de ameaças e as proteções implementadas no
`mcp-ibge`, organizadas pelos pontos obrigatórios de segurança/robustez do
projeto. O servidor consulta exclusivamente APIs **públicas e sem
autenticação** do IBGE — não há segredos, chaves de API ou dados de usuários
persistidos.

## 1. Sem execução de comandos shell

O servidor **não executa comandos de shell** em nenhum momento: não há uso de
`subprocess`, `os.system`, `os.popen`, `shell=True` ou similares em
`src/mcp_ibge/`. Toda a lógica é Python puro + chamadas HTTP via `httpx`. Os
parâmetros recebidos das tools (UF, código de município, ID de agregado etc.)
nunca são interpolados em comandos de sistema.

## 2. Sem acesso a arquivos locais do usuário

O servidor **não lê nem escreve arquivos do usuário** em tempo de execução:
não há chamadas a `open()` (ou equivalentes) sobre caminhos fornecidos por
tools/clientes. A única leitura de arquivo acontece na inicialização do
processo, via `pydantic-settings`, que opcionalmente carrega um `.env` local
(apenas configuração — URLs, timeouts, cache; nunca dados de usuário ou
caminhos arbitrários).

## 3. Sem aceitar URLs arbitrárias

Nenhuma tool aceita uma URL completa como parâmetro. Os parâmetros de entrada
são sempre identificadores estruturados (sigla de UF, código IBGE de
município, ID de agregado, variáveis, períodos, níveis territoriais, nomes
para busca etc.), validados pelo módulo `mcp_ibge.utils.validators` (ver §5) e então
embutidos em *templates* de path fixos dentro de `clients/localidades.py` e
`clients/agregados.py` (ex.: `f"/municipios/{codigo}"`,
`f"/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}"`). Não existe
nenhum caminho de código em que uma string fornecida pelo usuário/agente vire
diretamente a URL de destino de uma requisição.

Como segunda camada (em profundidade), `AsyncIBGEClient.get_json` chama
`mcp_ibge.security.assert_allowed_url(url)` imediatamente antes de qualquer
requisição — ver §4 e §12.

## 4. Domínios oficiais do IBGE (allowlist)

Toda saída de rede é HTTP(S) para `Settings.api_base_url`
(`MCP_IBGE_API_BASE_URL`, padrão `https://servicodados.ibge.gov.br/api`).
Esse valor é validado na inicialização (`config.Settings._validar_api_base_url`,
via `pydantic.field_validator`):

- o esquema **deve ser `https`**;
- o host **deve estar** na allowlist `config.ALLOWED_API_HOSTS`, atualmente
  `{"servicodados.ibge.gov.br"}`.

Qualquer outro valor (`http://...`, outro domínio, IP, `localhost`, domínios
parecidos como `servicodados.ibge.gov.br.evil.com`, URL malformada) faz a
inicialização do servidor falhar com um erro de validação — o servidor nunca
chega a rodar com um destino de rede não confiável. `AsyncIBGEClient` deriva
`base_url` sempre a partir desse valor já validado
(`settings.api_base_url.rstrip('/') + base_path`), então **toda** requisição
de qualquer cliente vai para o mesmo domínio oficial.

Além dessa validação na inicialização, `mcp_ibge.security.ALLOWED_HOSTS`
reexporta `config.ALLOWED_API_HOSTS` e `assert_allowed_url(url)` repete a
mesma checagem (esquema `https` + host na allowlist) **a cada requisição**,
em `AsyncIBGEClient.get_json` — ver §12.

## 5. Validação de entrada (UF, município, agregado, variável, período, nível, limite)

O módulo [`mcp_ibge/utils/validators.py`](../src/mcp_ibge/utils/validators.py)
centraliza a validação de formato dos parâmetros das tools, **antes** de
qualquer requisição de rede. Em caso de formato inválido, levanta
`IBGEValidationError` (HTTP 422, exceção customizada definida em
`utils/errors.py`), sem chamar a API do IBGE, com mensagens claras que nunca
expõem stack trace:

| Função | Valida | Exemplos válidos | Exemplos inválidos |
| --- | --- | --- | --- |
| `validate_uf(uf_or_id)` | Sigla de UF (2 letras) ou código IBGE (2 dígitos) de uma UF/DF existente. | `"RJ"`, `"rj"`, `"33"` | `"XX"`, `"99"`, `""` |
| `validate_municipality_code(codigo)` | Código IBGE de município: inteiro de exatamente 7 dígitos. | `3550308`, `"3303302"` | `"123"`, `"12345678"`, `"abc"` |
| `validate_agregado_id(agregado_id)` | ID de agregado SIDRA: inteiro positivo. | `"6579"`, `"1419"` | `""`, `"  "`, `"abc"`, `"-6579"` |
| `validate_variaveis(variaveis)` | Variável(is) SIDRA: `"all"` ou IDs numéricos separados por `\|`. | `"all"`, `"93"`, `"93\|1000093"` | `""`, `"abc"`, `"93,1000093"`, `"-93"` |
| `validate_periodos(periodos)` | Expressão de períodos SIDRA: `"all"`, ano/ano-mês, intervalo, relativo (`-N`), ou lista separada por `,` ou `\|`. | `"-1"`, `"-6"`, `"2021"`, `"2010-2020"`, `"all"`, `"2010,2015-2020,-1"`, `"2020\|2021\|2022"` | `""`, `"abc"`, `"2021;2022"`, `"ALL"` |
| `validate_niveis(niveis)` | Nível(is) territorial(is) SIDRA: `"N<dígitos>"`, opcionalmente com composição `"[<ids>]"` (ex.: `"N3[33]"`), `\|`-separados. | `"N6"`, `"N1\|N3"`, `"N3[33]"`, `"N3[33,35]"` | `""`, `"6"`, `"n6"`, `"N1,N3"`, `"N3[<script>]"` |
| `validate_limit(limit)` | Limite de itens retornados: inteiro entre 1 e 100. | `1`, `10`, `100` | `0`, `101`, `-1`, `"10"`, `1.5` |

Essas funções são usadas pelos clients e services (`clients/localidades.py`,
`clients/agregados.py`, `services/localidades_service.py`):

- `LocalidadesClient.get_estado` / `get_municipios_by_uf` →
  `validate_uf`;
- `LocalidadesClient.get_municipio` / `get_distritos_by_municipio` →
  `validate_municipality_code`;
- `AgregadosClient.get_agregado_metadata` / `get_agregado_periodos` /
  `get_agregado_variaveis` / `get_agregado_localidades` / `query_agregado` →
  `validate_agregado_id`;
- `AgregadosClient.get_agregado_localidades` → `validate_niveis`;
- `AgregadosClient.query_agregado` → `validate_variaveis` e
  `validate_periodos` (e checagem de não-vazio para `localidades`, que é
  repassado como parâmetro de query e não compõe o path);
- `LocalidadesService.buscar_municipio` → `validate_limit` (camada adicional
  além do `Field(ge=1, le=50)` já aplicado pela tool).

O **SIDRA Query Builder** (`sidra_service.SidraService`) reutiliza as mesmas
funções: `buscar_tabelas_sidra` → `validate_limit`;
`validar_consulta_sidra`/`executar_consulta_sidra_validada` →
`validate_agregado_id`, `validate_variaveis`, `validate_niveis` e
`validate_periodos`, antes de consultar os metadados do agregado. Além da
validação de formato, `validar_consulta_sidra` faz uma segunda validação,
puramente local (sem rede), contra os metadados já obtidos do agregado
(`sidra/query_builder.validar_consulta`) — `executar_consulta_sidra_validada`
só chama a API de dados (`consultar_agregado`) se essa validação passar.

Testes de formato válido e inválido para as sete funções estão em
[`tests/test_validators.py`](../tests/test_validators.py).

## 6. Timeout

Toda requisição HTTP usa o timeout configurável `Settings.timeout`
(`MCP_IBGE_TIMEOUT`, padrão `30.0` segundos), aplicado em
`AsyncIBGEClient.get_json` via `httpx.AsyncClient(timeout=settings.timeout, ...)`.
Um timeout é convertido em `IBGEClientError` (sem stack trace exposta — ver
§10), evitando que uma chamada à tool fique bloqueada indefinidamente.

## 7. Limite de tamanho de resposta

`AsyncIBGEClient.get_json` consome a resposta da API do IBGE em streaming
(`client.stream("GET", ...)` + `aiter_bytes()`) e, após cada chunk, chama
`mcp_ibge.security.response_size_guard(len(body), max_size=..., url=url)`
(ver §12), que levanta `ResponseTooLargeError` assim que o corpo acumulado
excede `Settings.max_response_size_bytes`
(`MCP_IBGE_MAX_RESPONSE_SIZE_BYTES`, padrão `5_000_000` bytes / ~5 MB).
`get_json` converte essa exceção em `IBGEServerError`. Isso evita que uma
resposta inesperadamente grande (ou uma API comprometida) consuma memória do
processo de forma descontrolada antes do `json.loads`.

## 8. Cache

Um cache em memória com TTL (`utils/cache.py`, `get_cache()`) evita chamadas
repetidas à API do IBGE para a mesma URL + parâmetros, controlado por:

- `MCP_IBGE_CACHE_ENABLED` (padrão `true`);
- `MCP_IBGE_CACHE_TTL_SECONDS` (padrão `3600.0`);
- `MCP_IBGE_CACHE_MAX_SIZE` (padrão `256` entradas, com remoção LRU).

Apenas respostas de sucesso (`200`, JSON já decodificado) são cacheadas; o
cache vive apenas em memória do processo (nunca em disco) e é descartado ao
encerrar o servidor.

## 9. Logs sem dados sensíveis

O `mcp-ibge` não lida com segredos, tokens ou dados pessoais — apenas
identificadores públicos (códigos IBGE, siglas de UF, IDs de agregado/variável,
nomes de municípios para busca). Os logs (`logging_config.py`,
`clients/base.py`) registram no nível `DEBUG` apenas a URL consultada e os
parâmetros de query (todos derivados de identificadores públicos do IBGE, sem
PII). Não há logging de corpos de resposta completos nem de variáveis de
ambiente. O nível de log é configurável via `MCP_IBGE_LOG_LEVEL` (padrão
`INFO`); em produção, `INFO` evita até esse nível de detalhe de parâmetros.

## 10. Tratamento de erros sem vazar stack trace

Erros de rede, timeouts, status HTTP de erro, respostas malformadas e
respostas acima do limite de tamanho são capturados em `clients/base.py` e
convertidos em subclasses de `IBGEClientError` (`IBGENotFoundError`,
`IBGEValidationError`, `IBGERateLimitError`, `IBGEServerError`), com mensagens
descritivas mas sem dados internos sensíveis (stack trace, variáveis locais,
caminhos do sistema de arquivos).

A camada `tools/` (`run_typed_tool` em `tools/__init__.py`) captura **qualquer**
exceção e converte para o envelope padrão com `ok=False`
(`{"ok": false, "data": null, "metadata": {...}, "warnings": [...], "errors": [{"message": "<mensagem>", "code": null}]}`):

- a mensagem em `errors[0].message` retornada ao cliente MCP é montada com
  `mcp_ibge.security.safe_error_response(exc)` (ver §12), que usa apenas
  `str(exc)` (ou o nome da classe da exceção, se a mensagem for vazia) — nunca
  o traceback, caminhos do sistema de arquivos ou `repr()` de objetos internos;
- o traceback completo é registrado via `logger.exception(...)`, que vai para
  `stderr` (ver §11) — útil para depuração local, mas não chega ao cliente MCP;
- o servidor nunca derruba (não há exceção não tratada que propague até
  `mcp.run()`).

## 11. Logs sempre em `stderr`, nunca em `stdout` (stdio)

`logging_config.configure_logging()` chama
`logging.basicConfig(stream=sys.stderr, force=True)`: **todo** log do processo
vai para `stderr`. O código da aplicação nunca usa `print()` (ver comentário em
`server.py`). Isso é essencial no transporte padrão `stdio`, onde `stdout` é
reservado exclusivamente para mensagens do protocolo MCP — qualquer escrita
acidental em `stdout` corromperia a comunicação com o cliente MCP (ex.: Claude
Desktop).

## 12. Módulo central `mcp_ibge.security`

[`mcp_ibge/security.py`](../src/mcp_ibge/security.py) centraliza, em um único
módulo, as primitivas de segurança reutilizadas pelos clients HTTP
(`clients/base.py`) e pela camada de tools (`tools/__init__.py`):

| Nome | Usado em | Faz |
| --- | --- | --- |
| `ALLOWED_HOSTS` | `is_allowed_url`, `assert_allowed_url` | Reexporta `config.ALLOWED_API_HOSTS` (`{"servicodados.ibge.gov.br"}`) sob um nome mais descritivo. |
| `is_allowed_url(url)` | `assert_allowed_url` | Retorna `True` apenas se `url` for `https` para um host em `ALLOWED_HOSTS`; qualquer outro esquema, host fora da allowlist (incluindo domínios "parecidos", ex.: `servicodados.ibge.gov.br.evil.com`) ou URL malformada retorna `False`. |
| `assert_allowed_url(url)` | `AsyncIBGEClient.get_json` | Levanta `URLNotAllowedError` se `is_allowed_url(url)` for `False` — chamado antes de toda requisição (§3, §4). |
| `response_size_guard(current_size, *, max_size=None, url="")` | `AsyncIBGEClient.get_json` | Levanta `ResponseTooLargeError` se `current_size` exceder `max_size` (ou `Settings.max_response_size_bytes`, se omitido) — chamado a cada chunk recebido (§7). |
| `safe_error_response(exc)` | `run_typed_tool` | Converte `exc` em `str(exc)` (ou `type(exc).__name__`, se vazio) — nunca um traceback (§10). |

`URLNotAllowedError` e `ResponseTooLargeError` (subclasses de `SecurityError`)
são capturadas em `AsyncIBGEClient.get_json` e reconvertidas para
`IBGEClientError`/`IBGEServerError` respectivamente, preservando o contrato de
exceções já documentado em §10 — nenhum código que consome `AsyncIBGEClient`
precisa conhecer `mcp_ibge.security` diretamente.

Testes em [`tests/test_security.py`](../tests/test_security.py) cobrem:
allowlist de domínios (URLs permitidas, http/ftp/file, domínios fora da
allowlist e domínios "parecidos"), o bloqueio de uma requisição cuja URL não
está na allowlist antes de qualquer chamada HTTP (via `respx`, verificando que
a rota mockada nunca é chamada), o limite de tamanho de resposta (no nível da
função e via `AsyncIBGEClient`), `safe_error_response` (sem traceback) e
entradas maliciosas (SQL injection, `<script>`, *path traversal*) para todos
os validadores de §5.

## Outros pontos

### Execução local, sem rede de entrada

- O transporte padrão é `stdio`: o servidor lê/escreve no `stdin`/`stdout` do
  processo que o invoca, sem abrir portas de rede.
- O transporte `streamable-http` (opcional, via `MCP_IBGE_TRANSPORT`) abre um
  servidor HTTP local; ao habilitá-lo, trate-o como qualquer outro serviço de
  rede (não exponha publicamente sem autenticação/proxy adequados).

### Sem segredos

Não há chaves de API, tokens ou credenciais de qualquer tipo — o arquivo
`.env.example` existe apenas para ajustar URLs, timeouts, cache e o limite de
tamanho de resposta, e não deve conter segredos.

### Dependências

Dependências de produção são mínimas e amplamente utilizadas: `mcp`, `httpx`,
`pydantic`, `pydantic-settings`. Dependências de desenvolvimento (`pytest`,
`pytest-asyncio`, `respx`, `ruff`, `mypy`) não são incluídas na instalação
padrão (`uv pip install -e .`), apenas em `.[dev]`.

### Escaping de parâmetros

Os parâmetros validados (códigos de município, siglas de UF, IDs de agregado
etc.) são repassados como parâmetros de query/path para as APIs do IBGE via
`httpx`, que cuida do *escaping* adequado — não há construção manual de
strings SQL, shell ou HTML a partir de entrada do usuário.
