# Tools esperadas

Para o prompt "Me dá um perfil básico do município de Niterói, no Rio de
Janeiro (RJ) ...", um agente bem-comportado deve chamar:

1. **`gerar_perfil_municipal`** — a tool dedicada para este caso, que já
   combina identificação + população em uma única resposta.

```python
gerar_perfil_municipal(nome="Niterói", uf="RJ")
```

## Internamente (não precisa ser chamado de novo pelo agente)

`gerar_perfil_municipal` já faz, internamente:

- `obter_codigo_municipio(nome="Niterói", uf="RJ")` → resolve para o código
  IBGE `3303302`.
- `obter_municipio_por_codigo(codigo_ibge=3303302)` → nome, UF, região e
  microrregião.
- `consultar_populacao_municipio(nome="Niterói", uf="RJ")` → população
  estimada mais recente.

O agente **não precisa** chamar essas três tools separadamente — chamar
`gerar_perfil_municipal` diretamente evita requisições duplicadas.

## Quando NÃO usar `gerar_perfil_municipal`

- Se o usuário pedir **apenas** o código IBGE → use
  [`obter_codigo_municipio`](../../../packages/mcp_ibge/docs/tools.md#5-obter_codigo_municipio).
- Se o usuário pedir **apenas** a população, sem o resto do perfil → use
  [`consultar_populacao_municipio`](../../../packages/mcp_ibge/docs/tools.md#14-consultar_populacao_municipio).
- Se o usuário pedir um **mapa** ou a **geometria** do município → veja a
  receita [`education_activity`](../education_activity/) (usa
  `obter_malha_municipio`/`obter_bbox_municipio`).
- Se o usuário pedir para **comparar** vários municípios → use
  [`comparar_municipios`](../../../packages/mcp_ibge/docs/tools.md#23-comparar_municipios)
  (veja a receita [`compare_municipalities`](../compare_municipalities/)).
