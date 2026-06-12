"""Lógica de negócio: validação, filtragem e agregação de dados (planejado).

Seguindo `mcp_ibge.services`, esta camada é testável sem o protocolo MCP e
não conhece `FastMCP` — recebe parâmetros já validados de `mcp_bcb.tools` e
devolve dados tipados (`mcp_bcb.schemas`) usando `mcp_bcb.clients` e/ou datasets
derivados.

Nenhum serviço implementado ainda — ver "Fontes planejadas" e "Tools
planejadas" em `docs/modules/bcb.md`.
"""
