"""Lógica de negócio: validação, filtragem e agregação de dados (planejado).

Seguindo `mcp_ibge.services`, esta camada é testável sem o protocolo MCP e
não conhece `FastMCP` — recebe parâmetros já validados de `mcp_dados_gov_br.tools` e
devolve dados tipados (`mcp_dados_gov_br.schemas`) usando `mcp_dados_gov_br.clients` e/ou datasets
derivados.

Nenhum serviço implementado ainda — ver "Fontes planejadas" e "Tools
planejadas" em `docs/modules/dados-gov-br.md`.
"""
