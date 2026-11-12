"""Gera images/*.png e README.md (dashboard estático) a partir de data/processed/ (rode simulate.py antes)."""
import json, pathlib
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
P, RAW, IMG = ROOT/'data/processed', ROOT/'data/raw', ROOT/'images'
IMG.mkdir(exist_ok=True)
DASHBOARD_URL = '<preencher>'   # link do dashboard (README publicado)
REPO_URL = '<preencher>'        # link do repositório / GitHub Projects
show = lambda u: u if u.startswith('http') else '`<preencher>`'
W, M, CB, SB, RED = '#2a6fbb', '#e8833a', '#2e8b57', '#8e5ea2', '#d62839'   # Welch, MW, com bot, sem bot, rejeição
s = json.load(open(P/'real_stats.json'))
sim = pd.read_csv(P/'simulacao.csv'); h0 = pd.read_csv(P/'h0_stats.csv')
real = pd.read_csv(RAW/'prs_reais.csv')
a = real[real.grupo == 'com_bot'].horas_ate_merge.values
b = real[real.grupo == 'sem_bot'].horas_ate_merge.values
SC = list(sim.cenario.unique()); LAB = {k: sim[sim.cenario == k].rotulo.iloc[0] for k in SC}
pct = lambda v, n=1: f'{v*100:.{n}f}'.replace('.', ',')
num = lambda v, n=1: f'{v:.{n}f}'.replace('.', ',')

t_out = (np.abs(h0.t) > stats.t.ppf(.975, 57)).mean(); z_out = (np.abs(h0.z) > 1.96).mean()
# ---------- Textos (números calculados dos resultados) ----------
gi = lambda k, d, c: sim[(sim.cenario == k) & (sim.d == d)][c].iloc[0]
t1 = {k: (gi(k, 0, 'welch_05'), gi(k, 0, 'mw_05')) for k in SC}
mw_rng = (min(v[1] for v in t1.values()), max(v[1] for v in t1.values()))
adv_s1 = max((sim[sim.cenario == 'S1'].welch_05-sim[sim.cenario == 'S1'].mw_05)*100)
T = dict(
 dados=f'Os dois grupos são fortemente assimétricos à direita: a média (com bot {num(s["mean_com"])} h; sem bot {num(s["mean_sem"])} h) fica muito acima da mediana ({num(s["med_com"])} h e {num(s["med_sem"])} h), há PRs de até {num(s["max_com"],0)} h e o teste de Shapiro-Wilk rejeita normalidade (p < 0,001). Na escala log o formato fica quase simétrico, então usamos uma lognormal. Os parâmetros vieram dos dados: μ = {num(s["logmu_sem"],2)} (log-média do grupo sem bot) e σ = {num(s["sigma"],2)} (média dos desvios do log dos dois grupos). Com só 30 PRs por grupo o histograma real é irregular, mas cobre a mesma faixa (de minutos a semanas) e tem a mesma cauda longa da curva simulada.',
 g2=f'O t de Welch compara as médias dos grupos e o Mann-Whitney compara postos (se um grupo tende a ter valores maiores que o outro). O gráfico mostra a distribuição de cada estatística quando H₀ é verdadeira, obtida em 20.000 experimentos simulados; as caudas em vermelho formam a região de rejeição, bicaudal porque o bot poderia acelerar ou atrasar. Nos dados reais, a área hachurada dá p = {num(s["p_welch"],2)} (Welch) e p = {num(s["p_mw"],2)} (Mann-Whitney): sem efeito, diferenças assim ou maiores apareceriam em {pct(s["p_welch"],0)}% e {pct(s["p_mw"],0)}% dos experimentos. Isso não é a probabilidade de H₀ ser verdadeira nem prova de que o bot não tem efeito. Atenção: com dados tão assimétricos, só {pct(t_out)}% das estatísticas t caem na região de rejeição, em vez de 5%.'.replace('.', '.'),
 g3=f'O Mann-Whitney ficou entre {pct(mw_rng[0])}% e {pct(mw_rng[1])}% em todos os cenários, sempre um pouco abaixo de 5% (provavelmente por usarmos a aproximação normal com correção de continuidade), sem nunca ficar liberal; o erro de simulação é de ±0,4 p.p. O t de Welch ficou perto de 5% só com dados normais ({pct(t1["S1"][0])}%) e se afastou para baixo nos demais: {pct(t1["S2"][0])}% (S2), {pct(t1["S5"][0])}% (S5), {pct(t1["S3"][0])}% (S3) e {pct(t1["S4"][0])}% (S4, n = 10). Ele ficou conservador: a estatística t é dominada por poucos valores extremos e raramente cruza o valor crítico, então erra pouco, mas ao custo de poder. Use o botão para ver o erro tipo I com α = 1%.',
 g4=f'Com dados normais (S1) os testes têm poder quase igual, com leve vantagem do Welch (até {num(adv_s1)} p.p.). Em todas as outras situações o Mann-Whitney detecta melhor, e a diferença cresce com o efeito: com d = 1, ele chega a {pct(gi("S3",1.0,"mw_05"),0)}% contra {pct(gi("S3",1.0,"welch_05"),0)}% do Welch no cenário real (S3), e a {pct(gi("S4",1.0,"mw_05"),0)}% contra {pct(gi("S4",1.0,"welch_05"),0)}% com n = 10. A vantagem muda de lado apenas quando os dados são normais. Com α = 1% (botão), todas as curvas descem, mas a ordem se mantém (S3, d = 1: {pct(gi("S3",1.0,"mw_01"),0)}% contra {pct(gi("S3",1.0,"welch_01"),0)}%).',
)

