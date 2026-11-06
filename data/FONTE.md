# Fonte dos dados reais

Dados usados no G1 (seção 2), no ajuste dos parâmetros da simulação (`cenario.PARAMS`)
e na aplicação final dos testes (seção 6). Issues #5 (coleta) e #6 (ajuste).

## Resumo

| Item | Valor |
|---|---|
| Repositório | [formbricks/formbricks](https://github.com/formbricks/formbricks) — plataforma open-source de pesquisas (TypeScript) |
| Bot de revisão | [CodeRabbit](https://coderabbit.ai) (`coderabbitai[bot]`) |
| Adoção do bot | 19/08/2024 (criação do 1º PR comentado pelo bot, #3020) |
| Variável | `horas_ate_merge = (merged_at − created_at)` em horas |
| Amostra | 30 PRs sem bot + 30 PRs com bot (`data/raw/prs_reais.csv`) |
| Data da coleta | 05/11/2026, via API de busca do GitHub |
| Reproduzir | `python -m src.coleta` (sorteio com `SEED = 42`) |

## Desenho: antes × depois da adoção

O enunciado pede dados de **um** repositório público, com e sem bot. Comparamos o
mesmo repositório antes e depois de adotar o bot, para que o projeto, a equipe e o
processo de revisão sejam os mesmos nos dois grupos.

| Grupo | PRs criados entre | Regra |
|---|---|---|
| `sem_bot` | 21/05/2024 e 18/08/2024 (90 dias antes da adoção) | nenhum bot da lista fechada comentou ou revisou |
| `com_bot` | 02/09/2024 e 30/11/2024 (90 dias, após 14 dias de transição) | `coderabbitai[bot]` comentou ou revisou |

Os 14 dias logo após a adoção ficam de fora como período de implantação, em que a
equipe ainda se adaptava ao bot.

**Lista fechada de bots de revisão** (bots de CI, cobertura, deploy ou dependências não
contam): `coderabbitai`, `copilot-pull-request-reviewer`, `sourcery-ai`, `ellipsis-dev`,
`greptile-apps`.

## Critérios de inclusão e exclusão

Entram PRs **mergeados** (`is:pr is:merged`) criados dentro da janela do grupo. Saem:

| Motivo | sem_bot | com_bot |
|---|---:|---:|
| PRs mergeados na janela | 242 | 299 |
| autor do PR é bot (ex.: dependabot) | 0 | 3 |
| merge em menos de 1 minuto (merge automático/administrativo) | 6 | 11 |
| bot de revisão antes da adoção | 0 | — |
| não revisado pelo bot após a adoção | — | 36 |
| **Elegíveis** | **236** | **249** |
| **Sorteados** (`numpy.random.default_rng(42)`) | **30** | **30** |

Na janela com bot, o CodeRabbit revisou 87% dos PRs humanos (249 de 285).
Todos os candidatos, com o motivo de exclusão, estão em `data/raw/prs_candidatos.csv`.

## Como a coleta funciona

`src/coleta.py` usa só a API de busca (`/search/issues`):

1. `repo:formbricks/formbricks is:pr is:merged created:<início>..<fim>` lista os PRs da
   janela, já com `created_at`, `merged_at` e o tipo do autor;
2. a mesma consulta com `commenter:app/<bot>` e `reviewed-by:app/<bot>` identifica os
   PRs em que cada bot comentou ou revisou;
3. os critérios acima classificam cada PR, e o sorteio escolhe 30 elegíveis por grupo.

Com `GITHUB_TOKEN` (variável de ambiente ou `.env`), a coleta leva cerca de 2 minutos;
sem token, a busca aceita só 10 consultas por minuto e demora mais.

## Arquivos

- `data/raw/prs_reais.csv` — amostra final: `grupo, repo, pr_number, created_at, merged_at, horas_ate_merge, bot`
- `data/raw/prs_candidatos.csv` — todos os PRs das duas janelas, com `autor` e `motivo_exclusao`

## Limitações

- **Tempo como fator de confusão:** os grupos são de períodos diferentes (meados × fim de
  2024). Mudanças na equipe, em releases ou na época do ano também afetam o tempo até o merge.
- **Seleção no grupo com bot:** os 13% de PRs que o bot não revisou ficaram de fora e podem
  ser diferentes (ex.: PRs pequenos ou abertos por mantenedores).
- **Drafts:** o tempo conta desde a criação do PR; um PR aberto como draft acumula horas antes
  de estar pronto para revisão.
- **Índice de busca:** a classificação depende do índice de busca do GitHub, e não da
  timeline de cada PR. Conferimos na página do GitHub uma amostra de PRs sorteados
  (ex.: #3174 com o CodeRabbit; #2806 sem nenhum bot).
