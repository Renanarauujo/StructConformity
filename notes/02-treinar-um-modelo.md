# Treinar um Modelo de ML

## O que significa "treinar"?

Treinar um modelo = ensinar por exemplos.

O modelo **nao recebe as regras** da NBR 6118. Ele nunca ve que
"cobrimento minimo e 2.5 cm". O que ele recebe sao as 1000 fichas
com as respostas prontas, e ele precisa **descobrir sozinho os padroes**
que separam conforme de nao conforme.

## Analogia: o estagiario

E como pegar um estagiario que nunca leu a norma, colocar ele numa sala
com 800 fichas ja carimbadas, e dizer: "estuda essas fichas e descobre o padrao".

Depois voce testa ele com 200 fichas novas que ele nunca viu, para ver se
ele aprendeu de verdade.

## Treino vs Teste (Holdout)

| Conceito | Analogia | O que e |
|----------|----------|---------|
| **Treino** | As 800 fichas que o estagiario estuda | Dados que o modelo usa para aprender os padroes |
| **Teste** | As 200 fichas novas para provar que aprendeu | Dados que o modelo nunca viu, usados para avaliar |

Essa separacao se chama **Holdout**: voce "segura" uma parte dos dados
fora do treino para testar depois.

Se voce testasse com as mesmas fichas que ele estudou, ele poderia
simplesmente decorar as respostas em vez de aprender o padrao.
Isso se chama **overfitting** (decoreba).

## Por que 4 algoritmos?

Cada algoritmo tem uma forma diferente de encontrar padroes.
E como contratar 4 estagiarios com estilos diferentes de raciocinio:

| Algoritmo | Como ele "pensa" |
|-----------|-----------------|
| **KNN** | "Essa ficha e parecida com quais outras? Se as mais parecidas sao conformes, essa tambem deve ser" |
| **Arvore de Classificacao** | "Vou criar um fluxograma de perguntas: fck >= 20? Se sim, cobrimento >= 2.5? Se sim..." |
| **Naive Bayes** | "Qual a probabilidade de ser conforme dado que tem fck=30 e cover=3.0?" |
| **SVM** | "Vou tracar uma linha (ou superficie) que separa os conformes dos nao conformes no espaco" |

No final, comparamos os 4 e vemos qual acertou mais nas 200 fichas de teste.
