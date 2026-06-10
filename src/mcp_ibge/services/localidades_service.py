"""Regras de negócio do domínio de Localidades: filtros, busca e validação.

Esta camada usa `LocalidadesClient` para falar com a API do IBGE e os
modelos de `mcp_ibge.schemas.localidades` para validar/normalizar os dados
antes de devolvê-los às tools.
"""

from __future__ import annotations

from typing import Any

from ..clients.base import IBGEResult
from ..clients.localidades import LocalidadesClient
from ..schemas.localidades import Estado, Municipio
from ..utils.normalization import normalize_text


class LocalidadesService:
    """Operações de alto nível sobre regiões, estados e municípios."""

    def __init__(self, client: LocalidadesClient | None = None) -> None:
        self._client = client or LocalidadesClient()

    async def listar_regioes(self) -> IBGEResult:
        """Lista as 5 grandes regiões geográficas do Brasil."""
        return await self._client.listar_regioes()

    async def listar_estados(self, regiao: str | None = None) -> IBGEResult:
        """Lista estados, opcionalmente filtrados por sigla/ID de região."""
        result = await self._client.listar_estados()
        estados = [Estado.model_validate(item) for item in result.data]

        params: dict[str, Any] = {}
        if regiao:
            regiao_norm = regiao.strip().upper()
            estados = [
                estado
                for estado in estados
                if estado.regiao is not None
                and (
                    (estado.regiao.sigla or "").upper() == regiao_norm
                    or str(estado.regiao.id) == regiao_norm
                )
            ]
            params["regiao"] = regiao

        data = [estado.model_dump(mode="json") for estado in estados]
        return IBGEResult(data=data, endpoint=result.endpoint, params=params)

    async def obter_estado(self, uf: str) -> IBGEResult:
        """Obtém os detalhes de um estado por sigla (ex.: "SP") ou ID IBGE."""
        return await self._client.obter_estado(uf)

    async def listar_municipios(self, uf: str | None = None) -> IBGEResult:
        """Lista municípios, opcionalmente filtrados por estado."""
        return await self._client.listar_municipios(uf=uf)

    async def obter_municipio(self, codigo: str) -> IBGEResult:
        """Obtém os detalhes completos de um município pelo código IBGE."""
        return await self._client.obter_municipio(codigo)

    async def buscar_municipios_por_nome(
        self, nome: str, uf: str | None = None, limit: int = 20
    ) -> IBGEResult:
        """Busca municípios cujo nome contenha o termo informado.

        A busca ignora maiúsculas/minúsculas e acentos (ex.: "sao jose"
        encontra "São José dos Campos").
        """
        result = await self._client.listar_municipios(uf=uf)
        municipios = [Municipio.model_validate(item) for item in result.data]

        termo = normalize_text(nome)
        encontrados = [m for m in municipios if termo in normalize_text(m.nome)]
        encontrados = encontrados[: max(limit, 0)]

        params: dict[str, Any] = {"nome": nome, "limit": limit}
        if uf:
            params["uf"] = uf

        data = [m.model_dump(mode="json") for m in encontrados]
        return IBGEResult(data=data, endpoint=result.endpoint, params=params)
