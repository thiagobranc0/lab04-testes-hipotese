"""Gera images/*.png e README.md (o dashboard) — Issues #17 e #18.

Lê os resultados de data/processed/ (gerados por src/simulate.py), os dados reais de
data/raw/ e os textos/parâmetros de src/cenario.py. Rode tudo com: python build.py
"""
import json, pathlib, sys
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy import stats

ROOT = pathlib.Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from src import cenario, config, simulacao, testes  # noqa: E402

P, RAW, IMG = ROOT/'data/processed', ROOT/'data/raw', ROOT/'images'
IMG.mkdir(exist_ok=True)
W, M = config.CORES['welch'], config.CORES['mann_whitney']                    # mesma cor por teste
CB, SB = config.CORES_GRUPOS['com_bot'], config.CORES_GRUPOS['sem_bot']
RED = '#d62839'                                                               # região de rejeição
PARAMS = cenario.PARAMS
SIGMA = PARAMS['sem_bot']['sigma']                                            # σ dos cenários S3 e S4

s = json.load(open(P/'real_stats.json', encoding='utf-8'))
sim = pd.read_csv(P/'simulacao.csv'); h0 = pd.read_csv(P/'h0_stats.csv')
real = pd.read_csv(RAW/'prs_reais.csv')
a = real[real.grupo == 'com_bot'].horas_ate_merge.values
b = real[real.grupo == 'sem_bot'].horas_ate_merge.values
n_cand = len(pd.read_csv(RAW/'prs_candidatos.csv'))
SC = list(sim.cenario.unique()); LAB = {k: sim[sim.cenario == k].rotulo.iloc[0] for k in SC}
pct = lambda v, n=1: f'{v*100:.{n}f}'.replace('.', ',')
num = lambda v, n=1: f'{v:.{n}f}'.replace('.', ',')
pv = lambda p: f'{p:.3f}'.replace('.', ',')
decisao = lambda r: 'Rejeita H₀' if r['rejeita'] else 'Não rejeita H₀'
gi = lambda k, d, c: sim[(sim.cenario == k) & (sim.d == d)][c].iloc[0]

# ---------- Números usados nos textos ----------
t_out = (np.abs(h0.t) > stats.t.ppf(.975, 57)).mean()
t1 = {k: (gi(k, 0, 'welch_05'), gi(k, 0, 'mw_05')) for k in SC}
mw_rng = (min(v[1] for v in t1.values()), max(v[1] for v in t1.values()))
s1 = sim[sim.cenario == 'S1']
adv_s1 = max((s1.welch_05 - s1.mw_05)*100)
outros = sim[(sim.cenario != 'S1') & (sim.d > 0)]
# As frases abaixo descrevem padrões dos resultados; se a simulação mudar, o build avisa.
assert 0.04 < mw_rng[0] and mw_rng[1] < 0.05, 'texto do G3: Mann-Whitney "um pouco abaixo de 5%"'
assert all(t1[k][0] < t1['S1'][0] for k in SC if k != 'S1'), 'texto do G3: Welch abaixo de S1 nos demais'
assert adv_s1 > 0 and (outros.mw_05 >= outros.welch_05).all(), 'texto do G4: vantagem só muda com dados normais'
assert gi('S3', 1.0, 'mw_01') > gi('S3', 1.0, 'welch_01'), 'texto do G4: ordem mantida com α = 1%'

# Exemplo com UM conjunto simulado (Sprint 1, Issue #9): mediana com bot 30% menor
EFEITO_EX, N_EX = 0.3, 30
ex = testes.aplicar_testes(*simulacao.gerar_dados(N_EX, PARAMS, EFEITO_EX, np.random.default_rng(config.SEED)))
d_ex = -np.log(1 - EFEITO_EX)/SIGMA
r_real = testes.aplicar_testes(a, b)                                          # dados reais (seção 6)

