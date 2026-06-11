# Configuração em clientes MCP

Este guia mostra como configurar o `mcp-ibge` em clientes MCP (Claude
Desktop, Cursor) e traz perguntas de teste para validar a integração.

Arquivos de exemplo prontos:

- [examples/claude_desktop/mcp_ibge.json](../../../examples/claude_desktop/mcp_ibge.json)
- [examples/cursor/mcp_ibge.json](../../../examples/cursor/mcp_ibge.json)

Todas as configurações usam o transporte `stdio` (padrão do servidor) — o
cliente inicia o processo do servidor e se comunica via stdin/stdout, sem
abrir portas de rede.

## 1. Claude Desktop (Linux/macOS)

Edite `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) ou `~/.config/Claude/claude_desktop_config.json` (Linux) e adicione:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "uvx",
      "args": ["mcp-ibge"]
    }
  }
}
```

`uvx` baixa e executa o pacote `mcp-ibge` isoladamente (sem precisar
clonar o repositório), desde que ele esteja publicado em um índice acessível
(ex.: PyPI). Enquanto o pacote não estiver publicado, use a
[alternativa local de desenvolvimento](#3-alternativa-local-durante-o-desenvolvimento).

## 2. Claude Desktop (Windows)

Edite `%APPDATA%\Claude\claude_desktop_config.json`. No Windows, comandos
como `uvx` costumam precisar ser invocados através do `cmd /c` para que o
Claude Desktop encontre o executável corretamente:

```json
{
  "mcpServers": {
    "ibge": {
      "command": "cmd",
      "args": ["/c", "uvx", "mcp-ibge"]
    }
  }
}
```

Se `uvx`/`uv` não estiverem no `PATH` do processo do Claude Desktop, use o
caminho absoluto do executável (ex.:
`"C:\\Users\\<usuario>\\.local\\bin\\uv.exe"` como `command`, com
`args: ["run", ...]` em vez de `cmd /c uvx ...`).

## 3. Alternativa local durante o desenvolvimento

Para rodar a partir do código-fonte (sem publicar o pacote), aponte `uv` para
o diretório do projeto e execute o módulo do servidor diretamente:

```json
{
  "mcpServers": {
    "ibge-dev": {
      "command": "uv",
      "args": ["run", "python", "-m", "mcp_ibge.server"]
    }
  }
}
```

Esse comando precisa ser executado **a partir da raiz do repositório**
`mcp-data-br` (onde está o `pyproject.toml` do workspace — `mcp-ibge` é
instalado como membro do workspace). Como a maioria dos clientes MCP não
permite configurar o diretório de trabalho, adicione `--directory` com o
caminho absoluto do repositório antes de `run` — é o que faz
[examples/claude_desktop/mcp_ibge.json](../../../examples/claude_desktop/mcp_ibge.json)
(entrada `ibge-dev`):

```json
{
  "mcpServers": {
    "ibge-dev": {
      "command": "uv",
      "args": [
        "--directory",
        "/caminho/absoluto/para/mcp-data-br",
        "run",
        "python",
        "-m",
        "mcp_ibge.server"
      ]
    }
  }
}
```

No Windows, use o caminho absoluto com barras duplas ou simples, ex.:
`"C:\\caminho\\para\\mcp-data-br"` ou `"C:/caminho/para/mcp-data-br"`.

## Cursor

Em `Settings -> MCP -> Add new MCP Server`, ou editando `~/.cursor/mcp.json`,
use o mesmo formato `mcpServers` — veja
[examples/cursor/mcp_ibge.json](../../../examples/cursor/mcp_ibge.json) para
as variantes Linux/macOS, Windows (`cmd /c`) e desenvolvimento local
(`uv --directory ... run mcp-ibge`).

## Reiniciar o cliente

Após editar o arquivo de configuração, reinicie o Claude Desktop (ou recarregue
a janela do Cursor) para que o servidor seja iniciado e as tools fiquem
disponíveis na conversa.

## Perguntas de teste

Use estas perguntas em linguagem natural para validar a configuração — veja
[examples/agent_recipes/mcp_ibge_queries.md](../../../examples/agent_recipes/mcp_ibge_queries.md)
para os argumentos equivalentes de cada tool e mais exemplos:

1. "Liste os estados brasileiros."
2. "Qual é o código IBGE de Niterói, RJ?"
3. "Liste os municípios do Rio de Janeiro."
4. "Busque municípios chamados São José."
5. "Consulte os metadados de um agregado do SIDRA (ex.: o agregado 6579)."
6. "Liste as variáveis de um agregado do SIDRA (ex.: o agregado 6579)."
7. "Compare a população do Rio de Janeiro e de Niterói."

A última pergunta também pode ser feita diretamente como o prompt MCP
`comparar_municipios`, que orienta o modelo a citar fonte, ano, unidade
territorial e limitações na resposta.

## Limitações

- **Dependência da API oficial do IBGE**: todos os dados vêm em tempo real de
  `servicodados.ibge.gov.br` (sem chave de API). Indisponibilidade,
  instabilidade ou mudanças nessa API afetam diretamente as respostas do
  servidor — veja [docs/data_sources.md](data_sources.md).
- **Agregados do SIDRA exigem contexto**: `consultar_agregado` espelha a
  sintaxe do SIDRA (tabela/agregado, variável, localidades, períodos e,
  opcionalmente, classificações). Para tabelas que você não conhece, use
  primeiro `listar_agregados`, `obter_metadados_agregado`,
  `listar_variaveis_agregado`, `listar_periodos_agregado` e
  `listar_localidades_agregado` para descobrir os IDs corretos antes de
  consultar os dados.
- **Verifique antes de usar oficialmente**: as respostas incluem `metadata`
  (fonte, endpoint, parâmetros e data/hora da consulta) e, quando aplicável,
  `warnings` sobre ambiguidades ou incertezas metodológicas (ex.: dado
  ausente/sigiloso, período retornado quando nenhum foi pedido). Use esses
  campos para conferir os números na fonte oficial antes de utilizá-los em
  relatórios, decisões ou qualquer uso oficial.
