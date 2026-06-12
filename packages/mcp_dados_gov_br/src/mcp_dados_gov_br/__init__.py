"""mcp-dados-gov-br: servidor MCP para o Portal Brasileiro de Dados Abertos
(dados.gov.br): busca e detalhamento de datasets, organizações, grupos e tags
publicados por órgãos públicos brasileiros, via API CKAN.

Expõe 8 tools de dados (`buscar_datasets`, `obter_dataset`,
`listar_recursos_dataset`, `buscar_organizacoes`, `obter_organizacao`,
`listar_grupos`, `buscar_tags`, `sugerir_datasets_para_pergunta`) além da tool
`status` exigida para todo módulo do mcp-data-br. Veja
``docs/modules/dados-gov-br.md``.
"""

__version__ = "0.1.0"