T = dict(
 g2=(f'O t de Welch compara as médias dos grupos, e o Mann-Whitney compara postos, isto é, se um grupo tende a ter '
     f'valores maiores que o outro. O gráfico mostra a distribuição de cada estatística quando H₀ é verdadeira '
     f'({len(h0):,} experimentos simulados no cenário S3), e as caudas em vermelho formam a região de rejeição, '
     f'bicaudal porque o bot poderia acelerar ou atrasar o merge. Nos dados reais, a área hachurada dá p = '
     f'{num(s["p_welch"],2)} (Welch) e p = {num(s["p_mw"],2)} (Mann-Whitney): sem efeito, diferenças assim ou maiores '
     f'apareceriam em {pct(s["p_welch"],0)}% e {pct(s["p_mw"],0)}% dos experimentos, o que não é a probabilidade de H₀ '
     f'ser verdadeira. Com dados tão assimétricos, só {pct(t_out)}% das estatísticas t simuladas caem na região de '
     f'rejeição, em vez de 5%.').replace(',000 ', '.000 '),
 g3=(f'O Mann-Whitney ficou entre {pct(mw_rng[0])}% e {pct(mw_rng[1])}% em todos os cenários, sempre um pouco abaixo de '
     f'5% (provavelmente pela aproximação normal com correção de continuidade), sem nunca ficar liberal; o erro de '
     f'simulação é de ±0,4 p.p. O t de Welch ficou perto de 5% só com dados normais ({pct(t1["S1"][0])}%) e se afastou '
     f'para baixo nos demais: {pct(t1["S2"][0])}% (S2), {pct(t1["S5"][0])}% (S5), {pct(t1["S3"][0])}% (S3) e '
     f'{pct(t1["S4"][0])}% (S4, n = 10). Ele ficou conservador: a estatística t é dominada por poucos valores extremos e '
     f'raramente cruza o valor crítico, então erra pouco, mas ao custo de poder. O painel da direita mostra o mesmo com α = 1%.'),
 g4=(f'Com dados normais (S1) os testes têm poder quase igual, com leve vantagem do Welch (até {num(adv_s1)} p.p.). Em '
     f'todas as outras situações o Mann-Whitney detecta melhor, e a diferença cresce com o efeito: com d = 1, ele chega '
     f'a {pct(gi("S3",1.0,"mw_05"),0)}% contra {pct(gi("S3",1.0,"welch_05"),0)}% do Welch no cenário real (S3), e a '
     f'{pct(gi("S4",1.0,"mw_05"),0)}% contra {pct(gi("S4",1.0,"welch_05"),0)}% com n = 10. A vantagem muda de lado apenas '
     f'quando os dados são normais. Com α = 1% (linhas tracejadas), todas as curvas descem, mas a ordem se mantém '
     f'(S3, d = 1: {pct(gi("S3",1.0,"mw_01"),0)}% contra {pct(gi("S3",1.0,"welch_01"),0)}%).'),
)

# Interpretação do exemplo simulado
rej = [n for n, k in (('t de Welch', 'welch'), ('Mann-Whitney', 'mann_whitney')) if ex[k]['rejeita']]
if not rej:
    interp_ex = ('Nenhum dos testes rejeitou H₀, embora neste conjunto o efeito exista: é um erro tipo II. Com σ ≈ '
                 f'{num(SIGMA,1)} e {N_EX} PRs por grupo, um efeito desse tamanho costuma passar despercebido, e o G4 '
                 'mostra com que frequência cada teste o detecta.')
elif len(rej) == 2:
    interp_ex = 'Os dois testes rejeitaram H₀ e detectaram o efeito que colocamos na simulação.'
else:
    interp_ex = (f'Só o {rej[0]} rejeitou H₀: no mesmo conjunto de dados, os testes chegaram a conclusões diferentes, '
                 'e só ele detectou o efeito que colocamos na simulação.')
tab_ex = ('| Teste | Estatística | p-valor | Tamanho do efeito | Decisão (α = 5%) |\n|---|---|---|---|---|\n'
          f'| t de Welch | t = {num(ex["welch"]["stat"],2)} | {pv(ex["welch"]["p"])} | g de Hedges = '
          f'{num(ex["welch"]["efeito"],2)} | {decisao(ex["welch"])} |\n'
          f'| Mann-Whitney | U = {ex["mann_whitney"]["stat"]:.0f} | {pv(ex["mann_whitney"]["p"])} | delta de Cliff = '
          f'{num(ex["mann_whitney"]["efeito"],2)} | {decisao(ex["mann_whitney"])} |')

