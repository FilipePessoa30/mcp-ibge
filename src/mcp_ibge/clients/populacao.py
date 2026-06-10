"""Indicadores de população: estimativas municipais e projeções.

Combina a API de Agregados (SIDRA) com a API de Projeções da População do
IBGE. Documentação:
    - SIDRA: https://servicodados.ibge.gov.br/api/docs/agregados
    - Projeções: https://servicodados.ibge.gov.br/api/docs/projecoes
"""

from __future__ import annotations

from ..config import AGREGADOS_BASE_URL, PROJECOES_BASE_URL
from ..http_client import get_json
from .base import IBGEResult

# Agregado 6579 = "População residente estimada"; variável 9324 = "População residente estimada".
AGREGADO_POPULACAO_ESTIMADA = 6579
VARIAVEL_POPULACAO_ESTIMADA = 9324


async def obter_populacao_municipio(codigo_municipio: str) -> IBGEResult:
    """Obtém a população residente estimada mais recente de um município.

    Usa o agregado 6579 (Estimativas de população) do SIDRA, variável 9324,
    para o período mais recente disponível (-1).

    Args:
        codigo_municipio: Código IBGE do município (7 dígitos), ex.:
            "3550308" para São Paulo/SP.
    """
    endpoint = (
        f"{AGREGADOS_BASE_URL}/{AGREGADO_POPULACAO_ESTIMADA}"
        f"/periodos/-1/variaveis/{VARIAVEL_POPULACAO_ESTIMADA}"
    )
    query = {"localidades": f"N6[{codigo_municipio}]"}
    data = await get_json(endpoint, params=query)

    request_params = {"codigo_municipio": codigo_municipio, **query}
    return IBGEResult(data=data, endpoint=endpoint, params=request_params)


async def obter_projecao_populacao(localidade: str = "BR") -> IBGEResult:
    """Obtém a projeção populacional do IBGE para o Brasil ou uma UF.

    Args:
        localidade: "BR" para o Brasil, ou o código IBGE de 2 dígitos de uma
            unidade federativa (ex.: "35" para São Paulo).
    """
    endpoint = f"{PROJECOES_BASE_URL}/populacao/{localidade}"
    data = await get_json(endpoint)
    return IBGEResult(data=data, endpoint=endpoint, params={"localidade": localidade})
