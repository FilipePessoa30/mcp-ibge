"""Servidor MCP `mcp-dados-gov-br`.

Expõe ferramentas de busca e detalhamento de datasets, organizações, grupos e
tags do Portal Brasileiro de Dados Abertos (dados.gov.br, API CKAN), seguindo
o padrão do `mcp-ibge` (`tools.<dominio>_tools.register_<dominio>_tools(mcp)`).

Execução:
    python -m mcp_dados_gov_br.server

Por padrão usa o transporte stdio. O transporte pode ser trocado via a
variável de ambiente `MCP_DADOS_GOV_BR_TRANSPORT` (ex.: "streamable-http"); host
e porta usados nesse modo são configuráveis via
`MCP_DADOS_GOV_BR_HOST`/`MCP_DADOS_GOV_BR_PORT`.

Importante: nunca usar `print()`. Em modo stdio, stdout é reservado para o
protocolo MCP — todo log vai para stderr via `logging`.
"""

from __future__ import annotations

import logging
import sys
from typing import Literal, cast

from mcp.server.fastmcp import FastMCP

from .config import get_settings
from .tools.catalogo_tools import register_catalogo_tools
from .tools.dataset_tools import register_dataset_tools
from .tools.organizacao_tools import register_organizacao_tools
from .tools.status_tools import register_status_tools

_settings = get_settings()

mcp = FastMCP(
    "mcp-dados-gov-br",
    instructions=(
        "Servidor MCP para o Portal Brasileiro de Dados Abertos (dados.gov.br, API "
        "CKAN): busca e detalhamento de datasets, organizações, grupos temáticos e "
        "tags publicados por órgãos públicos brasileiros. Use `buscar_datasets` ou "
        "`sugerir_datasets_para_pergunta` para descobrir datasets, `obter_dataset` "
        "e `listar_recursos_dataset` para detalhes e arquivos/links de um dataset "
        "específico, e `buscar_organizacoes`/`obter_organizacao` para informações "
        "sobre os órgãos publicadores. Algumas operações podem exigir um token de "
        "consumidor (`DADOS_GOV_BR_API_TOKEN`) — se não configurado, a tool retorna "
        "um erro explicando como configurá-lo."
    ),
    host=_settings.host,
    port=_settings.port,
)

register_status_tools(mcp)
register_dataset_tools(mcp)
register_organizacao_tools(mcp)
register_catalogo_tools(mcp)


def main() -> None:
    """Configura logging e inicia o servidor MCP."""
    logging.basicConfig(
        level=_settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        stream=sys.stderr,
    )
    logging.getLogger(__name__).info(
        "Iniciando mcp-dados-gov-br (transporte=%s)",
        _settings.transport,
    )
    transport = cast("Literal['stdio', 'sse', 'streamable-http']", _settings.transport)
    mcp.run(transport=transport)


if __name__ == "__main__":
    main()
