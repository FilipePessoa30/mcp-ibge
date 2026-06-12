# Security baseline

`mcp-data-br` modules connect MCP clients (and the LLMs behind them) to
**public, unauthenticated** Brazilian government data APIs. There are no
secrets, API keys, or user data persisted by any module. Every module is
expected to meet the same baseline; module-specific details live in each
package's `docs/security.md` (e.g.
[packages/mcp_ibge/docs/security.md](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_ibge/docs/security.md)).

## Baseline requirements for every module

1. **No shell execution** — no `subprocess`, `os.system`, `shell=True`, or
   similar. All logic is Python + HTTP calls via `httpx`.
2. **No local file access** beyond loading configuration (`.env` /
   environment variables) at startup. Tools never read or write files based
   on client/agent-supplied paths.
3. **No arbitrary URLs** — tool parameters are structured identifiers
   (codes, names, IDs, periods), validated and embedded into fixed path
   templates. No tool accepts a full URL as input.
4. **Allowlisted upstream hosts** — each module validates its configured API
   base URL at startup against a fixed allowlist of official hosts
   (`https` only). The server refuses to start otherwise.
5. **Input validation before any network call** — all tool parameters are
   validated (format, ranges, enums) before a request is made, returning a
   structured validation error instead of forwarding bad input upstream.
6. **Timeouts** on every outbound HTTP request, configurable per module.
7. **Response size limits** — oversized upstream responses are aborted
   instead of fully buffered.
8. **No secrets** — configuration covers URLs, timeouts, and cache settings
   only; nothing in `.env.example` should ever be a credential.
9. **Errors without stack traces** — exceptions are converted into short,
   informative error messages in the response envelope; full tracebacks go
   to `stderr` logs only, never to the MCP client.
10. **stdio-safe logging** — all logs go to `stderr`. `stdout` is reserved
    exclusively for the MCP protocol when using the `stdio` transport.

## Reference implementation

In `mcp-ibge`, points 3, 4, 6, 7 and 9 are implemented by a small,
centralized `mcp_ibge.security` module
([source](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_ibge/src/mcp_ibge/security.py),
[tests](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_ibge/tests/test_security.py))
that exposes `assert_allowed_url`/`is_allowed_url` (host allowlist check
before every request), `response_size_guard` (response size limit) and
`safe_error_response` (stack-trace-free error messages). See
[packages/mcp_ibge/docs/security.md §12](https://github.com/FilipePessoa30/mcp-data-br/blob/main/packages/mcp_ibge/docs/security.md#12-módulo-central-mcp_ibgesecurity)
for details — future modules should follow the same pattern.

## Transports

- **`stdio`** (default): no inbound network exposure — the client spawns the
  server process and communicates via stdin/stdout.
- **`streamable-http`** (optional, where supported): opens a local HTTP
  server. Treat it like any other local network service — don't expose it
  publicly without authentication/proxying. Each module's
  `docs/security.md` documents its current hardening level for this
  transport.

## Reporting a vulnerability

If you find a security issue, please open a GitHub issue with as much detail
as possible (affected module, reproduction steps, impact). Since these
servers only access public data and hold no secrets, most concerns will be
about input validation, host allowlists, or resource exhaustion — but we
still want to know.
