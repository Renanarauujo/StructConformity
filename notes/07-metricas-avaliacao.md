# 07 - Metricas de Avaliacao de Modelos

> Por que acuracia sozinha nao basta e como interpretar a matriz de confusao.

---

## O problema da acuracia

Se de 300 pecas de teste, 170 sao conformes e 130 nao conformes, um modelo que chuta "conforme" pra tudo teria 57% de acuracia. Parece razoavel, mas ele nao pegou NENHUM defeito.

Acuracia diz "quantos acertou no total", mas nao diz **onde** errou. Em engenharia estrutural, deixar passar um elemento nao conforme e muito pior que rejeitar um conforme.

---

## Matriz de Confusao

Tabela 2x2 que mostra acertos e erros por classe:

```
                    Predito Nao Conforme    Predito Conforme
Real Nao Conforme         VN                    FN (ERRO!)
Real Conforme             FP (erro)             VP
```

| Sigla | Nome | Significado | Gravidade |
|-------|------|-------------|-----------|
| VP | Verdadeiro Positivo | Era conforme, modelo acertou | OK |
| VN | Verdadeiro Negativo | Era nao conforme, modelo acertou | OK |
| FP | Falso Positivo | Era conforme, modelo disse nao conforme | Erro leve (rejeita peca boa) |
| FN | Falso Negativo | Era nao conforme, modelo disse conforme | **Erro grave** (libera peca com defeito!) |

**Analogia:** FP = estagiario rejeitou uma peca boa (voce confere e libera). FN = estagiario liberou uma peca com defeito (vai pra obra com problema).

---

## Metricas Derivadas

| Metrica | Formula | O que responde |
|---------|---------|---------------|
| **Acuracia** | (VP + VN) / Total | "No geral, quantos acertou?" |
| **Precisao** | VP / (VP + FP) | "Dos que disse conforme, quantos realmente sao?" |
| **Recall** | VP / (VP + FN) | "Dos que sao conforme, quantos identificou?" |
| **F1-Score** | 2 x (Precisao x Recall) / (Precisao + Recall) | "Equilibrio entre precisao e recall" |

### Recall Nao Conforme - a metrica critica

No contexto estrutural, a metrica mais importante e o **recall da classe "Nao Conforme"**:
- "De todos os elementos que realmente violam a norma, quantos o modelo conseguiu pegar?"
- Recall Nao Conforme = VN / (VN + FN)
- Se for 100% = nenhuma peca defeituosa escapou
- Se for 80% = 20% das pecas defeituosas foram liberadas como conformes

### Precisao vs Recall - o tradeoff

- **Precisao alta** = poucos alarmes falsos (quando diz conforme, acerta)
- **Recall alto** = pega quase todos os defeitos (nao deixa passar)
- Dificilmente os dois sao 100% - melhorar um tende a piorar o outro
- **F1** equilibra os dois numa unica metrica

---

## classification_report

O Scikit-Learn gera automaticamente todas as metricas com `classification_report`:

```
              precision    recall  f1-score   support
Nao Conforme      0.95      0.90      0.92       128
    Conforme      0.93      0.97      0.95       172
    accuracy                          0.94       300
```

- `support` = quantas amostras reais de cada classe existem no teste
- `macro avg` = media simples das metricas (trata classes igualmente)
- `weighted avg` = media ponderada pelo support (peso proporcional ao tamanho)
