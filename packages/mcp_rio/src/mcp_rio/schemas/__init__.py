"""Modelos Pydantic do mcp-rio e do envelope de resposta.

`common.py` define o envelope compartilhado `{"ok", "data", "metadata",
"warnings", "errors"}` (ver docs/data_sources.md), usado pela tool `status`.
Modelos específicos de dados (datasets, séries, indicadores, ...) serão
adicionados aqui conforme as tools planejadas em
`docs/modules/rio.md` forem implementadas, seguindo `mcp_ibge.schemas`.
"""
