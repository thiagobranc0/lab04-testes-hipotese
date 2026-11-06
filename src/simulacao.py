"""Geração dos dados simulados — Issue #8."""
import numpy as np


def gerar_dados(n: int, params: dict, efeito: float, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Gera (com_bot, sem_bot), cada um com n tempos até o merge, em horas.

    Os dois grupos seguem uma lognormal com a mediana e o sigma do grupo "sem_bot".
    `efeito` é a redução relativa da mediana com bot: 0 → H0 verdadeira;
    0.2 → com bot, a mediana é 20% menor.
    """
    mediana, sigma = params["sem_bot"]["mediana"], params["sem_bot"]["sigma"]
    mu = np.log(mediana)
    sem_bot = rng.lognormal(mu, sigma, n)
    com_bot = rng.lognormal(mu + np.log(1 - efeito), sigma, n)
    return com_bot, sem_bot
