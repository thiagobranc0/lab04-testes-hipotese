"""Configuração global do experimento. Todos os módulos importam daqui."""

SEED = 42            # semente fixa: np.random.default_rng(SEED)
ALPHA = 0.05         # nível de significância
N_SIM = 10_000       # repetições por cenário de simulação

GRUPOS = ("com_bot", "sem_bot")

# Mesma cor para cada teste em TODOS os gráficos (paleta Okabe-Ito, segura para daltônicos)
CORES = {
    "welch": "#0072B2",         # azul
    "mann_whitney": "#E69F00",  # laranja
}
CORES_GRUPOS = {
    "com_bot": "#009E73",       # verde
    "sem_bot": "#CC79A7",       # rosa
}
NOMES_TESTES = {
    "welch": "t de Welch",
    "mann_whitney": "Mann-Whitney",
}

REPO_URL = "https://github.com/thiagobranc0/lab04-testes-hipotese"
PROJECT_URL = "https://github.com/users/thiagobranc0/projects/1"
DASHBOARD_URL = "https://github.com/thiagobranc0/lab04-testes-hipotese#readme"  # o README é o dashboard
