"""Cenário do experimento — Issues #6 (PARAMS) e #7 (texto)."""

PERGUNTA = "Usar um bot de revisão de código muda o tempo até o merge de um Pull Request?"

H0 = ("O tempo até o merge tem a mesma distribuição em PRs com e sem bot de revisão "
      "(Welch: médias iguais; Mann-Whitney: P(com bot > sem bot) = 1/2).")

H1 = ("O tempo até o merge é diferente em PRs com bot de revisão "
      "(Welch: médias diferentes; Mann-Whitney: P(com bot > sem bot) ≠ 1/2).")

# Notação: X_com e X_sem são os tempos até o merge (horas) de PRs com e sem bot;
# μ é a média de cada grupo.
H0_NOTACAO = "H₀: μ_com = μ_sem (Welch)  ·  P(X_com > X_sem) = 1/2 (Mann-Whitney)"
H1_NOTACAO = "H₁: μ_com ≠ μ_sem (Welch)  ·  P(X_com > X_sem) ≠ 1/2 (Mann-Whitney)"

CAUDAS = ("Bilateral: o bot pode acelerar o merge (revisão mais rápida), mas também pode "
          "atrasá-lo (mais comentários e mais rodadas de ajuste), então testamos as duas direções.")

EXPECTATIVA_PREVIA = (
    "Esperamos que o Mann-Whitney se saia melhor. O tempo até o merge é muito assimétrico, "
    "com cauda longa e outliers (PRs que ficam dias abertos). Esses valores extremos inflam a "
    "variância e puxam a média, o que reduz o poder do t de Welch. O Mann-Whitney usa postos e "
    "é pouco afetado por outliers."
)

# Parâmetros da lognormal por grupo, ajustados aos dados reais (Issue #6).
# Ajuste por quantis em data/raw/prs_reais.csv (python -m src.analise; coleta de 05/11/2026):
# mediana = mediana observada; sigma = IQR de ln(horas) / 1,349. A máxima verossimilhança dá
# sigma parecido (2,19 e 2,58), mas mediana sem bot de 14 h, puxada pelos merges feitos em minutos.
# A simulação (Issue #8) usa os parâmetros de "sem_bot" nos dois grupos.
PARAMS = {
    "com_bot": {"mediana": 23.99, "sigma": 2.27},   # horas
    "sem_bot": {"mediana": 41.52, "sigma": 2.54},   # horas
}

# Origem e tamanho dos dados reais — seção 1 do dashboard (Issue #5).
TEXTO_DADOS_REAIS = (
    "**Dados reais:** 60 PRs mergeados do repositório público "
    "[formbricks/formbricks](https://github.com/formbricks/formbricks), que adotou o bot de revisão "
    "CodeRabbit em 19/08/2024. São 30 PRs **sem bot**, criados nos 90 dias anteriores à adoção, e 30 "
    "**com bot**, criados nos 90 dias seguintes a uma transição de 14 dias e revisados pelo CodeRabbit, "
    "sorteados com semente fixa entre 236 e 249 PRs elegíveis. Coleta feita pela API de busca do GitHub "
    "em 05/11/2026; critérios de inclusão e exclusão em `data/FONTE.md`."
)

# Como são os dados e por que esses parâmetros — seção 2 do dashboard (Issue #6).
TEXTO_G1 = (
    "Os tempos reais até o merge são muito assimétricos à direita: a média fica bem acima da mediana "
    "(99 h × 24 h com bot; 71 h × 42 h sem bot) e o critério do IQR aponta 3 outliers por grupo, PRs que "
    "levaram de 11 a 27 dias até o merge. Em escala log a assimetria diminui e os outliers somem, por isso "
    "simulamos lognormais com a mediana observada e σ = IQR de ln(horas)/1,349 (2,54 sem bot; 2,27 com bot), "
    "ajuste robusto aos merges feitos em minutos, que formam a cauda esquerda do QQ-plot. A simulação usa os "
    "parâmetros do grupo sem bot nos dois grupos; como os dois testes não mudam quando todos os tempos são "
    "multiplicados pela mesma constante, é o σ, e não a mediana, que pesa no erro tipo I e no poder."
)
