"""Coleta dos PRs reais via API de busca do GitHub — Issue #5 (papel A).

Desenho "antes × depois da adoção do bot", num único repositório público:

- sem_bot: PRs mergeados criados nos JANELA_DIAS dias anteriores à ADOCAO do bot,
  sem comentário/revisão de nenhum bot da lista fechada BOTS_REVISAO;
- com_bot: PRs mergeados criados nos JANELA_DIAS dias seguintes ao período de
  transição (TRANSICAO_DIAS após a ADOCAO), comentados ou revisados pelo BOT.

Dos PRs elegíveis de cada grupo, sorteamos N_POR_GRUPO com a semente fixa do projeto.
Critérios e resultado da coleta estão documentados em data/FONTE.md.

Uso (a partir da raiz do repositório):
    python -m src.coleta

GITHUB_TOKEN (variável de ambiente ou linha no arquivo .env) é opcional, mas sem ele
a API de busca aceita só 10 consultas por minuto.
"""
from __future__ import annotations

import os
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from src import config

RAIZ = Path(__file__).resolve().parent.parent
CSV_REAIS = RAIZ / "data" / "raw" / "prs_reais.csv"
CSV_CANDIDATOS = RAIZ / "data" / "raw" / "prs_candidatos.csv"

# ── Parâmetros da coleta (ver data/FONTE.md) ─────────────────────────────────
REPO = "formbricks/formbricks"
BOT = "coderabbitai"                 # slug do GitHub App; o login aparece como "coderabbitai[bot]"
# Lista fechada de bots de REVISÃO (bots de CI, cobertura, deploy etc. não contam)
BOTS_REVISAO = (
    "coderabbitai",
    "copilot-pull-request-reviewer",
    "sourcery-ai",
    "ellipsis-dev",
    "greptile-apps",
)
ADOCAO = date(2024, 8, 19)           # criação do 1º PR comentado pelo BOT no repositório
JANELA_DIAS = 90                     # tamanho de cada janela (antes e depois)
TRANSICAO_DIAS = 14                  # dias após a adoção que ficam fora das duas janelas
N_POR_GRUPO = 30                     # enunciado: ~30 observações por grupo
MIN_HORAS = 1 / 60                   # merges em menos de 1 minuto são automáticos → excluídos

COLUNAS = ["grupo", "repo", "pr_number", "created_at", "merged_at", "horas_ate_merge", "bot"]

API = "https://api.github.com"
PAUSA_S = 2.5                        # pausa entre consultas, para não cair no limite secundário


def janelas() -> dict[str, tuple[date, date]]:
    """Intervalos (inclusivos) de criação dos PRs de cada grupo."""
    inicio_depois = ADOCAO + timedelta(days=TRANSICAO_DIAS)
    return {
        "sem_bot": (ADOCAO - timedelta(days=JANELA_DIAS), ADOCAO - timedelta(days=1)),
        "com_bot": (inicio_depois, inicio_depois + timedelta(days=JANELA_DIAS - 1)),
    }


# ── Acesso à API ─────────────────────────────────────────────────────────────

def _token() -> str | None:
    token = os.environ.get("GITHUB_TOKEN")
    arquivo_env = RAIZ / ".env"
    if not token and arquivo_env.exists():
        for linha in arquivo_env.read_text(encoding="utf-8").splitlines():
            if linha.strip().startswith("GITHUB_TOKEN="):
                token = linha.split("=", 1)[1].strip().strip("'\"")
    return token or None


def _sessao():
    import requests  # só a coleta precisa de requests; o dashboard não

    s = requests.Session()
    s.headers.update({
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "lab04-testes-hipotese",
    })
    if token := _token():
        s.headers["Authorization"] = f"Bearer {token}"
    return s


def _espera(resposta) -> float:
    """Segundos a esperar depois de um 403/429 de limite de requisições."""
    if "Retry-After" in resposta.headers:
        return float(resposta.headers["Retry-After"]) + 1
    if resposta.headers.get("X-RateLimit-Remaining") == "0":
        return max(0.0, float(resposta.headers["X-RateLimit-Reset"]) - time.time()) + 1
    return 60.0  # limite secundário: a API não diz quanto esperar


def _get(sessao, url: str, params: dict, tentativas: int = 6):
    for _ in range(tentativas):
        r = sessao.get(url, params=params, timeout=30)
        if r.status_code == 200:
            time.sleep(PAUSA_S)
            return r
        if r.status_code in (403, 429):
            espera = _espera(r)
            print(f"  limite da API atingido; aguardando {espera:.0f} s…", flush=True)
            time.sleep(espera)
            continue
        r.raise_for_status()
    raise RuntimeError(f"Falha repetida ao consultar {url} com {params}")


def buscar_prs(sessao, consulta: str) -> list[dict]:
    """Todos os resultados de uma consulta à busca de issues/PRs (máx. 1000)."""
    itens: list[dict] = []
    pagina = 1
    while True:
        dados = _get(sessao, f"{API}/search/issues", {
            "q": consulta, "per_page": 100, "page": pagina, "sort": "created", "order": "asc",
        }).json()
        if dados.get("incomplete_results"):
            print(f"  aviso: resultados incompletos para '{consulta}'", flush=True)
        itens += dados["items"]
        if len(itens) >= dados["total_count"] or not dados["items"]:
            return itens
        if len(itens) >= 1000:
            raise RuntimeError(f"Mais de 1000 resultados para '{consulta}'; reduza a janela.")
        pagina += 1