# Dados reais (seção 6)
assert not r_real['welch']['rejeita'] and not r_real['mann_whitney']['rejeita'], 'texto da seção 6 assume não rejeição'
tab = ('| Teste | Compara | Estatística | p-valor | Tamanho do efeito | Conclusão (α = 5%) |\n|---|---|---|---|---|---|\n'
       f'| t de Welch | médias | t = {num(r_real["welch"]["stat"],2)} (gl = {num(s["df"])}) | {pv(r_real["welch"]["p"])} | '
       f'diferença de médias = {num(s["mean_com"]-s["mean_sem"])} h; g de Hedges = {num(r_real["welch"]["efeito"],2)} | '
       f'{decisao(r_real["welch"])} |\n'
       f'| Mann-Whitney | postos | U = {r_real["mann_whitney"]["stat"]:.0f} (z = {num(s["z"],2)}) | '
       f'{pv(r_real["mann_whitney"]["p"])} | delta de Cliff = {num(r_real["mann_whitney"]["efeito"],2)}; razão de medianas = '
       f'{num(s["ratio_med"],2)} (IC 95% bootstrap: {num(s["ratio_lo"],2)} a {num(s["ratio_hi"],2)}) | '
       f'{decisao(r_real["mann_whitney"])} |')
real_txt = (f'Os dois testes chegam à mesma conclusão: não há evidência de que o bot mude o tempo até o merge (p = '
            f'{pv(r_real["welch"]["p"])} e {pv(r_real["mann_whitney"]["p"])}). O efeito não tem importância prática clara: '
            f'a média é maior com bot ({num(s["mean_com"])} h contra {num(s["mean_sem"])} h), mas a mediana é menor '
            f'({num(s["med_com"])} h contra {num(s["med_sem"])} h), e a chance de um PR com bot ser mais lento que um sem '
            f'bot é de cerca de {pct((1 + r_real["mann_whitney"]["efeito"])/2, 0)}%. O intervalo da razão de medianas '
            f'({num(s["ratio_lo"],2)} a {num(s["ratio_hi"],2)}) inclui efeitos grandes nos dois sentidos, ou seja, com '
            f'{len(a)} PRs por grupo o estudo tem pouco poder para decidir. Como os grupos vêm de períodos diferentes '
            '(antes e depois do bot), mesmo uma diferença não seria atribuível só ao bot.')

# ---------- Gráficos ----------
plt.rcParams.update({'font.size': 11, 'axes.spines.top': False, 'axes.spines.right': False, 'savefig.dpi': 170,
                     'axes.titleweight': 'bold'})
rng = np.random.default_rng(config.SEED)

# G1 — histograma real × lognormal simulada com os parâmetros de cada grupo (cenario.PARAMS)
fig, ax = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
bins = np.linspace(-2, 3.6, 29); largura = bins[1] - bins[0]; centros = (bins[:-1] + bins[1:])/2
for j, (grupo, x, c, nome) in enumerate([('com_bot', a, CB, 'Com bot'), ('sem_bot', b, SB, 'Sem bot')]):
    prm = PARAMS[grupo]
    ax[j].hist(np.log10(x), bins=bins, density=True, color=c, alpha=.8, edgecolor='white', label=f'Real (n = {len(x)})')
    simulado = np.log10(rng.lognormal(np.log(prm['mediana']), prm['sigma'], 50_000))
    contagem, _ = np.histogram(simulado, bins=bins)
    ax[j].plot(centros, contagem/(len(simulado)*largura), 'k-o', ms=3.5, lw=2,
               label=f'Simulado: lognormal (mediana {num(prm["mediana"])} h, σ = {num(prm["sigma"],2)})')
    ax[j].axvline(np.log10(np.median(x)), color=c, ls='--', label='Mediana real')
    ax[j].set_title(f'{nome} (mediana {np.median(x):.0f} h)')
    ax[j].set_xticks([-2, -1, 0, 1, 2, 3]); ax[j].set_xticklabels(['0,01', '0,1', '1', '10', '100', '1000'])
    ax[j].set_xlabel('Horas até o merge (h, escala log)'); ax[j].set_ylim(0, 1.25)
    ax[j].legend(frameon=False, fontsize=8.5, loc='upper left')
