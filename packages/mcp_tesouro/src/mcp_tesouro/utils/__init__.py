"""Utilitários transversais: cache, normalização, erros (planejado).

Seguindo `mcp_ibge.utils`, este pacote concentra helpers compartilhados entre
`clients`, `services` e `tools` — por exemplo, um cache em memória com TTL
(`mcp_ibge.utils.cache`) e tratamento de erros sem stack trace
(`mcp_ibge.security.safe_error_response`).

Nada implementado ainda; ao adicionar `mcp_tesouro.clients`/`mcp_tesouro.services`,
reaproveitar os utilitários de `mcp_ibge.utils` quando possível em vez de
duplicar a lógica.
"""
