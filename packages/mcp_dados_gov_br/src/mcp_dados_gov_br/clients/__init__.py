"""Clientes HTTP para as APIs/portais públicos de dados.gov.br - Portal Brasileiro de Dados Abertos
(planejado).

Camada fina de acesso às fontes oficiais, seguindo o mesmo padrão de
`mcp_ibge.clients`: timeouts, allowlist de domínios
(`mcp_dados_gov_br.config.ALLOWED_API_HOSTS`) e tratamento de erros sem stack trace para
o cliente MCP.

Nenhum cliente implementado ainda — ver "Fontes planejadas" em
`docs/modules/dados-gov-br.md`.
"""
