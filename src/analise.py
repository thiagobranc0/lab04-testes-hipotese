"""Análise descritiva dos dados reais e ajuste da lognormal — Issue #6 (papel A).

Uso (a partir da raiz do repositório):
    python -m src.analise

Imprime as estatísticas descritivas por grupo, a checagem do ajuste e o bloco
PARAMS pronto para colar em src/cenario.py.

Ajuste: se X ~ Lognormal, então ln X ~ Normal(μ, σ) e a mediana de X é e^μ.
Dois métodos são calculados:

- "quantis" (usado em PARAMS): mediana = mediana amostral; σ = IQR de ln X / 1,349
  (o IQR de uma normal vale 1,349σ). É robusto aos merges-relâmpago (minutos), que
  formam uma cauda à esquerda em ln X e puxariam a média de ln X para baixo;
- "mv" (máxima verossimilhança, só para comparação): μ e σ = média e desvio-padrão
  populacional de ln X — o mesmo que scipy.stats.lognorm.fit(x, floc=0).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

from src import config

ROTULOS = {"com_bot": "Com bot", "sem_bot": "Sem bot"}


def _horas(df: pd.DataFrame, grupo: str) -> np.ndarray:
    return df.loc[df["grupo"] == grupo, "horas"].to_numpy(dtype=float)


def _n_outliers(x: np.ndarray) -> int:
    """Pontos fora de [Q1 − 1,5·IQR, Q3 + 1,5·IQR]."""
    q1, q3 = np.percentile(x, [25, 75])
    iqr = q3 - q1
    return int(((x < q1 - 1.5 * iqr) | (x > q3 + 1.5 * iqr)).sum())


def descritiva(df: pd.DataFrame) -> pd.DataFrame:
    """Estatísticas descritivas por grupo (linhas = grupos). Tempos em horas."""
    linhas = {}
    for grupo in config.GRUPOS:
        x = _horas(df, grupo)
        log = np.log(x)
        q1, q3 = np.percentile(x, [25, 75])
        linhas[grupo] = {
            "n": len(x),
            "mediana": np.median(x),
            "media": x.mean(),
            "dp": x.std(ddof=1),
            "q1": q1,
            "q3": q3,
            "max": x.max(),
            "assimetria": stats.skew(x, bias=False),
            "assimetria_log": stats.skew(log, bias=False),
            "outliers": _n_outliers(x),
            "outliers_log": _n_outliers(log),
        }
    return pd.DataFrame(linhas).T.astype(float).astype({"n": int, "outliers": int, "outliers_log": int})


IQR_NORMAL = stats.norm.ppf(0.75) - stats.norm.ppf(0.25)   # ≈ 1,349


def ajustar_lognormal(horas, metodo: str = "quantis") -> dict:
    """Mediana (horas) e σ (escala log) da lognormal ajustada. metodo: "quantis" ou "mv"."""
    log = np.log(np.asarray(horas, dtype=float))
    if metodo == "quantis":
        q1, q3 = np.percentile(log, [25, 75])
        return {"mediana": float(np.median(np.exp(log))), "sigma": float((q3 - q1) / IQR_NORMAL)}
    if metodo == "mv":
        return {"mediana": float(np.exp(log.mean())), "sigma": float(log.std(ddof=0))}
    raise ValueError("metodo deve ser 'quantis' ou 'mv'")


def ajustar_por_grupo(df: pd.DataFrame, metodo: str = "quantis") -> dict[str, dict]:
    """Parâmetros no formato de cenario.PARAMS."""
    return {grupo: ajustar_lognormal(_horas(df, grupo), metodo) for grupo in config.GRUPOS}


def checar_ajuste(df: pd.DataFrame) -> pd.DataFrame:
    """Compara os dois métodos de ajuste e testa a normalidade de ln(horas) (Shapiro-Wilk)."""
    q, mv = ajustar_por_grupo(df, "quantis"), ajustar_por_grupo(df, "mv")
    linhas = {}
    for grupo in config.GRUPOS:
        x = _horas(df, grupo)
        w, p = stats.shapiro(np.log(x))
        linhas[grupo] = {
            "mediana_amostral": np.median(x),
            "mediana_quantis": q[grupo]["mediana"],
            "sigma_quantis": q[grupo]["sigma"],
            "mediana_mv": mv[grupo]["mediana"],
            "sigma_mv": mv[grupo]["sigma"],
            "shapiro_W_log": w,
            "shapiro_p_log": p,
        }
    return pd.DataFrame(linhas).T


def efeito_observado(params: dict) -> float:
    """Redução relativa da mediana com bot, na mesma definição de `efeito` da simulação:
    mediana_com = mediana_sem · (1 − efeito). Negativo = com bot o merge demora mais."""
    return 1 - params["com_bot"]["mediana"] / params["sem_bot"]["mediana"]


def qq_lognormal(df: pd.DataFrame, params: dict):
    """QQ-plot de ln(horas) contra a normal ajustada, um painel por grupo (Plotly)."""
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots

    fig = make_subplots(rows=1, cols=len(config.GRUPOS), horizontal_spacing=0.1,
                        subplot_titles=[ROTULOS[g] for g in config.GRUPOS])
    for col, grupo in enumerate(config.GRUPOS, start=1):
        obs = np.sort(np.log(_horas(df, grupo)))
        n = len(obs)
        mu, sigma = np.log(params[grupo]["mediana"]), params[grupo]["sigma"]
        teo = stats.norm.ppf((np.arange(1, n + 1) - 0.5) / n, loc=mu, scale=sigma)
        cor = config.CORES_GRUPOS[grupo]
        fig.add_trace(go.Scatter(
            x=teo, y=obs, mode="markers", marker=dict(color=cor, size=8, opacity=0.85),
            name=f"{ROTULOS[grupo]}: PRs reais",
            customdata=np.exp(obs),
            hovertemplate="teórico %{x:.2f} · observado %{y:.2f}<br>= %{customdata:.1f} h<extra></extra>",
        ), row=1, col=col)
        lo, hi = min(teo.min(), obs.min()), max(teo.max(), obs.max())
        fig.add_trace(go.Scatter(
            x=[lo, hi], y=[lo, hi], mode="lines", line=dict(color="#555555", dash="dash", width=1.5),
            name="Ajuste perfeito (y = x)", showlegend=(col == 1), hoverinfo="skip",
        ), row=1, col=col)
        fig.update_xaxes(title_text="Quantis teóricos de ln(horas)", row=1, col=col)
        fig.update_yaxes(title_text="Quantis observados de ln(horas)", row=1, col=col)

    fig.update_layout(
        title="Checagem do ajuste — QQ-plot da lognormal ajustada a cada grupo",
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        height=430, margin=dict(t=80, b=110), plot_bgcolor="white",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eeeeee", zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor="#eeeeee", zeroline=False)
    return fig


def main() -> None:
    from src.coleta import carregar_dados_reais

    df = carregar_dados_reais()
    params = ajustar_por_grupo(df)
    pd.set_option("display.width", 140)
    print("Estatísticas descritivas (horas)\n")
    print(descritiva(df).round(2).to_string())
    print("\nChecagem do ajuste lognormal\n")
    print(checar_ajuste(df).round(3).to_string())
    print(f"\nEfeito observado (redução relativa da mediana com bot): {efeito_observado(params):.2f}")
    print("\nPARAMS (método dos quantis) = {")
    for grupo in config.GRUPOS:
        p = params[grupo]
        print(f'    "{grupo}": {{"mediana": {p["mediana"]:.2f}, "sigma": {p["sigma"]:.2f}}},   # horas')
    print("}")


if __name__ == "__main__":
    main()
