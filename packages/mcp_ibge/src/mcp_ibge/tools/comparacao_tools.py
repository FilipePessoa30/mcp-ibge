"""Tool MCP de comparação de municípios (`comparar_municipios`)."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.fastmcp import FastMCP
from pydantic import Field

from ..schemas.comparacao import MunicipioConsulta
from ..services.comparacao_service import MAX_MUNICIPIOS, ComparacaoService
from . import run_typed_tool

_service = ComparacaoService()

_MUNICIPIOS_DESCRIPTION = (
    "Municípios a comparar, cada um com `nome` e `uf` (sigla ou código IBGE "
    'da UF), ex.: `[{"nome": "Rio de Janeiro", "uf": "RJ"}, '
    '{"nome": "Niterói", "uf": "RJ"}]`. '
    f"Máximo de {MAX_MUNICIPIOS} municípios por chamada."
)

_INDICADORES_DESCRIPTION = (
    'Nomes dos indicadores a comparar (ex.: `["populacao"]`). Sem este '
    "parâmetro, usa os indicadores básicos disponíveis (atualmente, apenas "
    "população residente estimada). Indicadores não implementados são "
    "ignorados com um aviso em `warnings`, sem interromper a comparação."
)


def register_comparacao_tools(mcp: FastMCP) -> None:
    """Registra a tool de comparação de municípios na instância FastMCP fornecida."""

    @mcp.tool()
    async def comparar_municipios(
        municipios: Annotated[list[MunicipioConsulta], Field(description=_MUNICIPIOS_DESCRIPTION)],
        indicadores: Annotated[
            list[str] | None, Field(description=_INDICADORES_DESCRIPTION)
        ] = None,
        ano: Annotated[
            int | None,
            Field(
                description=(
                    "Ano de referência para os indicadores. Sem este "
                    "parâmetro, usa o período mais recente disponível no "
                    "SIDRA para cada município."
                )
            ),
        ] = None,
    ) -> dict[str, Any]:
        """Compara municípios com base em indicadores oficiais do IBGE.

        Resolve cada município por `nome`/`uf` e monta uma tabela pronta para
        apresentação:
        - `data.municipios`: municípios resolvidos, cada um com `codigo_ibge`,
          UF, região e `indicadores` (dados efetivamente obtidos do IBGE,
          nunca inventados);
        - `data.municipios_nao_resolvidos`: municípios não encontrados ou
          ambíguos, com o `motivo`;
        - `data.indicadores_consultados` / `data.indicadores_nao_implementados`:
          quais indicadores foram efetivamente consultados e quais foram
          ignorados (apenas nomes, não dados);
        - `data.fontes`: endpoints da API do IBGE usados na comparação;
        - `data.limitacoes`: limitações conhecidas dos dados retornados.

        Indicadores não reconhecidos geram um aviso em `warnings` e não
        impedem a comparação dos demais. Se nenhum município puder ser
        resolvido, a resposta tem `ok=False`.
        """
        return await run_typed_tool(
            _service.comparar_municipios(municipios, indicadores=indicadores, ano=ano)
        )
