"""Cenário do experimento — Issues #6 (PARAMS, papel A) e #7 (texto, papel B)."""

PERGUNTA = "<Issue #7>"
H0 = "<Issue #7>"
H1 = "<Issue #7>"
CAUDAS = "<Issue #7: unicaudal ou bicaudal, com justificativa>"
EXPECTATIVA_PREVIA = "<Issue #7: qual teste deve se sair melhor e por quê — registrar ANTES de simular>"

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