ax[0].set_ylabel('Densidade (na escala log10)')
fig.suptitle('G1 — Dados reais × dados simulados', fontweight='bold'); fig.tight_layout(); fig.savefig(IMG/'g1.png'); plt.close()

# G2
def panel(ax, sim_stat, theo, crit, obs, pobs, lim, col, xl, title):
    bb = np.linspace(-lim, lim, 71)
    ax.hist(np.clip(sim_stat, -lim, lim), bins=bb, density=True, color=col, alpha=.4, label='Simulado sob H₀')
    xs = np.linspace(-lim, lim, 600); ax.plot(xs, theo(xs), 'k', lw=1.6, label='Densidade teórica')
    ax.fill_between(xs, 0, theo(xs), where=np.abs(xs) >= crit, color=RED, alpha=.45, label='Região de rejeição (α = 5%)')
    ax.fill_between(xs, 0, theo(xs), where=np.abs(xs) >= abs(obs), facecolor='none', edgecolor='k', hatch='///', lw=0,
                    label=f'p-valor do exemplo = {pobs:.3f}'.replace('.', ','))
    ax.axvline(obs, color='k', lw=2.2, label='Valor observado'); ax.set_xlabel(xl); ax.set_ylabel('Densidade'); ax.set_title(title)
    ax.set_ylim(0, ax.get_ylim()[1]*1.5); ax.legend(frameon=False, fontsize=8.5, loc='upper left')
fig, ax = plt.subplots(1, 2, figsize=(12, 4.8))
panel(ax[0], h0.t.values, lambda v: stats.t.pdf(v, 57), stats.t.ppf(.975, 57), s['t'], s['p_welch'], 6, W,
      'Estatística t (adimensional)', 't de Welch (compara médias)')
panel(ax[1], h0.z.values, stats.norm.pdf, 1.96, s['z'], s['p_mw'], 5, M, 'Estatística z do U (adimensional)',
      'Mann-Whitney (compara postos)')
fig.suptitle('G2 — Estatística sob H₀ (S3, n = 30), região de rejeição e p-valor dos dados reais', fontweight='bold')
fig.tight_layout(); fig.savefig(IMG/'g2.png'); plt.close()

# G3 (α = 5% e 1%)
r0 = sim[sim.d == 0].reset_index(drop=True); xi = np.arange(len(r0))
fig, ax = plt.subplots(1, 2, figsize=(12, 4.6))
for k, (al, nom) in enumerate((('05', 5), ('01', 1))):
    for off, t, c, lab in ((-.2, 'welch', W, 't de Welch'), (.2, 'mw', M, 'Mann-Whitney')):
        v = r0[f'{t}_{al}']*100; bars = ax[k].bar(xi+off, v, .38, color=c, label=lab)
        for bb_, q in zip(bars, v):
            ax[k].text(bb_.get_x()+.19, q+.05*nom, f'{q:.1f}'.replace('.', ','), ha='center', fontsize=8.5)
    ax[k].axhline(nom, color=RED, ls='--', label=f'α nominal = {nom}%'); ax[k].set_ylim(0, nom*1.45)
    ax[k].set_xticks(xi); ax[k].set_xticklabels(SC); ax[k].set_xlabel('Cenário (S1 normal; S2–S4 lognormais; S5 outliers)')
    ax[k].set_ylabel('Rejeições com H₀ verdadeira (%)'); ax[k].set_title(f'α = {nom}%')
ax[0].legend(frameon=False, fontsize=9, loc='lower left')
fig.suptitle('G3 — Erro tipo I dos dois testes em cada cenário', fontweight='bold'); fig.tight_layout()
fig.savefig(IMG/'g3.png'); plt.close()

