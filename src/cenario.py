"""Cenário do experimento — Issues #6 (PARAMS, papel A) e #7 (texto, papel B)."""

PERGUNTA = "<Issue #7>"
H0 = "<Issue #7>"
H1 = "<Issue #7>"
CAUDAS = "<Issue #7: unicaudal ou bicaudal, com justificativa>"
EXPECTATIVA_PREVIA = "<Issue #7: qual teste deve se sair melhor e por quê — registrar ANTES de simular>"

# Parâmetros da lognormal por grupo, ajustados aos dados reais (Issue #6).
# Valores provisórios até a coleta ficar pronta.
PARAMS = {
    "com_bot": {"mediana": 10.0, "sigma": 1.0},   # horas
    "sem_bot": {"mediana": 10.0, "sigma": 1.0},   # horas
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
