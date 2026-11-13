"""Simulação Monte Carlo: t de Welch × Mann-Whitney (par P1) — Issue #16.
Gera data/processed/{simulacao.csv, real_stats.json, h0_stats.csv}.

Tamanho do efeito d: nos cenários normais (S1, S5), um grupo é deslocado em d desvios-padrão;
nos lognormais (S2–S4), ln(horas) é deslocado em d·σ, ou seja, a mediana é multiplicada por e^(d·σ).
Os cenários lognormais com σ real usam a mediana e o σ do grupo sem bot (cenario.PARAMS, Issue #6).
"""
import json, pathlib, sys
import numpy as np, pandas as pd
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import cenario, config  # noqa: E402

RAW, OUT = ROOT/'data/raw', ROOT/'data/processed'
SEED, REPS = config.SEED, config.N_SIM
N_H0 = 20_000                                            # experimentos sob H0 para o G2
EFFECTS = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.8, 1.0]   # d: ver docstring
SCENARIOS = {  # chave: (gerador, n, rótulo)
    'S1': ('normal', 30, 'S1 Normal, n=30'),
    'S2': ('lognorm_1', 30, 'S2 Lognormal σ=1,0, n=30'),
    'S3': ('lognorm_real', 30, 'S3 Lognormal σ real, n=30'),
    'S4': ('lognorm_real', 10, 'S4 Lognormal σ real, n=10'),
    'S5': ('outliers', 30, 'S5 Normal + 10% outliers, n=30'),
}

def mann_whitney(x, y):
    """Mann-Whitney bicaudal vetorizado (aprox. normal, correção de continuidade)."""
    n1, n2 = x.shape[1], y.shape[1]
    r = stats.rankdata(np.concatenate([x, y], 1), axis=1)
    U = r[:, :n1].sum(1) - n1*(n1+1)/2
    m, s = n1*n2/2, np.sqrt(n1*n2*(n1+n2+1)/12)
    z = (U-m)/s
    p = 2*stats.norm.sf(np.maximum((np.abs(U-m)-.5)/s, 0))
    return p, z

def real_params():
    real = pd.read_csv(RAW/'prs_reais.csv')
    a = real[real.grupo == 'com_bot'].horas_ate_merge.values
    b = real[real.grupo == 'sem_bot'].horas_ate_merge.values
    la, lb = np.log(a), np.log(b)
    base = cenario.PARAMS['sem_bot']               # simulação usa o grupo sem bot nos dois grupos
    return real, a, b, la, lb, np.log(base['mediana']), base['sigma']

def make_generator(rng, mu_ref, sigma):
    def gen(kind, n, d, size):
        if kind == 'normal':
            mu, sd = 60, 20
            return rng.normal(mu, sd, (size, n)), rng.normal(mu+d*sd, sd, (size, n))
        if kind in ('lognorm_1', 'lognorm_real'):
            s = sigma if kind == 'lognorm_real' else 1.0
            return (np.exp(rng.normal(mu_ref, s, (size, n))),
                    np.exp(rng.normal(mu_ref+d*s, s, (size, n))))
        if kind == 'outliers':
            mu, sd = 60, 20
            def f(m):
                x = rng.normal(m, sd, (size, n)); o = rng.random((size, n)) < .10
                return np.where(o, m+rng.normal(0, 10*sd, (size, n)), x)
            return f(mu), f(mu+d*sd)
    return gen

def real_stats(a, b, la, lb, sigma, rng):
    tt = stats.ttest_ind(a, b, equal_var=False)
    mw = stats.mannwhitneyu(a, b, alternative='two-sided', method='asymptotic')
    n1, n2 = len(a), len(b)
    z = (mw.statistic-n1*n2/2)/np.sqrt(n1*n2*(n1+n2+1)/12)
    boot = [np.median(rng.choice(a, n1))/np.median(rng.choice(b, n2)) for _ in range(5000)]
    tl = stats.ttest_ind(la, lb, equal_var=False)
    sp = np.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
    out = dict(
        n_com=len(a), n_sem=len(b), mean_com=a.mean(), mean_sem=b.mean(), med_com=np.median(a), med_sem=np.median(b),
        sd_com=a.std(ddof=1), sd_sem=b.std(ddof=1), max_com=a.max(), max_sem=b.max(),
        skew_com=stats.skew(a), skew_sem=stats.skew(b),
        logmu_com=la.mean(), logmu_sem=lb.mean(), sd_log_com=la.std(ddof=1), sd_log_sem=lb.std(ddof=1), sigma=sigma,
        sw_com=stats.shapiro(a).pvalue, sw_sem=stats.shapiro(b).pvalue, sw_log_com=stats.shapiro(la).pvalue, sw_log_sem=stats.shapiro(lb).pvalue,
        t=tt.statistic, df=tt.df, p_welch=tt.pvalue, U=mw.statistic, z=z, p_mw=mw.pvalue,
        d_cohen=(a.mean()-b.mean())/sp, cliff=2*mw.statistic/(n1*n2)-1, ratio_med=np.median(a)/np.median(b),
        ratio_lo=np.percentile(boot, 2.5), ratio_hi=np.percentile(boot, 97.5),
        geo_ratio=np.exp(la.mean()-lb.mean()), p_t_log=tl.pvalue)
    return {k: float(v) for k, v in out.items()}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    real, a, b, la, lb, mu_ref, sigma = real_params()
    json.dump(real_stats(a, b, la, lb, sigma, rng), open(OUT/'real_stats.json', 'w'), indent=1)
    gen = make_generator(rng, mu_ref, sigma)
    rows = []
    for key, (kind, n, label) in SCENARIOS.items():
        for d in EFFECTS:
            x, y = gen(kind, n, d, REPS)
            pt = stats.ttest_ind(x, y, equal_var=False, axis=1).pvalue
            pm, _ = mann_whitney(x, y)
            rows.append(dict(cenario=key, rotulo=label, n=n, d=d,
                             welch_05=(pt < .05).mean(), mw_05=(pm < .05).mean(),
                             welch_01=(pt < .01).mean(), mw_01=(pm < .01).mean()))
        print('cenário', key, 'ok', flush=True)
    pd.DataFrame(rows).to_csv(OUT/'simulacao.csv', index=False)
    # G2: estatísticas sob H0 (cenário S3)
    x, y = gen('lognorm_real', 30, 0, N_H0)
    t = stats.ttest_ind(x, y, equal_var=False, axis=1).statistic
    _, z = mann_whitney(x, y)
    pd.DataFrame(dict(t=t, z=z)).to_csv(OUT/'h0_stats.csv', index=False)

if __name__ == '__main__':
    main()
