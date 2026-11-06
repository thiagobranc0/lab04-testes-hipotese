"""Cenário do experimento — Issues #6 (PARAMS) e #7 (texto)."""

PERGUNTA = "Usar um bot de revisão de código muda o tempo até o merge de um Pull Request?"

H0 = ("O tempo até o merge tem a mesma distribuição em PRs com e sem bot de revisão "
      "(Welch: médias iguais; Mann-Whitney: P(com bot > sem bot) = 1/2).")

H1 = ("O tempo até o merge é diferente em PRs com bot de revisão "
      "(Welch: médias diferentes; Mann-Whitney: P(com bot > sem bot) ≠ 1/2).")

CAUDAS = ("Bilateral: o bot pode acelerar o merge (revisão mais rápida), mas também pode "
          "atrasá-lo (mais comentários e mais rodadas de ajuste), então testamos as duas direções.")

EXPECTATIVA_PREVIA = (
    "Esperamos que o Mann-Whitney se saia melhor. O tempo até o merge é muito assimétrico, "
    "com cauda longa e outliers (PRs que ficam dias abertos). Esses valores extremos inflam a "
    "variância e puxam a média, o que reduz o poder do t de Welch. O Mann-Whitney usa postos e "
    "é pouco afetado por outliers."
)

# Parâmetros da lognormal por grupo, ajustados aos dados reais (Issue #6).
# Valores provisórios até a coleta ficar pronta.
PARAMS = {
    "com_bot": {"mediana": 10.0, "sigma": 1.0},   # horas
    "sem_bot": {"mediana": 10.0, "sigma": 1.0},   # horas
}
