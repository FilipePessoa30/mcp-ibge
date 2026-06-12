# Prompt do usuário

> Estou preparando uma aula de Geografia sobre as capitais São Paulo, Rio de
> Janeiro e Belo Horizonte. Me dê a população estimada de cada uma (com a
> fonte) e gere um GeoJSON com o contorno das três cidades para eu mostrar no
> mapa.

## Variações

- "Quero um quiz: para cada cidade, dê o nome, a UF, a região e a
  população — os alunos precisam adivinhar qual contorno no mapa corresponde
  a qual cidade."
- "Pode me dar o bounding box de cada uma das três cidades, para eu centralizar
  o mapa em cada uma separadamente?"
- "Adicione Salvador (BA) à comparação." — testa o limite de
  `gerar_geojson_municipios`/`comparar_municipios` continuando a funcionar
  normalmente até 10 municípios.
- "Quero também o IDEB de cada cidade." — indicador não implementado; o
  agente deve dizer que essa informação não está disponível nesta versão, sem
  inventar valores.
