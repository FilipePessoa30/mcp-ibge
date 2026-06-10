# Segurança

## Sem segredos

O `mcp-ibge` consulta exclusivamente APIs **públicas e sem autenticação** do
IBGE. Não há chaves de API, tokens ou credenciais de qualquer tipo — o
arquivo `.env.example` existe apenas para ajustar URLs, timeouts e cache, e
não deve conter segredos.

## Execução local, sem rede de entrada

- O transporte padrão é `stdio`: o servidor lê/escreve no `stdin`/`stdout`
  do processo que o invoca (ex.: Claude Desktop), sem abrir portas de rede.
- Logs vão sempre para `stderr` (`logging_config.py`), nunca para `stdout`,
  para não corromper o protocolo MCP.
- O transporte `streamable-http` (opcional, via `MCP_IBGE_TRANSPORT`) abre um
  servidor HTTP local; ao habilitá-lo, trate-o como qualquer outro serviço de
  rede (não exponha publicamente sem autenticação/proxy adequados).

## Saída de rede

O único tráfego de saída é HTTP(S) para a URL configurada em
`MCP_IBGE_API_BASE_URL` (por padrão, `servicodados.ibge.gov.br`). Cada
requisição tem timeout configurável (`MCP_IBGE_TIMEOUT`) para evitar
bloqueios indefinidos.

## Tratamento de erros

Erros de rede, timeouts, status HTTP de erro e respostas malformadas são
capturados em `clients/base.py` e convertidos em subclasses de
`IBGEClientError` (`IBGENotFoundError`, `IBGEValidationError`,
`IBGERateLimitError`, `IBGEServerError`). A camada `tools/` (`run_tool`)
converte qualquer exceção em um envelope de
erro estruturado (`{"metadata": ..., "error": ...}`), sem expor stack traces
ao cliente MCP nem derrubar o servidor.

## Dados de entrada

Os parâmetros recebidos das tools (códigos de município, siglas de UF, IDs
de agregado, etc.) são repassados como parâmetros de query/URL para as APIs
do IBGE via `httpx`, que cuida do *escaping* adequado — não há construção
manual de strings SQL, shell ou HTML a partir de entrada do usuário.

## Dependências

Dependências de produção são mínimas e amplamente utilizadas: `mcp`,
`httpx`, `pydantic`, `pydantic-settings`. Dependências de desenvolvimento
(`pytest`, `pytest-asyncio`, `respx`, `ruff`) não são incluídas na
instalação padrão (`uv pip install -e .`), apenas em `.[dev]`.
