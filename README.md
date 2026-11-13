# Welch × Mann-Whitney: qual teste usar para o tempo até o merge de PRs?

Laboratório 04 · Testes de hipótese por simulação · Engenharia de Software

- **Dashboard:** `<preencher>`
- **Repositório / GitHub Projects:** `<preencher>`

> Este README é o dashboard. Os gráficos são gerados por código: `pip install -r requirements.txt && python build.py`.

## 1. Cenário

**Pergunta:** o tempo até o merge de um Pull Request muda quando o repositório passa a usar um bot de revisão automática (CodeRabbit)?

**H₀:** o bot não muda o tempo até o merge (médias iguais para o Welch; mesma chance de um PR ser mais lento ou mais rápido para o Mann-Whitney).
**H₁:** o bot muda o tempo até o merge, para mais ou para menos (teste bicaudal).

**Dados reais:** PRs com merge do repositório público formbricks/formbricks (GitHub), em horas entre abertura e merge. Foram coletados **30 PRs com bot** (set. a nov. de 2024, revisados pelo coderabbitai) e **30 sem bot** (mai. a ago. de 2024), a partir de uma lista de 541 candidatos (`data/raw/prs_candidatos.csv`). Excluímos PRs abertos por bots, merges em menos de 1 minuto e PRs não revisados pelo bot após a adoção.

## 2. Os dados (G1)

![G1](images/g1.png)

Os dois grupos são fortemente assimétricos à direita: a média (com bot 99,4 h; sem bot 71,0 h) fica muito acima da mediana (24,0 h e 41,5 h), há PRs de até 646 h e o teste de Shapiro-Wilk rejeita normalidade (p < 0,001). Na escala log o formato fica quase simétrico, então usamos uma lognormal. Os parâmetros vieram dos dados: μ = 2,64 (log-média do grupo sem bot) e σ = 2,43 (média dos desvios do log dos dois grupos). Com só 30 PRs por grupo o histograma real é irregular, mas cobre a mesma faixa (de minutos a semanas) e tem a mesma cauda longa da curva simulada.

| Cenário | Distribuição | n por grupo | Finalidade |
|---|---|---|---|
| S1 | Normal(60; 20) | 30 | Pressupostos do Welch atendidos |
| S2 | Lognormal, σ = 1,0 | 30 | Assimetria moderada |
| S3 | Lognormal, σ = 2,43 (real) | 30 | Assimetria igual à dos dados reais |
| S4 | Lognormal, σ = 2,43 (real) | 10 | Assimetria e amostra pequena |
| S5 | Normal com 10% de outliers | 30 | Caudas pesadas |

## 3. Como os testes funcionam (G2)

![G2](images/g2.png)

O t de Welch compara as médias dos grupos e o Mann-Whitney compara postos (se um grupo tende a ter valores maiores que o outro). O gráfico mostra a distribuição de cada estatística quando H₀ é verdadeira, obtida em 20.000 experimentos simulados; as caudas em vermelho formam a região de rejeição, bicaudal porque o bot poderia acelerar ou atrasar. Nos dados reais, a área hachurada dá p = 0,42 (Welch) e p = 0,82 (Mann-Whitney): sem efeito, diferenças assim ou maiores apareceriam em 42% e 82% dos experimentos. Isso não é a probabilidade de H₀ ser verdadeira nem prova de que o bot não tem efeito. Atenção: com dados tão assimétricos, só 1,7% das estatísticas t caem na região de rejeição, em vez de 5%.

## 4. Erro tipo I (G3)

![G3](images/g3.png)

O Mann-Whitney ficou entre 4,3% e 4,8% em todos os cenários, sempre um pouco abaixo de 5% (provavelmente por usarmos a aproximação normal com correção de continuidade), sem nunca ficar liberal; o erro de simulação é de ±0,4 p.p. O t de Welch ficou perto de 5% só com dados normais (5,2%) e se afastou para baixo nos demais: 3,7% (S2), 3,4% (S5), 1,4% (S3) e 0,6% (S4, n = 10). Ele ficou conservador: a estatística t é dominada por poucos valores extremos e raramente cruza o valor crítico, então erra pouco, mas ao custo de poder. O painel da direita mostra o mesmo com α = 1%.

## 5. Poder (G4)

![G4](images/g4.png)

Com dados normais (S1) os testes têm poder quase igual, com leve vantagem do Welch (até 3,5 p.p.). Em todas as outras situações o Mann-Whitney detecta melhor, e a diferença cresce com o efeito: com d = 1, ele chega a 96% contra 28% do Welch no cenário real (S3), e a 50% contra 7% com n = 10. A vantagem muda de lado apenas quando os dados são normais. Com α = 1% (linhas tracejadas), todas as curvas descem, mas a ordem se mantém (S3, d = 1: 86% contra 6%).

## 6. Dados reais

| Teste | Compara | Estatística | p-valor | Tamanho do efeito | Conclusão (α = 5%) |
|---|---|---|---|---|---|
| t de Welch | médias | t = 0,81 (gl = 46,9) | 0,425 | diferença de médias = 28,3 h; d de Cohen = 0,21 | Não rejeita H₀ |
| Mann-Whitney | postos | U = 466 (z = 0,24) | 0,819 | delta de Cliff = 0,04; razão de medianas = 0,58 (IC95% 0,22 a 3,17) | Não rejeita H₀ |

Os dois testes chegam à mesma conclusão: não há evidência de que o bot mude o tempo até o merge (p = 0,425 e 0,819). O efeito não tem importância prática clara: a média é maior com bot (99,4 h contra 71,0 h), mas a mediana é menor (24,0 h contra 41,5 h), e a probabilidade de um PR com bot ser mais lento que um sem bot é de cerca de 52% (delta de Cliff = 0,04). O intervalo da razão de medianas (0,22 a 3,17) inclui efeitos grandes nos dois sentidos, ou seja, com 30 PRs por grupo o estudo tem pouco poder para decidir. Como os grupos vêm de períodos diferentes (antes e depois do bot), mesmo uma diferença não seria atribuível só ao bot.

## 7. Conclusão

**Esperávamos** que o Mann-Whitney se saísse melhor com dados assimétricos e com outliers, porque usa postos, e que os dois testes ficassem equivalentes com dados normais. **Encontramos** esse padrão, mas com uma diferença maior que a esperada: com a assimetria dos dados reais, o Welch quase não detecta efeitos (28% de poder com d = 1) e fica conservador (1,4% de erro tipo I), porque a média de uma lognormal com σ ≈ 2,4 é dominada por poucos PRs extremos.

**Recomendação:** usar o Mann-Whitney para comparar tempos de merge. Ele manteve o erro tipo I perto de 5% em todos os cenários e perdeu no máximo 3,5 p.p. de poder com dados normais. **Mudaríamos para o Welch** se os dados fossem aproximadamente normais (por exemplo, tempos de build medidos várias vezes) ou se a pergunta fosse sobre a média, como o total de horas gasto. **Principal limitação:** os grupos são de períodos diferentes (antes e depois do bot), de um único repositório e com n = 30, e os dados simulados são uma aproximação (lognormal, mesma forma e mesmo σ nos dois grupos).

## Estrutura do repositório

- `src/simulate.py`: simulação Monte Carlo (semente 2026, 10.000 réplicas por ponto) e estatísticas dos dados reais → `data/processed/`
- `src/readme.py`: gera `images/` (G1 a G4) e este README
- `build.py`: executa tudo (`--resimular` refaz a simulação)
