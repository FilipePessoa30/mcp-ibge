"""Testes da configuração de logging (`mcp_ibge.logging_config`)."""

from __future__ import annotations

import json
import logging
import sys

from mcp_ibge.logging_config import JSONFormatter, configure_logging


def test_json_formatter_produz_linha_json_com_campos_esperados():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="mcp_ibge.teste",
        level=logging.INFO,
        pathname=__file__,
        lineno=1,
        msg="GET %s params=%s",
        args=("/estados", {"orderBy": "nome"}),
        exc_info=None,
    )

    linha = formatter.format(record)
    payload = json.loads(linha)

    assert payload["level"] == "INFO"
    assert payload["logger"] == "mcp_ibge.teste"
    assert payload["message"] == "GET /estados params={'orderBy': 'nome'}"
    assert "timestamp" in payload
    assert "exc_info" not in payload


def test_json_formatter_inclui_exc_info_quando_presente():
    formatter = JSONFormatter()
    try:
        raise ValueError("falha de teste")
    except ValueError:
        record = logging.LogRecord(
            name="mcp_ibge.teste",
            level=logging.ERROR,
            pathname=__file__,
            lineno=1,
            msg="erro inesperado",
            args=None,
            exc_info=sys.exc_info(),
        )

    payload = json.loads(formatter.format(record))

    assert payload["message"] == "erro inesperado"
    assert "ValueError: falha de teste" in payload["exc_info"]


def test_configure_logging_emite_json_em_stderr(capsys, monkeypatch):
    settings = __import__("mcp_ibge.config", fromlist=["get_settings"]).get_settings().model_copy(
        update={"log_level": "INFO"}
    )
    monkeypatch.setattr("mcp_ibge.logging_config.get_settings", lambda: settings)

    configure_logging()
    logging.getLogger("mcp_ibge.teste").info("mensagem de teste")

    captured = capsys.readouterr()
    assert captured.out == ""

    linha = captured.err.strip().splitlines()[-1]
    payload = json.loads(linha)
    assert payload["level"] == "INFO"
    assert payload["message"] == "mensagem de teste"
