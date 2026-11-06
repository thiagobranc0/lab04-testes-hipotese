"""Gráficos do dashboard (Plotly). Use sempre config.CORES para os testes."""
import numpy as np
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from scipy import stats

from src import config

CAUDAS_VALIDAS = ("bilateral", "maior", "menor")


def g1(reais, simulados):
    """G1 — dados reais × simulados, histograma por grupo. Issue #3."""
    raise NotImplementedError("Issue #3")


# ── G2 ───────────────────────────────────────────────────────────────────────

def _rgba(hex_cor: str, alpha: float) -> str:
    h = hex_cor.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return f"rgba({r},{g},{b},{alpha})"


def _df_welch(a: np.ndarray, b: np.ndarray) -> float:
    """Graus de liberdade de Welch–Satterthwaite."""
    va, vb = np.var(a, ddof=1) / len(a), np.var(b, ddof=1) / len(b)
    return (va + vb) ** 2 / (va ** 2 / (len(a) - 1) + vb ** 2 / (len(b) - 1))


def _nula(teste: str, a: np.ndarray, b: np.ndarray):
    """Distribuição da estatística sob H0 como objeto scipy "congelado" + rótulos.

    - Welch: t de Student com gl de Welch–Satterthwaite.
    - Mann-Whitney: U ~ Normal(n1·n2/2, √(n1·n2·(n1+n2+1)/12)) — aproximação normal,
      sem correção para empates.
    """
    if teste == "welch":
        gl = _df_welch(a, b)
        return stats.t(df=gl), "Estatística t (adimensional)", f"t de Student, gl = {gl:.1f}"
    n1, n2 = len(a), len(b)
    mu, sigma = n1 * n2 / 2, np.sqrt(n1 * n2 * (n1 + n2 + 1) / 12)
    return (stats.norm(loc=mu, scale=sigma), "Estatística U (nº de pares em que o 1º grupo vence)",
            f"aproximação normal: média {mu:.0f}, dp {sigma:.1f}")


def _regioes(dist, observado: float, caudas: str, alpha: float):
    """Retorna (intervalos de rejeição, intervalos do p-valor) como listas de (ini, fim)."""
    lo, hi = dist.ppf(1e-4), dist.ppf(1 - 1e-4)
    centro = dist.mean()
    if caudas == "bilateral":
        c_lo, c_hi = dist.ppf(alpha / 2), dist.ppf(1 - alpha / 2)
        dist_obs = abs(observado - centro)
        rejeicao = [(lo, c_lo), (c_hi, hi)]
        pvalor = [(lo, centro - dist_obs), (centro + dist_obs, hi)]
    elif caudas == "maior":
        rejeicao = [(dist.ppf(1 - alpha), hi)]
        pvalor = [(observado, hi)]
    else:  # "menor"
        rejeicao = [(lo, dist.ppf(alpha))]
        pvalor = [(lo, observado)]
    # Estende os limites para o valor observado sempre aparecer no gráfico
    lo_plot, hi_plot = min(lo, observado), max(hi, observado)
    rejeicao = [(max(i, lo_plot), min(f, hi_plot)) for i, f in rejeicao]
    pvalor = [(max(i, lo_plot), min(f, hi_plot)) for i, f in pvalor if f > i]
    return (lo_plot, hi_plot), rejeicao, pvalor