def _numeros_com_bot(sessao, base: str, bot: str) -> set[int]:
    """PRs da consulta-base que o bot comentou OU revisou."""
    numeros: set[int] = set()
    for qualificador in ("commenter", "reviewed-by"):
        numeros |= {it["number"] for it in buscar_prs(sessao, f"{base} {qualificador}:app/{bot}")}
    return numeros


# ── Coleta ───────────────────────────────────────────────────────────────────

def coletar_candidatos(sessao=None) -> pd.DataFrame:
    """Todos os PRs mergeados das duas janelas, com o motivo de exclusão (vazio = elegível)."""
    sessao = sessao or _sessao()
    linhas = []
    for grupo, (ini, fim) in janelas().items():
        base = f"repo:{REPO} is:pr is:merged created:{ini.isoformat()}..{fim.isoformat()}"
        print(f"[{grupo}] PRs criados de {ini} a {fim}", flush=True)
        prs = buscar_prs(sessao, base)
        bots_por_pr: dict[int, list[str]] = {}
        for bot in (BOTS_REVISAO if grupo == "sem_bot" else (BOT,)):
            for numero in _numeros_com_bot(sessao, base, bot):
                bots_por_pr.setdefault(numero, []).append(f"{bot}[bot]")
        print(f"  {len(prs)} PRs mergeados; {len(bots_por_pr)} com bot de revisão", flush=True)

        for it in prs:
            criado = pd.Timestamp(it["created_at"])
            mergeado = pd.Timestamp(it["pull_request"]["merged_at"])
            horas = (mergeado - criado).total_seconds() / 3600
            bots = bots_por_pr.get(it["number"], [])
            if it["user"]["type"] == "Bot":
                motivo = "autor do PR é bot"
            elif horas < MIN_HORAS:
                motivo = "merge em menos de 1 minuto"
            elif grupo == "sem_bot" and bots:
                motivo = "bot de revisão antes da adoção"
            elif grupo == "com_bot" and not bots:
                motivo = "não revisado pelo bot após a adoção"
            else:
                motivo = ""
            linhas.append({
                "grupo": grupo, "repo": REPO, "pr_number": it["number"],
                "autor": it["user"]["login"], "created_at": it["created_at"],
                "merged_at": it["pull_request"]["merged_at"], "horas_ate_merge": round(horas, 4),
                "bot": ";".join(sorted(bots)) or "nenhum", "motivo_exclusao": motivo,
            })
    return pd.DataFrame(linhas).sort_values(["grupo", "pr_number"], ignore_index=True)


def amostrar(candidatos: pd.DataFrame, n: int = N_POR_GRUPO, seed: int = config.SEED) -> pd.DataFrame:
    """Sorteia n PRs elegíveis por grupo, de forma reprodutível (mesma semente → mesma amostra)."""
    rng = np.random.default_rng(seed)
    elegiveis = candidatos[candidatos["motivo_exclusao"] == ""]
    partes = []
    for grupo in config.GRUPOS:
        g = elegiveis[elegiveis["grupo"] == grupo].sort_values("pr_number", ignore_index=True)
        if len(g) < n:
            raise ValueError(f"Só {len(g)} PRs elegíveis em '{grupo}' (precisamos de {n}).")
        idx = np.sort(rng.choice(len(g), size=n, replace=False))
        partes.append(g.iloc[idx])
    return pd.concat(partes, ignore_index=True)[COLUNAS]


def carregar_dados_reais(caminho: Path = CSV_REAIS) -> pd.DataFrame:
    """Retorna DataFrame com colunas `grupo` ("com_bot"/"sem_bot") e `horas`."""
    if not caminho.exists():
        raise FileNotFoundError(f"{caminho} não encontrado. Gere-o com: python -m src.coleta")
    df = pd.read_csv(caminho)
    faltando = set(COLUNAS) - set(df.columns)
    if faltando:
        raise ValueError(f"Colunas ausentes em {caminho.name}: {sorted(faltando)}")
    df = df.rename(columns={"horas_ate_merge": "horas"})[["grupo", "horas"]]
    if not set(df["grupo"]) <= set(config.GRUPOS):
        raise ValueError(f"Grupos inesperados: {sorted(set(df['grupo']) - set(config.GRUPOS))}")
    if not (df["horas"] > 0).all():
        raise ValueError("Há tempos até o merge ≤ 0 horas.")
    return df.reset_index(drop=True)


def main() -> None:
    candidatos = coletar_candidatos()
    amostra = amostrar(candidatos)
    CSV_REAIS.parent.mkdir(parents=True, exist_ok=True)
    candidatos.to_csv(CSV_CANDIDATOS, index=False)
    amostra.to_csv(CSV_REAIS, index=False)

    print("\nResumo da coleta")
    resumo = (candidatos.assign(motivo=candidatos["motivo_exclusao"].replace("", "elegível"))
              .groupby(["grupo", "motivo"]).size())
    print(resumo.to_string())
    print(f"\nAmostra ({N_POR_GRUPO} por grupo, semente {config.SEED}) → {CSV_REAIS.relative_to(RAIZ)}")
    print(amostra.groupby("grupo")["horas_ate_merge"].describe().round(2).to_string())


if __name__ == "__main__":
    main()
