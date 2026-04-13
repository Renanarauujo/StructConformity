# StructConformity

Classificação de conformidade estrutural via Machine Learning.

MVP da pós-graduação em Engenharia de Software pela PUC-RJ.

## Sobre

Modelo de ML que classifica se uma viga ou pilar está **conforme** ou **não conforme** com a NBR 6118, a partir de propriedades geométricas e de armação.

- **Dataset:** sintético, 20.000 registros gerados a partir de 10 regras da NBR 6118
- **Classificação:** binária (Conforme / Não Conforme)
- **Algoritmos testados:** KNN, Árvore de Decisão, Naive Bayes, SVM
- **Modelo exportado:** Árvore de Decisão (acurácia ~97%, recall Não Conforme ~97%)

## Estrutura

```
StructConformity/
├── notebook/           Notebook Colab com o pipeline ML completo
├── backend/            API Flask e modelo exportado
│   ├── app.py          Servidor Flask com endpoint /predict
│   ├── test_model.py   Testes PyTest de performance do modelo
│   └── model/          Modelo treinado (best.pkl)
├── frontend/           Interface web (HTML, CSS, JS)
└── dataset/            CSV e script gerador
```

## Como rodar

### 1. Instalar dependências

```bash
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Subir a API

```bash
cd backend
python app.py
```

A API roda em `http://localhost:5000`. Swagger em `http://localhost:5000/openapi/swagger`.

### 3. Abrir o frontend

Abra `frontend/index.html` no navegador. Preencha os campos e clique em **Verificar conformidade**.

### 4. Rodar os testes

```bash
cd backend
pytest test_model.py -v
```

## Features de entrada

| Feature | Tipo | Descrição |
|---|---|---|
| `element_type` | int | 0 = viga, 1 = pilar |
| `dim_a` | float | Largura da seção (cm) |
| `dim_b` | float | Altura da seção (cm) |
| `dim_c` | float | Comprimento da viga ou altura em Z do pilar (cm) |
| `fck` | float | Resistência do concreto (MPa) |
| `cover` | float | Cobrimento (cm) |
| `main_rebar_diam` | float | Bitola longitudinal (mm) |
| `main_rebar_quantity` | int | Quantidade de barras longitudinais |
| `stirrup_diam` | float | Bitola do estribo (mm) |
| `stirrup_spacing` | float | Espaçamento dos estribos (cm) |

## Regras de conformidade

São 10 regras aplicadas no gerador e na avaliação:

1. Cobrimento ≥ 2,5 cm
2. fck ≥ 20 MPa
3. Largura mínima da seção (viga ≥ 12 cm; pilar ≥ 19 cm)
4. Quantidade mínima de barras longitudinais ≥ 4
5. Bitola do estribo ≥ 5,0 mm
6. Bitola longitudinal mínima (viga ≥ 8 mm; pilar ≥ 10 mm)
7. Espaçamento máximo de estribos (critério específico por tipo)
8. Taxa mínima de armadura (viga segue tabela da NBR por fck; pilar ≥ 0,4%)
9. Taxa máxima de armadura (viga ≤ 4%; pilar ≤ 8%)
10. Espaçamento geométrico real — verifica se as barras cabem na seção respeitando a distância mínima entre barras e o agregado graúdo

## Tecnologias

- **ML:** Python, Scikit-Learn, Pandas, NumPy
- **Backend:** Flask, flask-openapi3, flask-cors
- **Frontend:** HTML, CSS, JavaScript puro
- **Testes:** PyTest

## Autor

Renan Araújo - Pós-graduação em Engenharia de Software, PUC-RJ
