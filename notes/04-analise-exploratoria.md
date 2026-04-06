# 04 - Analise Exploratoria de Dados (EDA)

> O que olhar nos dados antes de treinar qualquer modelo.

---

## O que e EDA?

Antes de treinar um modelo de ML, voce precisa **entender os dados**. E como um engenheiro que, antes de calcular a armacao, precisa saber: qual o concreto? Qual o vao? Qual a carga?

A Analise Exploratoria responde 3 perguntas:
1. **Quantos dados eu tenho e como eles sao?** (shape, info, describe)
2. **As classes estao balanceadas?** (value_counts)
3. **As features sao independentes entre si?** (correlacao)

---

## Ferramentas usadas

| Comando | O que faz | Analogia |
|---------|-----------|----------|
| `df.shape` | Retorna (linhas, colunas) | "Quantas pecas vou conferir e quantas propriedades cada uma tem?" |
| `df.info()` | Tipo de cada coluna + nulos | "Tem alguma informacao faltando na planilha?" |
| `df.describe()` | Media, desvio padrao, min, max, quartis | "Qual o resumo estatistico de cada propriedade?" |
| `df["col"].value_counts()` | Conta ocorrencias de cada valor | "Quantas pecas conformes vs nao conformes?" |
| `df.corr()` | Correlacao de Pearson entre colunas | "Alguma propriedade e redundante com outra?" |

---

## Distribuicao das Classes

- **572 conformes (57%)** vs **428 nao conformes (43%)**
- Bom balanceamento - o modelo e obrigado a aprender os padroes reais
- Se fosse 95/5, o modelo poderia "chutar" sempre a classe majoritaria e acertar 95% sem aprender nada

**Analogia:** Treinar um estagiario pra conferir armacao. Se 95% das pecas que ele ve estao certas, ele aprende que "ta tudo certo sempre". Com 57/43, ele ve erros suficientes pra aprender a identificar o que esta errado.

---

## Histogramas das Features

O histograma mostra como os valores de cada feature estao distribuidos.

| Feature | Distribuicao | Observacao |
|---------|-------------|------------|
| `width_cm` | Uniforme (10-80cm) | Cobre vigas estreitas ate sapatas largas |
| `height_cm` | Uniforme (15-120cm) | Boa variacao de alturas |
| `fck` | Discreto (15, 20, 25, 30, 35, 50) | Classes comerciais reais |
| `cover_cm` | Concentrado entre 2-4.5cm | Valores com 0-1cm sao propositalmente nao conformes |
| `main_rebar_diam` | Discreto (8, 10, 12.5, 16, 20, 25, 32) | Bitolas comerciais reais |
| `stirrup_diam` | Discreto (4.2, 5.0, 6.3, 8.0, 10.0) | Bitolas de estribo comerciais |
| `stirrup_spacing_cm` | Uniforme (5-35cm) | Inclui espacamentos fora da norma |
| `steel_rate` | Uniforme (15-250 kg/m3) | Inclui taxas acima do maximo (200) |
| `length_cm` | Uniforme (100-1200cm) | Comprimentos variados |

**O importante:** Features com boa variacao de valores permitem ao modelo aprender os limites. Se tudo estivesse concentrado num valor so, nao teria como distinguir conforme de nao conforme.

---

## Matriz de Correlacao

A correlacao de Pearson mede a relacao linear entre duas variaveis, de -1 a +1:
- **0** = sem relacao linear
- **+1** = relacao positiva perfeita (uma sobe, outra sobe junto)
- **-1** = relacao negativa perfeita (uma sobe, outra desce)

**Resultado no nosso dataset:** Todas as correlacoes entre -0.08 e +0.17. Muito proximas de zero.

**O que isso significa:**
- Nenhuma feature e redundante com outra
- Cada feature traz informacao independente - bom para ML
- Se houvesse correlacao alta (ex: 0.95), uma feature seria "lixo" e poderia ser descartada

**Analogia:** Avaliar qualidade de concreto. Medir resistencia e slump traz informacoes diferentes (correlacao baixa = bom). Mas medir resistencia aos 7 e 28 dias sao muito correlacionadas - a segunda quase repete a primeira.

---

## Conclusao

Antes de treinar, confirmar:
- [x] Dataset tem tamanho suficiente (1000 registros)
- [x] Nao tem dados faltantes (zero nulos)
- [x] Classes balanceadas (~57/43)
- [x] Features com boa variacao de valores
- [x] Features independentes entre si (correlacoes baixas)

Se algum desses itens falhasse, precisariamos tratar antes de seguir pro pre-processamento.
