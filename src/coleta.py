"""Coleta dos PRs reais via API do GitHub — Issue #5 (papel A)."""
from pathlib import Path

import pandas as pd

CSV_REAIS = Path(__file__).resolve().parent.parent / "data" / "raw" / "prs_reais.csv"


def carregar_dados_reais() -> pd.DataFrame:
    """Retorna DataFrame com colunas `grupo` ("com_bot"/"sem_bot") e `horas`."""
    raise NotImplementedError("Issue #5")


if __name__ == "__main__":
    raise NotImplementedError("Issue #5: script de coleta")
