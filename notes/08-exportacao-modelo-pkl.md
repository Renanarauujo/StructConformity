# 08 - Exportacao do Modelo (.pkl)

> Como salvar o modelo treinado para uso em producao.

---

## O que e exportar um modelo?

Depois de treinar e escolher o melhor modelo, voce precisa **salvar** ele para que o backend consiga usar sem treinar de novo toda vez. O arquivo salvo contem o modelo "congelado" com tudo que ele aprendeu.

**Analogia:** E como salvar a "experiencia" do estagiario num manual. Da proxima vez que precisar conferir uma peca, ele consulta o manual em vez de aprender tudo do zero.

---

## joblib vs pickle

Duas formas de serializar objetos Python:

| Biblioteca | Uso | Vantagem |
|-----------|-----|----------|
| `pickle` | Padrao do Python | Funciona com qualquer objeto |
| `joblib` | Otimizado para ML | Mais rapido e eficiente com arrays numpy grandes |

No Scikit-Learn, `joblib` e o recomendado.

```python
import joblib

# Salvar
joblib.dump(modelo, "caminho/modelo.pkl")

# Carregar
modelo = joblib.load("caminho/modelo.pkl")
```

---

## O que foi salvo

Salvamos o **Pipeline completo**, nao so o classificador:

```
Pipeline = StandardScaler + DecisionTreeClassifier
```

Isso e importante porque:
- O scaler ja tem os parametros aprendidos (media e desvio padrao do treino)
- Quando o backend receber dados novos, o Pipeline transforma e prediz em um unico passo
- Sem o scaler junto, voce teria que recriar a normalizacao manualmente

---

## Arquivo gerado

- **Caminho:** `backend/model/best_model.pkl`
- **Modelo:** DecisionTreeClassifier (criterion='entropy', max_depth=10)
- **Acuracia:** 98.7%
- **Recall Nao Conforme:** 98%
