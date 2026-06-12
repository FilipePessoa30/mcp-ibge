# Prompt do usuário

> Compare a população estimada do Rio de Janeiro, Niterói e Maricá (RJ), com
> a fonte e o ano de referência.

## Variações

- "Qual desses três municípios do Rio de Janeiro tem mais habitantes: Rio de
  Janeiro, Niterói ou Maricá?"
- "Compare a população e o PIB de Rio de Janeiro, Niterói e Maricá." — PIB
  ainda não é suportado; o agente deve explicar que apenas a população foi
  comparada, listando "pib" em `data.indicadores_nao_implementados`.
- "Compare a população de Niterói (RJ) e de uma cidade chamada 'Itaboraí' que
  talvez não exista." — testa o caminho de `municipios_nao_resolvidos`.
