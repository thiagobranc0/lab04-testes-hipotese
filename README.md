# LAB04 — Testes de hipótese por dentro

**t de Welch × Mann-Whitney** aplicados ao tempo até o merge de PRs, com e sem bot de revisão.
Laboratório de Experimentação de Software — Engenharia de Software, PUC Minas (2026/2).

- **GitHub Projects:** https://github.com/users/thiagobranc0/projects/1
- **Dashboard publicado:** _a preencher_

## Como executar (comando único)

```bash
pip install -r requirements.txt && streamlit run app.py
```

Requer Python 3.11+. Todos os resultados usam semente fixa (`SEED = 42` em `src/config.py`) e são reproduzíveis.

## Estrutura

```
app.py                 dashboard Streamlit (7 seções na ordem do enunciado)
src/config.py          semente, α, nº de simulações, cores por teste
src/coleta.py          coleta dos PRs reais via API do GitHub
src/cenario.py         pergunta, H0/H1, parâmetros da simulação
src/simulacao.py       geração dos dados simulados
src/testes.py          Welch, Mann-Whitney e tamanhos de efeito
src/graficos.py        G1–G4
data/raw/              dados reais coletados (CSV)
data/FONTE.md          origem e método de coleta dos dados reais
```

## Equipe

| Integrante | Papel |
|---|---|
| Thiago Branco | _a definir_ |
| Bruna Costa | _a definir_ |
| Pedro Luiz Nato | _a definir_ |

## Fluxo de trabalho

- Toda mudança nasce de uma **Issue** e é feita em uma branch `feat/<nº-issue>-<slug>`.
- **Todo commit referencia a Issue:** `feat(simulacao): gera dados lognormais #8`.
- Merge na `main` apenas via Pull Request com `Closes #N`.
- No Projects: Backlog → To Do → In Progress (**WIP ≤ 1 por pessoa**) → Review → Done, atualizado toda semana.
