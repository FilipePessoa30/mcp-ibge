"""Tools MCP do perfil básico de município (`gerar_perfil_municipal`)."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..services.perfil_service import PerfilService
from . import run_typed_tool

_service = PerfilService()


def register_perfil_tools(mcp: FastMCP) -> None:
    """Registra a tool de perfil municipal na instância FastMCP fornecida."""

    @mcp.tool()
    async def gerar_perfil_municipal(
        nome: Annotated[str, Field(description="Nome do município.")],
        uf: Annotated[str, Field(description='Sigla (ex.: "RJ") ou código IBGE da UF.')],
        ano: Annotated[
            int | None,
            Field(
                description=(
                    "Ano de referência para o indicador de população. Sem "
                    "este parâmetro, usa o período mais recente disponível "
                    "no SIDRA."
                )
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Gera um perfil básico de um município com dados oficiais do IBGE.

        Resolve o município por nome + UF e retorna:
        - `data.municipio`: identificação (código IBGE, UF, região e
          microrregião ou região intermediária);
        - `data.indicadores`: indicadores efetivamente obtidos do IBGE (por
          ora, população estimada, quando disponível) — nunca inventados;
        - `data.fontes`: endpoints da API do IBGE usados para montar o
          perfil;
        - `data.limitacoes`: limitações conhecidas dos dados retornados;
        - `data.proximos_indicadores_sugeridos`: nomes de indicadores ainda
          não implementados por este servidor (apenas sugestões, não dados).

        Se um indicador não puder ser obtido com segurança, a resposta inclui
        um aviso em `warnings` em vez de um valor estimado. Se o nome do
        município for ambíguo dentro da UF, ou nenhum município corresponder,
        a resposta tem `ok=False` (veja `warnings`/`errors` para os
        candidatos).
        """
        return await run_typed_tool(_service.gerar_perfil_municipal(nome, uf, ano=ano))