def pv(p): return f'{p:.3f}'.replace('.', ',')
tab = (f"| Teste | Compara | Estatística | p-valor | Tamanho do efeito | Conclusão (α = 5%) |\n|---|---|---|---|---|---|\n"
 f"| t de Welch | médias | t = {num(s['t'],2)} (gl = {num(s['df'])}) | {pv(s['p_welch'])} | diferença de médias = {num(s['mean_com']-s['mean_sem'])} h; d de Cohen = {num(s['d_cohen'],2)} | Não rejeita H₀ |\n"
 f"| Mann-Whitney | postos | U = {s['U']:.0f} (z = {num(s['z'],2)}) | {pv(s['p_mw'])} | delta de Cliff = {num(s['cliff'],2)}; razão de medianas = {num(s['ratio_med'],2)} (IC95% {num(s['ratio_lo'],2)} a {num(s['ratio_hi'],2)}) | Não rejeita H₀ |")
real_txt = f'Os dois testes chegam à mesma conclusão: não há evidência de que o bot mude o tempo até o merge (p = {pv(s["p_welch"])} e {pv(s["p_mw"])}). O efeito não tem importância prática clara: a média é maior com bot ({num(s["mean_com"])} h contra {num(s["mean_sem"])} h), mas a mediana é menor ({num(s["med_com"])} h contra {num(s["med_sem"])} h), e a probabilidade de um PR com bot ser mais lento que um sem bot é de cerca de 52% (delta de Cliff = {num(s["cliff"],2)}). O intervalo da razão de medianas ({num(s["ratio_lo"],2)} a {num(s["ratio_hi"],2)}) inclui efeitos grandes nos dois sentidos, ou seja, com 30 PRs por grupo o estudo tem pouco poder para decidir. Como os grupos vêm de períodos diferentes (antes e depois do bot), mesmo uma diferença não seria atribuível só ao bot.'

plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 170, 'axes.titleweight': 'bold'})
rng = np.random.default_rng(5)

# G1
fig, ax = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
bins = np.linspace(-1.2, 3.4, 24)
for j, (x, mu, c, nome) in enumerate([(a, s['logmu_com'], CB, 'Com bot'), (b, s['logmu_sem'], SB, 'Sem bot')]):
    ax[j].hist(np.log10(x), bins=bins, density=True, color=c, alpha=.8, edgecolor='white', label='Real (n=30)')
    h, e = np.histogram(rng.normal(mu, s['sigma'], 50000)/np.log(10), bins=bins, density=True)
    ax[j].plot((e[:-1]+e[1:])/2, h, 'k-o', ms=3.5, lw=2, label='Simulado (lognormal)')
    ax[j].axvline(np.log10(np.median(x)), color=c, ls='--'); ax[j].set_title(f'{nome} (mediana {np.median(x):.0f} h)')
    ax[j].set_xticks([-1, 0, 1, 2, 3]); ax[j].set_xticklabels(['0,1', '1', '10', '100', '1000']); ax[j].set_xlabel('Horas até o merge (h, escala log)')
ax[0].set_ylabel('Densidade (na escala log10)'); ax[0].legend(frameon=False)
fig.suptitle('G1 — Dados reais × dados simulados', fontweight='bold'); fig.tight_layout(); fig.savefig(IMG/'g1.png'); plt.close()

