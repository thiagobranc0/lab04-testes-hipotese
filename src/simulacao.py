"""Geração dos dados simulados — Issue #8 (papel B)."""
import numpy as np


def gerar_dados(n: int, params: dict, efeito: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Gera (com_bot, sem_bot) com n observações cada.

    efeito = 0 → H0 verdadeira; efeito > 0 multiplica a mediana de um dos grupos.
    """
    raise NotImplementedError("Issue #8")
