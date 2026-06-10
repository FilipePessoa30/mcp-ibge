"""Cliente "fino" para a API de Localidades do IBGE (sem regras de negócio).

Documentação oficial: https://servicodados.ibge.gov.br/api/docs/localidades

Cada método mapeia diretamente um endpoint da API. Filtros, buscas e
normalização ficam em `mcp_ibge.services.localidades_service`.
"""

from __future__ import annotations

from .base import AsyncIBGEClient, IBGEResult

LOCALIDADES_PATH = "/v1/localidades"


class LocalidadesClient(AsyncIBGEClient):
    """Cliente HTTP para `/localidades` (regiões, estados e municípios)."""

    def __init__(self) -> None:
        super().__init__(LOCALIDADES_PATH)

    async def listar_regioes(self) -> IBGEResult:
        """`GET /regioes` — as 5 grandes regiões geográficas do Brasil."""
        path = "/regioes"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={})

    async def listar_estados(self) -> IBGEResult:
        """`GET /estados` — os 26 estados e o Distrito Federal."""
        path = "/estados"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={})

    async def obter_estado(self, uf: str) -> IBGEResult:
        """`GET /estados/{uf}` — detalhes de um estado (sigla ou ID IBGE)."""
        path = f"/estados/{uf}"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={"uf": uf})

    async def listar_municipios(self, uf: str | None = None) -> IBGEResult:
        """`GET /municipios` ou `GET /estados/{uf}/municipios`."""
        if uf:
            path = f"/estados/{uf}/municipios"
            params: dict[str, str] = {"uf": uf}
        else:
            path = "/municipios"
            params = {}

        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params=params)

    async def obter_municipio(self, codigo: str) -> IBGEResult:
        """`GET /municipios/{codigo}` — detalhes de um município pelo código IBGE."""
        path = f"/municipios/{codigo}"
        data = await self.get_json(path)
        return IBGEResult(data=data, endpoint=f"{self.base_url}{path}", params={"codigo": codigo})
