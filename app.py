"""Dashboard do LAB04. Executar: streamlit run app.py"""
import streamlit as st

from src import config

st.set_page_config(page_title="LAB04 — Testes de Hipótese", layout="wide")

st.title("LAB04 — Testes de hipótese por dentro")
st.caption("t de Welch × Mann-Whitney · tempo até o merge de PRs com e sem bot de revisão")
st.markdown(
    f"**Repositório:** {config.REPO_URL} · "
    f"**GitHub Projects:** {config.PROJECT_URL} · "
    f"**Dashboard:** {config.DASHBOARD_URL}"
)

st.info("Em construção — as 7 seções do dashboard entram na Issue #2.")