def g2(a: np.ndarray, b: np.ndarray, resultado: dict,
       caudas: str = "bilateral", alpha: float = config.ALPHA) -> go.Figure:
    """G2 — distribuição da estatística sob H0, com região de rejeição sombreada
    e o p-valor do exemplo marcado como área, um painel por teste.

    a, b       — o conjunto de dados simulado usado como exemplo (com_bot, sem_bot)
    resultado  — saída de testes.aplicar_testes(a, b):
                 {"welch": {"stat", "p", ...}, "mann_whitney": {"stat", "p", ...}}
    caudas     — "bilateral", "maior" ou "menor" (definido no cenário, Issue #7)
    """
    if caudas not in CAUDAS_VALIDAS:
        raise ValueError(f"caudas deve ser um de {CAUDAS_VALIDAS}")
    a, b = np.asarray(a, dtype=float), np.asarray(b, dtype=float)
    testes = ("welch", "mann_whitney")

    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.08,
                        subplot_titles=[config.NOMES_TESTES[t] for t in testes])

    for col, teste in enumerate(testes, start=1):
        cor = config.CORES[teste]
        nome = config.NOMES_TESTES[teste]
        obs, p = float(resultado[teste]["stat"]), float(resultado[teste]["p"])
        dist, rotulo_x, descricao = _nula(teste, a, b)
        (lo, hi), rejeicao, pvalor = _regioes(dist, obs, caudas, alpha)

        x = np.linspace(lo, hi, 600)
        fig.add_trace(go.Scatter(
            x=x, y=dist.pdf(x), mode="lines", line=dict(color=cor, width=2.5),
            name=f"{nome}: distribuição sob H₀", legendgroup=teste,
            hovertemplate="%{x:.2f}<extra>" + descricao + "</extra>",
        ), row=1, col=col)

        for i, (ini, fim) in enumerate(rejeicao):
            xr = np.linspace(ini, fim, 200)
            fig.add_trace(go.Scatter(
                x=np.r_[ini, xr, fim], y=np.r_[0, dist.pdf(xr), 0], fill="toself",
                fillcolor=_rgba(cor, 0.18), line=dict(width=0), hoverinfo="skip",
                name=f"{nome}: região de rejeição (α = {alpha:g})", legendgroup=teste,
                showlegend=(i == 0),
            ), row=1, col=col)

        for i, (ini, fim) in enumerate(pvalor):
            xp = np.linspace(ini, fim, 200)
            fig.add_trace(go.Scatter(
                x=np.r_[ini, xp, fim], y=np.r_[0, dist.pdf(xp), 0], fill="toself",
                fillcolor=_rgba(cor, 0.55), fillpattern=dict(shape="/", fgcolor="white", size=6),
                line=dict(width=0), hoverinfo="skip",
                name=f"{nome}: área do p-valor (p = {p:.3f})", legendgroup=teste,
                showlegend=(i == 0),
            ), row=1, col=col)

        fig.add_vline(x=obs, line=dict(color="#333333", dash="dash", width=1.5), row=1, col=col)
        fig.add_annotation(x=obs, y=1, yref="y domain" if col == 1 else "y2 domain",
                           xref="x" if col == 1 else "x2", text=f"observado = {obs:.2f}<br>p = {p:.3f}",
                           showarrow=False, yanchor="top", xanchor="left", xshift=6,
                           font=dict(size=12), bgcolor="rgba(255,255,255,0.8)")
        fig.update_xaxes(title_text=rotulo_x, row=1, col=col)
        fig.update_yaxes(title_text="Densidade de probabilidade", row=1, col=col)

    titulo_caudas = {"bilateral": "teste bilateral", "maior": "teste unicaudal (H₁: maior)",
                     "menor": "teste unicaudal (H₁: menor)"}[caudas]
    fig.update_layout(
        title=f"G2 — Distribuição da estatística de cada teste sob H₀ ({titulo_caudas}, α = {alpha:g})",
        legend=dict(orientation="h", yanchor="top", y=-0.18, xanchor="center", x=0.5),
        height=480, margin=dict(t=80, b=130), plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eeeeee", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eeeeee", zeroline=False, rangemode="tozero")
    return fig


def g3(*args, **kwargs):
    """G3 — erro tipo I por situação, linha em 5%. Sprint 2."""
    raise NotImplementedError("Sprint 2")


def g4(*args, **kwargs):
    """G4 — curvas de poder dos dois testes. Sprint 2."""
    raise NotImplementedError("Sprint 2")
