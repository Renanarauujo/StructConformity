# 06 - Otimizacao de Hiperparametros (GridSearchCV)

> Como encontrar a melhor configuracao de cada algoritmo.

---

## O que sao hiperparametros?

Sao as "configuracoes" do algoritmo que voce define **antes** de treinar. O modelo nao aprende eles sozinho - voce precisa escolher.

Exemplo: no KNN, o numero de vizinhos (k) e um hiperparametro. O padrao e 5, mas sera que 3 ou 7 seria melhor?

**Analogia:** Voce tem 4 estagiarios e quer otimizar o metodo de cada um. Pro estagiario 1 (KNN), voce testa: "olha 3 pecas parecidas", "olha 5", "olha 7", "olha 9" - e ve qual quantidade de referencia da o melhor resultado.

---

## GridSearchCV

Busca exaustiva: testa **todas** as combinacoes de hiperparametros usando cross-validation.

```python
grid = GridSearchCV(pipeline, param_grid, cv=5, scoring="accuracy", n_jobs=-1)
grid.fit(X_train, y_train)
```

- `cv=5` - 5-fold cross-validation (divide treino em 5 partes, treina com 4, valida com 1, repete 5x)
- `scoring="accuracy"` - usa acuracia pra decidir qual combinacao e melhor
- `n_jobs=-1` - usa todos os nucleos do processador
- `grid.best_estimator_` - pipeline treinado com os melhores parametros
- `grid.best_params_` - quais parametros ganharam
- `grid.best_score_` - acuracia media da cross-validation

---

## Hiperparametros de cada algoritmo

### KNN
| Hiperparametro | O que faz | Valores testados |
|---------------|-----------|-----------------|
| `n_neighbors` | Quantos vizinhos olhar | 3, 5, 7, 9, 11 |
| `metric` | Como medir distancia | euclidiana, manhattan |
| `weights` | Peso dos vizinhos | uniform (todos iguais), distance (mais proximo pesa mais) |

### Arvore de Decisao
| Hiperparametro | O que faz | Valores testados |
|---------------|-----------|-----------------|
| `max_depth` | Profundidade maxima | 3, 5, 10, 15, None (sem limite) |
| `criterion` | Como decidir a divisao | gini, entropy |
| `min_samples_split` | Minimo de amostras pra dividir | 2, 5, 10 |

### Naive Bayes
| Hiperparametro | O que faz | Valores testados |
|---------------|-----------|-----------------|
| `var_smoothing` | Suavizacao pra evitar probabilidade zero | 1e-9, 1e-8, 1e-7, 1e-6, 1e-5 |

### SVM
| Hiperparametro | O que faz | Valores testados |
|---------------|-----------|-----------------|
| `C` | Rigidez da margem | 0.1, 1, 10, 100 |
| `kernel` | Tipo de fronteira | linear (reta), rbf (curva) |
| `gamma` | Influencia de cada ponto | scale, auto |

---

## Prefixo `classifier__`

Dentro do Pipeline, o modelo se chama "classifier" (definido na criacao). Para acessar hiperparametros do modelo dentro do Pipeline, usa-se o prefixo `classifier__` (dois underscores).

Exemplo: `classifier__n_neighbors` = o hiperparametro `n_neighbors` do passo "classifier" do Pipeline.

---

## Cross-Validation (5-fold)

Em vez de avaliar com um unico split treino/teste, a cross-validation divide os dados de treino em 5 partes:

```
Fold 1: [TESTE] [treino] [treino] [treino] [treino]
Fold 2: [treino] [TESTE] [treino] [treino] [treino]
Fold 3: [treino] [treino] [TESTE] [treino] [treino]
Fold 4: [treino] [treino] [treino] [TESTE] [treino]
Fold 5: [treino] [treino] [treino] [treino] [TESTE]
```

Resultado = media das 5 avaliacoes. Isso e mais confiavel que um unico split porque reduz o efeito da "sorte" na divisao dos dados.
