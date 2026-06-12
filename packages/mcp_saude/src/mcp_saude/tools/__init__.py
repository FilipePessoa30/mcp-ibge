"""Registro das *tools* MCP do mcp-saude.

Cada arquivo deste pacote expõe uma função `register_<dominio>_tools(mcp:
FastMCP)` chamada por `mcp_saude.server`, seguindo `mcp_ibge.tools`. Hoje só
`status_tools.register_status_tools` está registrada (tool `status`, exigida
para todo módulo do mcp-data-br) — as tools de dados planejadas estão em
`docs/modules/saude.md`.
"""
