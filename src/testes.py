"""Aplicação dos testes — Issue #9."""
import numpy as np
from scipy import stats

from src import config


def hedges_g(a: np.ndarray, b: np.ndarray) -> float:
    """Diferença de médias padronizada, com correção para amostras pequenas."""
    n1, n2 = len(a), len(b)
    sp = np.sqrt(((n1 - 1) * np.var(a, ddof=1) + (n2 - 1) * np.var(b, ddof=1)) / (n1 + n2 - 2))
    return (np.mean(a) - np.mean(b)) / sp * (1 - 3 / (4 * (n1 + n2) - 9))


def aplicar_testes(a: np.ndarray, b: np.ndarray) -> dict:
    """Aplica t de Welch e Mann-Whitney (bilaterais) a a=com_bot e b=sem_bot.

    Efeito: Hedges' g (Welch) e Cliff's delta (Mann-Whitney), de -1 a 1.
    """
    w = stats.ttest_ind(a, b, equal_var=False)
    m = stats.mannwhitneyu(a, b, alternative="two-sided")
    return {
        "welch": {"stat": float(w.statistic), "p": float(w.pvalue),
                  "efeito": float(hedges_g(a, b)), "rejeita": bool(w.pvalue < config.ALPHA)},
        "mann_whitney": {"stat": float(m.statistic), "p": float(m.pvalue),
                         "efeito": float(2 * m.statistic / (len(a) * len(b)) - 1),
                         "rejeita": bool(m.pvalue < config.ALPHA)},
    }


def interpretar(resultado: dict) -> str:
    """Texto curto com a conclusão de cada teste (vai para o dashboard)."""
    nomes = {"welch": ("t de Welch", "Hedges' g"), "mann_whitney": ("Mann-Whitney", "Cliff's delta")}
    frases = []
    for teste, (nome, nome_efeito) in nomes.items():
        r = resultado[teste]
        decisao = "rejeitamos H0" if r["rejeita"] else "não rejeitamos H0"
        frases.append(f"**{nome}:** p = {r['p']:.3f} → {decisao} ao nível de {config.ALPHA:g}; "
                      f"{nome_efeito} = {r['efeito']:.2f}.")
    if resultado["welch"]["rejeita"] != resultado["mann_whitney"]["rejeita"]:
        frases.append("Os dois testes chegaram a conclusões diferentes no mesmo conjunto de dados.")
    return "\n\n".join(frases)


if __name__ == "__main__":
    from src import cenario
    from src.simulacao import gerar_dados

    rng = np.random.default_rng(config.SEED)
    com_bot, sem_bot = gerar_dados(30, cenario.PARAMS, efeito=0.3, rng=rng)
    print(interpretar(aplicar_testes(com_bot, sem_bot)))
