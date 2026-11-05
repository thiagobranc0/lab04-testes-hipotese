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