# G2
def panel(ax, sim_stat, theo, crit, obs, pobs, lim, col, xl, title):
    bb = np.linspace(-lim, lim, 71)
    ax.hist(np.clip(sim_stat, -lim, lim), bins=bb, density=True, color=col, alpha=.4, label='Simulado sob H₀')
    xs = np.linspace(-lim, lim, 600); ax.plot(xs, theo(xs), 'k', lw=1.6, label='Densidade teórica')
    ax.fill_between(xs, 0, theo(xs), where=np.abs(xs) >= crit, color=RED, alpha=.45, label='Região de rejeição (α = 5%)')
    ax.fill_between(xs, 0, theo(xs), where=np.abs(xs) >= abs(obs), facecolor='none', edgecolor='k', hatch='///', lw=0, label=f'p-valor do exemplo = {pobs:.3f}'.replace('.', ','))
    ax.axvline(obs, color='k', lw=2.2); ax.set_xlabel(xl); ax.set_ylabel('Densidade'); ax.set_title(title)
    ax.set_ylim(0, ax.get_ylim()[1]*1.45); ax.legend(frameon=False, fontsize=8.5, loc='upper left')
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
panel(ax[0], h0.t.values, lambda v: stats.t.pdf(v, 57), stats.t.ppf(.975, 57), s['t'], s['p_welch'], 6, W, 'Estatística t (adimensional)', 't de Welch (compara médias)')
panel(ax[1], h0.z.values, stats.norm.pdf, 1.96, s['z'], s['p_mw'], 5, M, 'Estatística z (adimensional)', 'Mann-Whitney (compara postos)')
fig.suptitle('G2 — Estatística sob H₀ (S3, n = 30), região de rejeição e p-valor dos dados reais', fontweight='bold'); fig.tight_layout(); fig.savefig(IMG/'g2.png'); plt.close()

# G3 (α = 5% e 1%)
r0 = sim[sim.d == 0].reset_index(drop=True); xi = np.arange(len(r0))
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for k, (al, nom) in enumerate((('05', 5), ('01', 1))):
    for off, t, c, lab in ((-.2, 'welch', W, 't de Welch'), (.2, 'mw', M, 'Mann-Whitney')):
        v = r0[f'{t}_{al}']*100; bars = ax[k].bar(xi+off, v, .38, color=c, label=lab)
        for bb_, q in zip(bars, v): ax[k].text(bb_.get_x()+.19, q+.05*nom, f'{q:.1f}'.replace('.', ','), ha='center', fontsize=8.5)
    ax[k].axhline(nom, color=RED, ls='--', label=f'α nominal = {nom}%'); ax[k].set_ylim(0, nom*1.45)
    ax[k].set_xticks(xi); ax[k].set_xticklabels(SC); ax[k].set_xlabel('Cenário (S1 normal; S2–S4 lognormais; S5 outliers)'); ax[k].set_ylabel('Rejeições com H₀ verdadeira (%)'); ax[k].set_title(f'α = {nom}%')
ax[0].legend(frameon=False, fontsize=9, loc='lower left')
fig.suptitle('G3 — Erro tipo I dos dois testes em cada cenário', fontweight='bold'); fig.tight_layout(); fig.savefig(IMG/'g3.png'); plt.close()

# G4
fig, axs = plt.subplots(2, 3, figsize=(13, 7.2), sharey=True)
for ax, k in zip(axs.ravel(), SC):
    d_ = sim[sim.cenario == k]
    for al, ls, alpha in (('05', '-', 1), ('01', '--', .6)):
        ax.plot(d_.d, d_[f'welch_{al}']*100, ls, marker='o', color=W, alpha=alpha, lw=2.2, ms=4)
        ax.plot(d_.d, d_[f'mw_{al}']*100, ls, marker='s', color=M, alpha=alpha, lw=2.2, ms=4)
    ax.axhline(80, color='gray', ls=':'); ax.set_title(LAB[k], fontsize=10.5); ax.set_xlabel('Tamanho do efeito d (desvios-padrão)')
for ax in axs[:, 0]: ax.set_ylabel('Poder = rejeições (%)')
from matplotlib.lines import Line2D
axs[1, 2].axis('off')
axs[1, 2].legend(handles=[Line2D([], [], color=W, marker='o', lw=2.2, label='t de Welch'), Line2D([], [], color=M, marker='s', lw=2.2, label='Mann-Whitney'),
    Line2D([], [], color='k', lw=2, label='α = 5% (linha cheia)'), Line2D([], [], color='k', ls='--', lw=2, alpha=.6, label='α = 1% (tracejada)'), Line2D([], [], color='gray', ls=':', label='poder de 80%')], loc='center', frameon=False, fontsize=11)
