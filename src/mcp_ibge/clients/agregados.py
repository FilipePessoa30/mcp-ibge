"""Cliente "fino" para a API de Agregados (SIDRA) do IBGE (sem regras de negócio).

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/agregados

Conceitos principais:
    - "Agregado": uma tabela/pesquisa estatística (ex.: Censo, PNAD, estimativas
      populacionais), identificada por um ID numérico.
    - "Variável": uma grandeza medida dentro de um agregado (ex.: população,
      PIB), identificada por um ID numérico.
    - "Período": ano ou trimestre de referência dos dados (ex.: "2021",
      "2021-2022", ou "-1" para o período mais recente disponível).
    - "Localidade": unidade territorial consultada, no formato
      ``N<nivel>[<ids>]``, ex.: ``N1[all]`` (Brasil), ``N3[all]`` (todos os
      estados), ``N6[3550308]`` (município de São Paulo).

Filtros, aliases e regras de negócio ficam em
`mcp_ibge.services.agregados_service`.
"""

from __future__ import annotations

from typing import Any

from ..config import get_settings
from .base import BaseIBGEClient, IBGEResult


class AgregadosClient(BaseIBGEClient):
    """Cliente HTTP para `/agregados` (tabelas, metadados e dados do SIDRA)."""

    def __init__(self) -> None:
        super().__init__(get_settings().agregados_base_url)

    async def listar_agregados(
        self, pesquisa: str | None = None, assunto: str | None = None
    ) -> IBGEResult:
        """`GET /agregados` — lista de pesquisas e seus agregados (tabelas)."""
        params: dict[str, Any] = {}
        if pesquisa:
            params["pesquisa"] = pesquisa
        if assunto:
            params["assunto"] = assunto

        data = await self.get_json("", params=params or None)
        return IBGEResult(data=data, endpoint=self.base_url, params=params)

    async def obter_metadados(self, agregado_id: int) -> IBGEResult:
        """`GET /agregados/{id}/metadados` — variáveis, períodos e níveis territoriais."""
        path = f"/{agregado_id}/metadados"
        data = await self.get_json(path)
        return IBGEResult(
            data=data, endpoint=f"{self.base_url}{path}", params={"agregado_id": agregado_id}
        )

    async def consultar_dados(
        self,
        agregado_id: int,
        *,
        variaveis: str = "all",
        periodos: str = "-1",
        localidades: str = "N1[all]",
        classificacoes: str | None = None,
    ) -> IBGEResult:
        """`GET /agregados/{id}/periodos/{periodos}/variaveis/{variaveis}`."""
        path = f"/{agregado_id}/periodos/{periodos}/variaveis/{variaveis}"
        query: dict[str, Any] = {"localidades": localidades}
        if classificacoes:
            query["classificacao"] = classificacoes

        data = await self.get_json(path, params=query)

        params = {
            "agregado_id": agregado_id,
            "variaveis": variaveis,
            "periodos": periodos,
            **query,
        }
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params=params)
