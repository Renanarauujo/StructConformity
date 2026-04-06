# 05 - Modelagem: Os 4 Algoritmos de Classificacao

> O que cada algoritmo faz e por que usamos Pipeline.

---

## A ideia geral

Voce tem 1000 pecas estruturais com propriedades (largura, altura, fck, cobrimento, etc.) e uma classificacao: conforme ou nao conforme com a NBR 6118.

O objetivo e treinar modelos que aprendam a classificar pecas **sozinhos**, sem precisar aplicar as regras manualmente.

Treinamos com 700 pecas (com gabarito) e testamos com 300 pecas que o modelo nunca viu.

---

## Os 4 "estagiarios"

Analogia: 4 estagiarios contratados pra conferir armacao em obra, cada um com um metodo diferente.

| Estagiario | Metodo | Algoritmo |
|-----------|--------|-----------|
| 1 | "Vou olhar as 5 pecas mais parecidas que ja vi e seguir a maioria" | **KNN** - compara com vizinhos proximos |
| 2 | "Vou criar uma lista de perguntas: cobrimento >= 2.5? sim/nao. fck >= 20? sim/nao..." | **Arvore de Decisao** - regras encadeadas |
| 3 | "Vou calcular a probabilidade de ser conforme com base em cada propriedade separada" | **Naive Bayes** - probabilidades |
| 4 | "Vou tracar uma linha que separa conformes de nao conformes da melhor forma possivel" | **SVM** - fronteira de separacao |

---

## Detalhes de cada algoritmo

### KNN (K-Nearest Neighbors)
- Para classificar uma peca nova, encontra as k pecas mais parecidas no treino
- Classe = voto da maioria dos k vizinhos
- Sensivel a escala dos dados (precisa de normalizacao)
- Hiperparametros: n_neighbors (k), metric (distancia), weights

### Arvore de Classificacao (Decision Tree)
- Cria regras de decisao em formato de arvore
- Cada no testa um atributo, cada folha e uma classe
- Alta interpretabilidade (da pra visualizar a arvore)
- Nao precisa de normalizacao (baseada em particionamento, nao distancia)
- Hiperparametros: max_depth, criterion (gini/entropy), min_samples_split

### Naive Bayes (GaussianNB)
- Classificador probabilistico baseado no Teorema de Bayes
- Assume independencia entre atributos (hipotese "ingenua")
- Rapido, eficiente, bom como baseline
- Hiperparametros: var_smoothing

### SVM (Support Vector Machine)
- Encontra o hiperplano que melhor separa as classes
- Maximiza a margem entre as classes
- Pode modelar fronteiras nao-lineares (com kernel rbf)
- Sensivel a escala (precisa de normalizacao)
- Hiperparametros: C (rigidez), kernel (linear/rbf/poly), gamma

---

## Por que Pipeline?

Alguns algoritmos (KNN, SVM) trabalham com **distancia** entre valores. Problema: `width_cm` vai de 10 a 80, mas `steel_rate` vai de 15 a 250. Sem ajuste, o steel_rate "pesa" muito mais so por ter numeros maiores.

O **scaler** (StandardScaler) coloca todas as features na mesma escala - transforma cada feature pra ter media 0 e desvio padrao 1.

O **Pipeline** junta scaler + modelo num pacote so:
- O scaler aprende a escala **so com os dados de treino**
- Os dados de teste sao transformados **sem vazamento de informacao** (Data Leakage)

Analogia: dar ao estagiario uma "tabela de conversao" feita so com as pecas de treino, pra ele usar quando encontrar pecas novas no teste.

---

## Acuracia (metrica inicial)

A metrica mais simples pra comparar os 4 modelos:

```
Acuracia = acertos / total
```

Se acertou 270 de 300 pecas de teste = 90%.

**Limitacao:** Acuracia sozinha pode enganar. Se 90% das pecas sao conformes, um modelo que chuta "conforme" sempre teria 90% de acuracia sem aprender nada. Por isso, depois usamos metricas mais detalhadas (precisao, recall, F1).
