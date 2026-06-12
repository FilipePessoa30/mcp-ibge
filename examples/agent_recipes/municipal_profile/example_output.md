# Exemplo de resposta

## Resposta da tool `gerar_perfil_municipal(nome="Niterói", uf="RJ")`

```json
{
  "ok": true,
  "data": {
    "municipio": {
      "codigo_ibge": 3303302,
      "nome": "Niterói",
      "uf_sigla": "RJ",
      "uf_nome": "Rio de Janeiro",
      "regiao_nome": "Sudeste",
      "microrregiao_ou_regiao_intermediaria": {
        "tipo": "microrregiao",
        "id": 33014,
        "nome": "Niterói"
      }
    },
    "indicadores": [
      {
        "indicador": "populacao_estimada",
        "valor": 516981.0,
        "unidade": "Pessoas",
        "periodo": "2024",
        "agregado_id": "6579",
        "variavel_id": "9324"
      }
    ],
    "fontes": [
      "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
      "https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324"
    ],
    "limitacoes": [
      "Este perfil cobre apenas identificação básica do município e o indicador de população estimada; não inclui PIB, IDH, área territorial ou outros indicadores socioeconômicos.",
      "O indicador de população usa o agregado SIDRA 6579 (Estimativas de população residente), que pode ser descontinuado ou renomeado pelo IBGE após um novo Censo."
    ],
    "proximos_indicadores_sugeridos": [
      "Área territorial e densidade demográfica",
      "PIB municipal e PIB per capita",
      "IDH municipal",
      "Distritos do município (via `listar_distritos`)",
      "Indicadores educacionais e de saúde"
    ]
  },
  "metadata": {
    "source_name": "IBGE - Instituto Brasileiro de Geografia e Estatística",
    "source_url": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
    "official_source": "https://www.ibge.gov.br/",
    "endpoint": "https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302",
    "params": { "nome": "Niterói", "uf": "RJ", "municipio_id": 3303302 },
    "retrieved_at": "2026-06-12T12:00:00.000000+00:00",
    "period": null,
    "territorial_level": null,
    "license_note": null,
    "version": "0.2.0",
    "cache_hit": false
  },
  "warnings": [
    {
      "message": "Nenhum \"ano\" foi informado para a população: retornado o período mais recente disponível no SIDRA (\"2024\").",
      "code": null
    }
  ],
  "errors": []
}
```

> Os valores acima (população `516981`, período `2024`) são ilustrativos.
> Execute a tool para obter o valor atual.

## Resposta final do agente ao usuário

> **Niterói (RJ)** — código IBGE `3303302`
>
> - **Região**: Sudeste
> - **Microrregião**: Niterói (código 33014)
> - **População estimada (2024)**: ~516.981 habitantes
>
> **Fonte**: IBGE — API de Localidades e Agregados/SIDRA (agregado 6579 —
> Estimativas de População), período 2024.
>
> **Limitações**: este perfil cobre apenas identificação básica e o
> indicador de população estimada (não inclui PIB, IDH ou área territorial).
> O indicador de população pode ser descontinuado/renomeado pelo IBGE após
> um novo Censo. Como nenhum "ano" foi informado, o valor corresponde ao
> período mais recente disponível no SIDRA na data da consulta.

## Exemplo de erro: município ambíguo

Se o usuário pedir, por exemplo, `gerar_perfil_municipal(nome="São José", uf="SP")`
e houver mais de um município "São José..." em SP, a resposta é:

```json
{
  "ok": false,
  "data": null,
  "warnings": [
    {
      "message": "Encontrados 2 municípios para \"São José\": São José dos Campos, São José do Rio Preto. Refine a busca com \"uf\" ou um nome mais específico.",
      "code": null
    }
  ],
  "errors": [
    {
      "message": "Encontrados 2 municípios para \"São José\": São José dos Campos, São José do Rio Preto. Refine a busca com \"uf\" ou um nome mais específico.",
      "code": null
    }
  ]
}
```

Nesse caso o agente deve **perguntar ao usuário** qual dos municípios
listados é o desejado, em vez de escolher um arbitrariamente.

## Como verificar a fonte

- Endpoint usado para identificação:
  `https://servicodados.ibge.gov.br/api/v1/localidades/municipios/3303302`
- Endpoint usado para a população:
  `https://servicodados.ibge.gov.br/api/v3/agregados/6579/periodos/-1/variaveis/9324?localidades=N6[3303302]`
- Compare os valores retornados em `data` com o conteúdo desses endpoints —
  ambos acessíveis diretamente no navegador, sem autenticação.
