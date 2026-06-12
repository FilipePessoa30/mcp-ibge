"""CLI `mcp-data-br`: testa as tools de `mcp-ibge` pela linha de comando.

Permite consultar os mesmos dados expostos pelas tools MCP sem precisar
configurar Claude Desktop, Cursor ou outro cliente MCP. Cada subcomando
chama a mesma camada de serviço usada pelas tools (`services/*`) e imprime
em stdout o envelope padrão `{ok, data, metadata, warnings, errors}` como
JSON — nenhuma lógica de consulta é duplicada aqui.

Exemplos:
    mcp-data-br ibge estados
    mcp-data-br ibge municipios --uf RJ
    mcp-data-br ibge codigo-municipio "Niterói" --uf RJ
    mcp-data-br ibge buscar-municipio "São José"
    mcp-data-br sidra metadados --agregado 6579
    mcp-data-br status
"""

from __future__ import annotations

import asyncio
import json
import os
from collections.abc import Awaitable, Callable, Iterator
from contextlib import contextmanager
from typing import Annotated, Any

import typer

from .config import get_settings
from .schemas.common import TypedToolResult
from .services.agregados_service import AgregadosService
from .services.localidades_service import LocalidadesService
from .tools import run_typed_tool

app = typer.Typer(
    name="mcp-data-br",
    help="CLI para testar as tools de mcp-data-br sem configurar um cliente MCP.",
    no_args_is_help=True,
)

ibge_app = typer.Typer(
    help="Tools de Localidades do IBGE (estados, municípios, ...).",
    no_args_is_help=True,
)
sidra_app = typer.Typer(
    help="Tools do SIDRA (metadados de agregados, ...).",
    no_args_is_help=True,
)
app.add_typer(ibge_app, name="ibge")
app.add_typer(sidra_app, name="sidra")

PrettyOption = Annotated[
    bool, typer.Option("--pretty", help="Formata a saída JSON com indentação.")
]
NoCacheOption = Annotated[
    bool, typer.Option("--no-cache", help="Ignora o cache em memória para esta chamada.")
]

# Variável de ambiente compartilhada que controla o cache em memória (ver
# `mcp_ibge.config.Settings.cache_enabled`); tem precedência sobre
# `MCP_IBGE_CACHE_ENABLED`.
_CACHE_ENV_VAR = "MCP_DATA_BR_ENABLE_CACHE"


@contextmanager
def _cache_override(*, no_cache: bool) -> Iterator[None]:
    """Desabilita temporariamente o cache em memória quando `no_cache=True`.

    `get_settings()` é `lru_cache`d, então alteramos a variável de ambiente
    e limpamos esse cache antes/depois da chamada, sem afetar outros
    processos nem deixar o estado vazar entre comandos.
    """
    if not no_cache:
        yield
        return

    previous = os.environ.get(_CACHE_ENV_VAR)
    os.environ[_CACHE_ENV_VAR] = "false"
    get_settings.cache_clear()
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(_CACHE_ENV_VAR, None)
        else:
            os.environ[_CACHE_ENV_VAR] = previous
        get_settings.cache_clear()


def _print_json(payload: dict[str, Any], *, pretty: bool) -> None:
    indent = 2 if pretty else None
    typer.echo(json.dumps(payload, indent=indent, ensure_ascii=False))


def _run_tool(
    build_call: Callable[[], Awaitable[TypedToolResult[Any]]],
    *,
    pretty: bool,
    no_cache: bool,
) -> None:
    """Executa uma chamada de serviço e imprime o envelope padrão como JSON.

    Sai com código 1 quando `ok=False`, para facilitar o uso em scripts.
    """
    with _cache_override(no_cache=no_cache):
        envelope = asyncio.run(run_typed_tool(build_call()))

    _print_json(envelope, pretty=pretty)
    if not envelope["ok"]:
        raise typer.Exit(code=1)


@ibge_app.command("estados")
def ibge_estados(pretty: PrettyOption = False, no_cache: NoCacheOption = False) -> None:
    """Lista as unidades federativas (UFs) do Brasil."""
    _run_tool(lambda: LocalidadesService().listar_estados(), pretty=pretty, no_cache=no_cache)


@ibge_app.command("municipios")
def ibge_municipios(
    uf: Annotated[
        str, typer.Option("--uf", help='Sigla da UF (ex.: "RJ", "SP") ou código IBGE da UF.')
    ],
    pretty: PrettyOption = False,
    no_cache: NoCacheOption = False,
) -> None:
    """Lista os municípios de uma unidade federativa."""
    _run_tool(lambda: LocalidadesService().listar_municipios(uf), pretty=pretty, no_cache=no_cache)


@ibge_app.command("codigo-municipio")
def ibge_codigo_municipio(
    nome: Annotated[str, typer.Argument(help="Nome do município.")],
    uf: Annotated[str, typer.Option("--uf", help='Sigla (ex.: "SP") ou código IBGE da UF.')],
    pretty: PrettyOption = False,
    no_cache: NoCacheOption = False,
) -> None:
    """Obtém o código IBGE de 7 dígitos de um município a partir do nome e da UF."""
    _run_tool(
        lambda: LocalidadesService().obter_codigo_municipio(nome, uf),
        pretty=pretty,
        no_cache=no_cache,
    )


@ibge_app.command("buscar-municipio")
def ibge_buscar_municipio(
    nome: Annotated[str, typer.Argument(help="Nome (ou parte do nome) do município a buscar.")],
    uf: Annotated[
        str | None,
        typer.Option("--uf", help="Restringe a busca aos municípios desta UF (sigla ou código)."),
    ] = None,
    limite: Annotated[
        int,
        typer.Option("--limite", help="Número máximo de candidatos retornados.", min=1, max=50),
    ] = 10,
    pretty: PrettyOption = False,
    no_cache: NoCacheOption = False,
) -> None:
    """Busca municípios pelo nome, opcionalmente filtrando por UF."""
    _run_tool(
        lambda: LocalidadesService().buscar_municipio(nome, uf=uf, limite=limite),
        pretty=pretty,
        no_cache=no_cache,
    )


@sidra_app.command("metadados")
def sidra_metadados(
    agregado: Annotated[
        str,
        typer.Option(
            "--agregado", help='ID do agregado do SIDRA (ex.: "6579" = população estimada).'
        ),
    ],
    pretty: PrettyOption = False,
    no_cache: NoCacheOption = False,
) -> None:
    """Obtém os metadados de um agregado do SIDRA: pesquisa, assunto, variáveis etc."""
    _run_tool(
        lambda: AgregadosService().obter_metadados_agregado(agregado),
        pretty=pretty,
        no_cache=no_cache,
    )


@app.command("status")
def status(pretty: PrettyOption = False) -> None:
    """Mostra o status do servidor: versão, tools registradas, cache e fontes de dados."""
    from .server import _status_payload

    payload = asyncio.run(_status_payload())
    _print_json(payload, pretty=pretty)


if __name__ == "__main__":
    app()