# G4
fig, axs = plt.subplots(2, 3, figsize=(13, 7.2), sharey=True)
for ax, k in zip(axs.ravel(), SC):
    d_ = sim[sim.cenario == k]
    for al, ls, alpha in (('05', '-', 1), ('01', '--', .6)):
        ax.plot(d_.d, d_[f'welch_{al}']*100, ls, marker='o', color=W, alpha=alpha, lw=2.2, ms=4)
        ax.plot(d_.d, d_[f'mw_{al}']*100, ls, marker='s', color=M, alpha=alpha, lw=2.2, ms=4)
    ax.axhline(80, color='gray', ls=':'); ax.set_title(LAB[k], fontsize=10.5); ax.set_xlabel('Tamanho do efeito d (ver seção 2)')
for ax in axs[:, 0]: ax.set_ylabel('Poder = rejeições (%)')
axs[1, 2].axis('off')
axs[1, 2].legend(handles=[Line2D([], [], color=W, marker='o', lw=2.2, label='t de Welch'),
                          Line2D([], [], color=M, marker='s', lw=2.2, label='Mann-Whitney'),
                          Line2D([], [], color='k', lw=2, label='α = 5% (linha cheia)'),
                          Line2D([], [], color='k', ls='--', lw=2, alpha=.6, label='α = 1% (tracejada)'),
                          Line2D([], [], color='gray', ls=':', label='poder de 80%')], loc='center', frameon=False, fontsize=11)
fig.suptitle('G4 — Curvas de poder: proporção de rejeições × tamanho do efeito', fontweight='bold'); fig.tight_layout()
fig.savefig(IMG/'g4.png'); plt.close()

