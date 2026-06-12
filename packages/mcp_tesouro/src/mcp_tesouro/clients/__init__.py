"""Clientes HTTP para as APIs/portais públicos de Tesouro Nacional - Tesouro Transparente
(planejado).

Camada fina de acesso às fontes oficiais, seguindo o mesmo padrão de
`mcp_ibge.clients`: timeouts, allowlist de domínios
(`mcp_tesouro.config.ALLOWED_API_HOSTS`) e tratamento de erros sem stack trace para
o cliente MCP.

Nenhum cliente implementado ainda — ver "Fontes planejadas" em
`docs/modules/tesouro.md`.
"""
