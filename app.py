"""Dashboard do LAB04. Executar: streamlit run app.py

As 7 seções seguem a ordem exigida no enunciado. Cada seção mostra o gráfico/tabela
quando a função correspondente estiver implementada; até lá, exibe um aviso com a
Issue responsável, para o dashboard sempre abrir sem erro.
"""
import streamlit as st

from src import analise, cenario, coleta, config

st.set_page_config(page_title="LAB04 — Testes de Hipótese", layout="wide")


@st.cache_data
def dados_reais():
    """PRs reais (grupo, horas) ou None se o CSV ainda não foi gerado (Issue #5)."""
    try:
        return coleta.carregar_dados_reais()
    except FileNotFoundError:
        return None

SECOES = [
    ("cenario", "1. Cenário"),
    ("dados", "2. Os dados"),
    ("como-funcionam", "3. Como os testes funcionam"),
    ("erro-tipo-i", "4. Erro tipo I"),
    ("poder", "5. Poder"),
    ("dados-reais", "6. Dados reais"),
    ("conclusao", "7. Conclusão"),
]


def pendente(valor: str) -> bool:
    return not valor or valor.startswith("<")


def aviso_pendente(o_que: str, issue: str) -> None:
    st.info(f"⏳ {o_que} — pendente ({issue}).")


def texto(conteudo: str, issue: str) -> None:
    """Texto curto (2–4 frases) que acompanha cada seção."""
    if pendente(conteudo):
        aviso_pendente("Texto da seção", issue)
    else:
        st.markdown(conteudo)


def secao(ancora: str, titulo: str, entrega: str) -> None:
    st.divider()
    st.header(titulo, anchor=ancora)
    st.caption(f"Entrega: {entrega}")


# ── Cabeçalho ────────────────────────────────────────────────────────────────
st.title("LAB04 — Testes de hipótese por dentro")
st.caption(
    f"{config.NOMES_TESTES['welch']} × {config.NOMES_TESTES['mann_whitney']} · "
    "tempo até o merge de PRs com e sem bot de revisão"
)
st.markdown(
    f"**Repositório:** [{config.REPO_URL}]({config.REPO_URL}) · "
    f"**GitHub Projects:** [{config.PROJECT_URL}]({config.PROJECT_URL}) · "
    f"**Dashboard:** {config.DASHBOARD_URL}"
)

with st.sidebar:
    st.subheader("Seções")
    st.markdown("\n".join(f"- [{titulo}](#{ancora})" for ancora, titulo in SECOES))
    st.caption(f"Semente: {config.SEED} · α = {config.ALPHA} · {config.N_SIM:,} simulações".replace(",", "."))

# ── 1. Cenário ───────────────────────────────────────────────────────────────
secao(*SECOES[0], "Sprint 1")
if pendente(cenario.PERGUNTA):
    aviso_pendente("Pergunta, H₀, H₁ e caudas", "Issue #7")
else:
    st.markdown(f"**Pergunta:** {cenario.PERGUNTA}")
    st.markdown(f"**H₀:** {cenario.H0}")
    st.markdown(f"**H₁:** {cenario.H1}")
    st.markdown(f"**Caudas:** {cenario.CAUDAS}")
texto(getattr(cenario, "TEXTO_DADOS_REAIS", ""), "Issue #5 — fonte e nº de observações")

# ── 2. Os dados (G1) ─────────────────────────────────────────────────────────
secao(*SECOES[1], "Sprint 1")
aviso_pendente("Gráfico G1 — dados reais × simulados", "Issue #3")
texto(getattr(cenario, "TEXTO_G1", ""), "Issues #3 e #6")
with st.expander("Checagem do ajuste: estatísticas descritivas e QQ-plot dos dados reais"):
    reais = dados_reais()
    if reais is None:
        aviso_pendente("Dados reais", "Issue #5")
    else:
        tabela = analise.descritiva(reais).rename(
            index=analise.ROTULOS,
            columns={"mediana": "mediana (h)", "media": "média (h)", "dp": "dp (h)", "q1": "Q1 (h)",
                     "q3": "Q3 (h)", "max": "máx. (h)", "assimetria_log": "assimetria de ln(h)",
                     "outliers": "outliers (IQR)", "outliers_log": "outliers em ln(h)"},
        )
        st.dataframe(tabela.style.format(precision=2))
        st.plotly_chart(analise.qq_lognormal(reais, cenario.PARAMS))
        st.caption("Se os pontos seguem a reta tracejada, ln(horas) é aproximadamente normal, "
                   "ou seja, a lognormal com os parâmetros de `cenario.PARAMS` descreve bem o grupo.")

# ── 3. Como os testes funcionam (G2) ─────────────────────────────────────────
secao(*SECOES[2], "Sprint 1")
aviso_pendente("Gráfico G2 — estatística sob H₀, região de rejeição e p-valor", "Issue #4")
texto(getattr(cenario, "TEXTO_G2", ""), "Issues #4 e #9")

# ── 4. Erro tipo I (G3) ──────────────────────────────────────────────────────
secao(*SECOES[3], "Sprint 2")
aviso_pendente("Gráfico G3 — erro tipo I por situação", "Sprint 2")

# ── 5. Poder (G4) ────────────────────────────────────────────────────────────
secao(*SECOES[4], "Sprint 2")
aviso_pendente("Gráfico G4 — curvas de poder", "Sprint 2")

# ── 6. Dados reais (tabela) ──────────────────────────────────────────────────
secao(*SECOES[5], "Entrega final")
aviso_pendente("Tabela: estatística, p-valor, tamanho do efeito e conclusão", "Entrega final")

# ── 7. Conclusão ─────────────────────────────────────────────────────────────
secao(*SECOES[6], "Entrega final")
if pendente(cenario.EXPECTATIVA_PREVIA):
    aviso_pendente("Expectativa prévia do grupo", "Issue #7")
else:
    st.markdown(f"**O que esperávamos antes de simular:** {cenario.EXPECTATIVA_PREVIA}")
aviso_pendente("O que encontramos e recomendação", "Entrega final")