fig.suptitle('G4 — Curvas de poder: proporção de rejeições × tamanho do efeito', fontweight='bold'); fig.tight_layout(); fig.savefig(IMG/'g4.png'); plt.close()

# README.md

md = f'''# Welch × Mann-Whitney: qual teste usar para o tempo até o merge de PRs?

Laboratório 04 · Testes de hipótese por simulação · Engenharia de Software

- **Dashboard:** {show(DASHBOARD_URL)}
- **Repositório / GitHub Projects:** {show(REPO_URL)}

> Este README é o dashboard. Os gráficos são gerados por código: `pip install -r requirements.txt && python build.py`.

## 1. Cenário

**Pergunta:** o tempo até o merge de um Pull Request muda quando o repositório passa a usar um bot de revisão automática (CodeRabbit)?

**H₀:** o bot não muda o tempo até o merge (médias iguais para o Welch; mesma chance de um PR ser mais lento ou mais rápido para o Mann-Whitney).
**H₁:** o bot muda o tempo até o merge, para mais ou para menos (teste bicaudal).

**Dados reais:** PRs com merge do repositório público formbricks/formbricks (GitHub), em horas entre abertura e merge. Foram coletados **{int(s["n_com"])} PRs com bot** (set. a nov. de 2024, revisados pelo coderabbitai) e **{int(s["n_sem"])} sem bot** (mai. a ago. de 2024), a partir de uma lista de 541 candidatos (`data/raw/prs_candidatos.csv`). Excluímos PRs abertos por bots, merges em menos de 1 minuto e PRs não revisados pelo bot após a adoção.

## 2. Os dados (G1)

![G1](images/g1.png)

{T["dados"]}

| Cenário | Distribuição | n por grupo | Finalidade |
|---|---|---|---|
| S1 | Normal(60; 20) | 30 | Pressupostos do Welch atendidos |
| S2 | Lognormal, σ = 1,0 | 30 | Assimetria moderada |
| S3 | Lognormal, σ = {num(s["sigma"],2)} (real) | 30 | Assimetria igual à dos dados reais |
| S4 | Lognormal, σ = {num(s["sigma"],2)} (real) | 10 | Assimetria e amostra pequena |
| S5 | Normal com 10% de outliers | 30 | Caudas pesadas |

## 3. Como os testes funcionam (G2)

![G2](images/g2.png)

{T["g2"]}

## 4. Erro tipo I (G3)

![G3](images/g3.png)

{T["g3"].replace(" Use o botão para ver o erro tipo I com α = 1%.", " O painel da direita mostra o mesmo com α = 1%.")}

## 5. Poder (G4)

![G4](images/g4.png)

{T["g4"].replace("Com α = 1% (botão),", "Com α = 1% (linhas tracejadas),")}

## 6. Dados reais

{tab}

{real_txt}

## 7. Conclusão

**Esperávamos** que o Mann-Whitney se saísse melhor com dados assimétricos e com outliers, porque usa postos, e que os dois testes ficassem equivalentes com dados normais. **Encontramos** esse padrão, mas com uma diferença maior que a esperada: com a assimetria dos dados reais, o Welch quase não detecta efeitos ({pct(gi("S3",1.0,"welch_05"),0)}% de poder com d = 1) e fica conservador ({pct(t1["S3"][0])}% de erro tipo I), porque a média de uma lognormal com σ ≈ {num(s["sigma"],1)} é dominada por poucos PRs extremos.

**Recomendação:** usar o Mann-Whitney para comparar tempos de merge. Ele manteve o erro tipo I perto de 5% em todos os cenários e perdeu no máximo {num(adv_s1)} p.p. de poder com dados normais. **Mudaríamos para o Welch** se os dados fossem aproximadamente normais (por exemplo, tempos de build medidos várias vezes) ou se a pergunta fosse sobre a média, como o total de horas gasto. **Principal limitação:** os grupos são de períodos diferentes (antes e depois do bot), de um único repositório e com n = 30, e os dados simulados são uma aproximação (lognormal, mesma forma e mesmo σ nos dois grupos).

## Estrutura do repositório

- `src/simulate.py`: simulação Monte Carlo (semente 2026, 10.000 réplicas por ponto) e estatísticas dos dados reais → `data/processed/`
- `src/readme.py`: gera `images/` (G1 a G4) e este README
- `build.py`: executa tudo (`--resimular` refaz a simulação)
'''
(ROOT/'README.md').write_text(md, encoding='utf-8'); print('README.md', len(md))
