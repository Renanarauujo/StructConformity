# StructConformity

Classificação de conformidade estrutural via Machine Learning.

MVP da pós-graduação em Engenharia de Software pela PUC-RJ.

## Sobre

Modelo de ML que classifica se um elemento estrutural (viga, pilar, laje, sapata) está **conforme** ou **não conforme** com a NBR 6118, baseado em propriedades geométricas e de armação.

- **Dataset:** Sintético, 1000 registros gerados a partir de 8 regras da NBR 6118
- **Classificação:** Binária (Conforme / Não Conforme)
- **Algoritmos:** KNN, Árvore de Decisão, Naive Bayes, SVM
- **Melhor modelo:** Árvore de Decisão (98.7% acurácia, 98% recall para Não Conforme)

## Estrutura

```
StructConformity/
├── notebook/           # Notebook Colab (pipeline ML completo)
├── backend/            # API Flask + modelo exportado (.pkl)
│   ├── app.py          # Servidor Flask com endpoint /predict
│   ├── test_model.py   # Testes PyTest de performance do modelo
│   └── model/          # Modelo treinado (best_model.pkl)
├── frontend/           # Interface web (HTML + CSS + JS)
├── dataset/            # Dataset CSV + script gerador
├── docs/               # Documentação (DATA_CONTEXT, DEV_LOG, PROGRESS)
└── notes/              # Notas de estudo
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

A API roda em `http://localhost:5000`. Documentação Swagger em `http://localhost:5000/openapi/swagger`.

### 3. Abrir o frontend

Abrir `frontend/index.html` no navegador. Preencher os campos do elemento estrutural e clicar em "Verificar Conformidade".

### 4. Rodar os testes

```bash
cd backend
pytest test_model.py -v
```

## Features do elemento

| Feature | Tipo | Descrição |
|---------|------|-----------|
| element_type | int | 0=viga, 1=pilar, 2=sapata, 3=laje |
| width_cm | float | Largura em cm |
| height_cm | float | Altura em cm |
| fck | float | Resistência do concreto em MPa |
| cover_cm | float | Cobrimento em cm |
| main_rebar_diam | float | Bitola longitudinal em mm |
| stirrup_diam | float | Bitola do estribo em mm |
| stirrup_spacing_cm | float | Espaçamento de estribos em cm |
| steel_rate | float | Taxa de armadura em kg/m3 |
| length_cm | float | Comprimento em cm |

## Tecnologias

- **ML:** Python, Scikit-Learn, Pandas, NumPy
- **Backend:** Flask, flask-openapi3, flask-cors
- **Frontend:** HTML, CSS, JavaScript
- **Testes:** PyTest

## Autor

Renan Araujo - Pós-graduação em Engenharia de Software, PUC-RJ