# ---------- README.md ----------
md = f'''# Welch × Mann-Whitney: qual teste usar para o tempo até o merge de PRs?

Laboratório 04 · Testes de hipótese por simulação · Engenharia de Software · PUC Minas

- **Dashboard:** [{config.DASHBOARD_URL}]({config.DASHBOARD_URL}) (este README)
- **Repositório:** [{config.REPO_URL}]({config.REPO_URL})
- **GitHub Projects:** [{config.PROJECT_URL}]({config.PROJECT_URL})

> Este README é o dashboard. Ele é gerado por código, com um único comando:
> `pip install -r requirements.txt && python build.py` (semente fixa `SEED = {config.SEED}`, em `src/config.py`).

## 1. Cenário

**Pergunta:** {cenario.PERGUNTA}

**H₀:** {cenario.H0}\\
{cenario.H0_NOTACAO}

**H₁:** {cenario.H1}\\
{cenario.H1_NOTACAO}

**Caudas:** {cenario.CAUDAS}

{cenario.TEXTO_DADOS_REAIS} Lista completa de {n_cand} candidatos, com o motivo de cada exclusão, em `data/raw/prs_candidatos.csv`.

## 2. Os dados (G1)

![G1](images/g1.png)

{cenario.TEXTO_G1}

| Cenário | Distribuição | n por grupo | Finalidade |
|---|---|---|---|
| S1 | Normal(60; 20) | 30 | Pressupostos do Welch atendidos |
| S2 | Lognormal, σ = 1,0 | 30 | Assimetria moderada |
| S3 | Lognormal, σ = {num(SIGMA,2)} (real) | 30 | Assimetria igual à dos dados reais |
| S4 | Lognormal, σ = {num(SIGMA,2)} (real) | 10 | Assimetria e amostra pequena |
| S5 | Normal com 10% de outliers | 30 | Caudas pesadas |

**Tamanho do efeito d** (eixo do G4): nos cenários normais (S1, S5), um grupo é deslocado em d desvios-padrão; nos
lognormais (S2–S4), ln(horas) é deslocado em d·σ, ou seja, a mediana é multiplicada por e^(d·σ). No S3, d = 0,2
multiplica a mediana por {num(np.exp(.2*SIGMA))} e d = 1, por {num(np.exp(SIGMA))}.

## 3. Como os testes funcionam (G2)

![G2](images/g2.png)

{T["g2"]}

**Exemplo com um conjunto simulado.** Geramos {N_EX} PRs por grupo com a mediana do grupo com bot {pct(EFEITO_EX,0)}% menor
(`simulacao.gerar_dados`, equivalente a d ≈ {num(d_ex,2)} no G4) e aplicamos os dois testes (`testes.aplicar_testes`):

{tab_ex}

{interp_ex}

## 4. Erro tipo I (G3)

![G3](images/g3.png)

{T["g3"]}

## 5. Poder (G4)

![G4](images/g4.png)

{T["g4"]}

## 6. Dados reais

{tab}

{real_txt}

## 7. Conclusão

**O que esperávamos antes de simular** (registrado em `src/cenario.py`): {cenario.EXPECTATIVA_PREVIA}

**O que encontramos:** o padrão se confirmou, com uma diferença maior que a esperada. Com a assimetria dos dados reais, o
Welch quase não detecta efeitos ({pct(gi("S3",1.0,"welch_05"),0)}% de poder com d = 1) e fica conservador
({pct(t1["S3"][0])}% de erro tipo I), porque a média de uma lognormal com σ ≈ {num(SIGMA,1)} é dominada por poucos PRs
extremos. Com dados normais, os dois testes ficaram equivalentes.

**Recomendação:** usar o Mann-Whitney para comparar tempos de merge. Ele manteve o erro tipo I perto de 5% em todos os
cenários e perdeu no máximo {num(adv_s1)} p.p. de poder com dados normais. **Mudaríamos para o Welch** se os dados fossem
aproximadamente normais (por exemplo, tempos de build medidos várias vezes) ou se a pergunta fosse sobre a média, como o
total de horas gasto. **Principal limitação:** os grupos são de períodos diferentes (antes e depois do bot), de um único
repositório e com n = {len(a)}, e os dados simulados são uma aproximação (lognormal, mesma forma e mesmo σ nos dois grupos).

---

## Como reproduzir

```bash
pip install -r requirements.txt
python build.py              # gera images/ e este README (usa data/processed/ se já existir)
python build.py --resimular  # refaz também a simulação Monte Carlo
python -m src.coleta         # (opcional) refaz a coleta dos PRs reais
python -m src.analise        # (opcional) estatísticas descritivas e ajuste da lognormal
streamlit run app.py         # (opcional) versão interativa complementar
```

## Estrutura do repositório

| Arquivo | Conteúdo |
|---|---|
| `build.py` | comando único: simulação (se preciso) + gráficos + README |
| `src/config.py` | semente, α, nº de simulações, cores por teste, links |
| `src/cenario.py` | pergunta, H₀/H₁, caudas, expectativa prévia, parâmetros e textos |
| `src/coleta.py` | coleta dos PRs reais via API de busca do GitHub (`data/FONTE.md`) |
| `src/analise.py` | estatísticas descritivas e ajuste da lognormal (`cenario.PARAMS`) |
| `src/simulacao.py` | gerador de dados simulados do cenário |
| `src/testes.py` | t de Welch, Mann-Whitney e tamanhos de efeito |
| `src/simulate.py` | simulação Monte Carlo de Q1–Q3 → `data/processed/` |
| `src/readme.py` | gera `images/` (G1–G4) e este README |
| `src/graficos.py`, `app.py` | versão interativa em Streamlit (complementar) |

## Equipe

| Integrante | Papel |
|---|---|
| Thiago Branco ([@thiagobranc0](https://github.com/thiagobranc0)) | C — dashboard e setup |
| Pedro Luiz Nato ([@pedrrr](https://github.com/pedrrr)) | A — dados reais |
| Bruna Costa ([@Brunamark](https://github.com/Brunamark)) | B — cenário, simulação e testes |

Toda mudança nasce de uma Issue, é feita em uma branch `feat/<nº-issue>-<slug>`, tem commits que referenciam a Issue e
entra na `main` por Pull Request com `Closes #N`.
'''
(ROOT/'README.md').write_text(md, encoding='utf-8'); print('README.md', len(md))
