# Etapas do Notebook ML

## Visao Geral

O notebook e o coracao do projeto. O fluxo completo:

1. **Carregar** o dataset (abrir as fichas)
2. **Explorar** os dados (entender o que tem ali dentro)
3. **Preparar** os dados para o modelo (pre-processamento)
4. **Treinar** 4 algoritmos diferentes (ensinar 4 "estagiarios" a ler as fichas)
5. **Avaliar** qual "estagiario" aprendeu melhor
6. **Exportar** o melhor para usar na aplicacao

## Bibliotecas Necessarias

| Biblioteca | Para que serve |
|------------|---------------|
| `pandas` | Manipular a tabela de dados (abrir CSV, filtrar, agrupar) |
| `numpy` | Calculos numericos (arrays, operacoes matematicas) |
| `matplotlib` | Graficos basicos (histogramas, barras) |
| `seaborn` | Graficos estatisticos mais bonitos (construido sobre matplotlib) |
| `scikit-learn` | Algoritmos de ML, metricas, pipelines |

## Fluxo no Notebook

Cada celula e um passo. O notebook conta uma historia:
- Celulas de **texto** (Markdown) explicam o que esta acontecendo e por que
- Celulas de **codigo** executam a acao
- A sequencia deve fazer sentido para alguem que nunca viu o projeto
