# StructConformity — Log de Desenvolvimento

> Registro passo a passo de tudo que foi feito no projeto.
> Cada sessão documenta comandos, decisões e o porquê de cada ação.

---

## Sessão 01 — 2026-03-24

### 1. Abertura do projeto no VS Code

```
code C:\Users\renan\source\repos\StructConformity
```

### 2. Criação do ambiente virtual (venv)

**O que é:** Um ambiente isolado de Python para o projeto. Cada projeto tem suas próprias dependências sem conflitar com outros projetos ou com o Python do sistema.

**Comando:**
```
python -m venv venv
```

**O que cria:** Pasta `venv/` com uma cópia local do Python e do pip. Tudo que instalarmos via pip vai parar aqui dentro, não no sistema global.

**Status:** ✅ Concluído

### 3. Ativação do ambiente virtual

**Comando:**
```
venv\Scripts\activate
```

**O que faz:** Ativa o venv para que tudo que rodarmos (pip, python) use o ambiente isolado. O terminal mostra `(venv)` no início da linha.

**Status:** ✅ Concluído

### 4. Instalação das dependências

**Comando:**
```
pip install flask flask-openapi3 flask-cors scikit-learn pandas numpy pytest
```

**O que cada pacote faz:**
- `flask` — micro-framework web para o backend (API)
- `flask-openapi3` — documentação automática da API (Swagger)
- `flask-cors` — permite que o frontend (HTML) acesse a API
- `scikit-learn` — biblioteca de Machine Learning (os 4 algoritmos)
- `pandas` — manipulação de dados (carregar CSV, filtrar, agrupar)
- `numpy` — operações numéricas (arrays, cálculos)
- `pytest` — framework de testes automatizados
- `seaborn` — Manipulação de dados tabulares ("Excel do python")
- `matplotlib` — Criador de gráficos básicos

**Status:** ✅ Concluído

### 5. Congelamento das dependências

**Comando:**
```
pip freeze > requirements.txt
```

**O que faz:** Gera um arquivo com todas as bibliotecas e versões exatas instaladas no venv. Permite reproduzir o ambiente em qualquer máquina com `pip install -r requirements.txt`.

**Status:** ✅ Concluído

### 6. Criação da estrutura de pastas

**Comando:**
```
mkdir notebook backend frontend dataset
mkdir backend\model
```

**Estrutura:**
```
StructConformity/
├── backend/        ← API Flask + testes
│   └── model/      ← arquivo .pkl do modelo treinado
├── dataset/        ← CSV do dataset
├── docs/           ← documentação (DATA_CONTEXT.md, DEV_LOG.md)
├── frontend/       ← HTML + CSS + JS
├── notebook/       ← notebook Colab (ML)
├── requirements.txt
├── .gitignore
└── venv/           ← ambiente virtual (não vai pro GitHub)
```

**Status:** ✅ Concluído

### 7. Criação do .gitignore

**Conteúdo:**
```
venv/
__pycache__/
*.pyc
.ipynb_checkpoints/
.env
```

**O que faz:** Diz ao Git quais arquivos/pastas ignorar. O venv é pesado e específico da máquina — não sobe pro repositório. `__pycache__` e `.pyc` são cache do Python. `.ipynb_checkpoints` são backups automáticos do Jupyter. `.env` pode conter secrets.

**Status:** ✅ Concluído

### 8. Inicialização do Git e push para GitHub

**Comandos:**
```
git init
git add .
git commit -m "Setup inicial do projeto StructConformity"
```

**Push:** Via UI do VS Code → Source Control → Publish Branch → GitHub (privado)

**Repositório:** Privado por enquanto - trocar para público antes da entrega final.

**Status:** ✅ Concluído

---

## Sessão 02 - 2026-04-03

### 1. Definição das regras de conformidade da NBR 6118

**O que são:** Critérios extraídos da norma brasileira NBR 6118 (Projeto de Estruturas de Concreto) que determinam se um elemento estrutural está dentro dos limites aceitáveis. São as "respostas certas" que o modelo de ML vai aprender.

**8 regras implementadas:**

| # | Regra | Condição |
|---|-------|----------|
| 1 | Cobrimento mínimo | cover_cm >= 2.5 cm |
| 2 | Espaçamento máx. estribos | stirrup_spacing <= min(0.6 * h, 30) |
| 3 | Diâmetro mín. estribo | stirrup_diam >= 5.0 mm |
| 4 | Taxa mín. armadura (vigas) | steel_rate >= 25 kg/m3 |
| 5 | Taxa máx. armadura | steel_rate <= 200 kg/m3 |
| 6 | fck mínimo | fck >= 20 MPa |
| 7 | Largura mín. viga | width >= 12 cm |
| 8 | Largura mín. pilar | width >= 19 cm |

**Lógica:** O elemento é conforme APENAS se TODAS as regras aplicáveis forem atendidas. Basta uma violação para ser "nao_conforme".

**Status:** ✅ Concluído

### 2. Criação do script gerador de dataset sintético

**Arquivo:** `dataset/generate_dataset.py`

**O que faz:** Gera registros fictícios de elementos estruturais com propriedades variando dentro e fora dos limites da NBR 6118. Aplica as 8 regras para classificar cada um.

**Estratégia de balanceamento:**
- 50% dos registros são gerados propositalmente dentro dos limites (conformes)
- 50% são gerados aleatoriamente (maioria cai como não conforme)
- O mix resulta em ~57/43 conforme/não conforme

**Decisões importantes:**
- Seed fixa (`random.seed(42)`) para reprodutibilidade
- Bitolas de aço usam valores comerciais reais (8, 10, 12.5, 16, 20, 25, 32 mm)
- Ranges de geração incluem valores fora da norma para criar exemplos negativos realistas

**Status:** ✅ Concluído

### 3. Ajustes de realismo nas features

**Valores discretos aplicados:**
- `width_cm` e `height_cm`: sempre múltiplos de 5 (como se dimensiona na prática)
- `fck`: apenas classes comerciais [15, 20, 25, 30, 35, 50] MPa
- `cover_cm`: de 0 a 4.5 cm, sempre múltiplos de 0.5

**Proporções por tipo de elemento:**
- **Vigas (beam):** altura sempre maior que largura (h/w entre 2x e 4x), largura entre 10-30 cm
- **Sapatas (footing):** formato quadrático ou levemente retangular (diferença máx ~30%), largura mínima 40 cm
- **Pilares e lajes:** sem restrição especial de proporção

**Status:** ✅ Concluído

### 4. Geração do CSV

**Comando:**
```
python dataset/generate_dataset.py
```

**Resultado:**
- 1000 registros gerados
- 572 conformes (57.2%)
- 428 não conformes (42.8%)
- Distribuição equilibrada entre os 4 tipos de elementos
- Salvo em `dataset/structural_conformity.csv`

**Status:** ✅ Concluído

### 5. Upload para GitHub e validação

**Push:** Commits enviados para o repositório privado no GitHub.

**Validação:** Carga do CSV testada localmente via pandas (1000 linhas, 11 colunas, tipos corretos). A URL raw (`https://raw.githubusercontent.com/Renanarauujo/StructConformity/master/dataset/structural_conformity.csv`) funcionará quando o repositório for tornado público antes da entrega.

**Status:** ✅ Concluído

---

## Sessão 03 - 2026-04-06

### 1. Criação do notebook e imports

**Arquivo:** `notebook/struct_conformity_ml.ipynb`

**Celulas criadas:**
- Markdown com titulo e metadados do projeto
- Code com imports: pandas, numpy, matplotlib, seaborn

**Status:** ✅ Concluído

### 2. Carga do dataset

**Método:** `pd.read_csv(url)` carregando CSV via URL raw do GitHub (com hash do commit).

**Conceitos trabalhados:**
- `pd.read_csv()` - leitura de CSV para DataFrame
- Diferença entre URL da pagina GitHub (`/blob/`) e URL raw (`raw.githubusercontent.com`)
- `df.head(10)` - visualizar primeiras linhas

**Status:** ✅ Concluído

### 3. Análise exploratória

**Celulas criadas:**
- `df.shape` e `df.info()` - 1000 linhas, 11 colunas, zero nulos
- `df.describe()` - estatísticas descritivas das 9 features numéricas
- `df["conformity"].value_counts()` - 572 conformes (57%), 428 não conformes (43%)

**Conceitos trabalhados:**
- `shape` - dimensões do DataFrame (tupla linhas x colunas)
- `info()` - tipos de dados e contagem de nulos
- `describe()` - resumo estatístico (media, std, min, quartis, max)
- `value_counts()` e `normalize=True` - contagem e proporção das classes

**Conclusão:** Dataset limpo, sem nulos, bom balanceamento de classes.

**Status:** ✅ Concluído

### 4. Visualizacoes

**3 graficos criados:**
1. **Barras** - distribuição das classes (azul #2980b9 / #1a5276)
2. **Histogramas** - distribuição de cada feature numerica (grade 3x3)
3. **Heatmap** - matriz de correlação de Pearson entre features

**Conceitos trabalhados:**
- `plt.subplots()` e `figsize` - criar figuras com tamanho definido
- `.plot(kind="bar")` - grafico de barras a partir de Series
- `tick_params(rotation=0)` e `set_xticklabels()` - customizar labels dos eixos
- `select_dtypes(include=[np.number])` - filtrar colunas por tipo
- `enumerate()` - iterar com indice
- `.corr()` - correlação de Pearson (-1 a 1)
- `sns.heatmap()` - mapa de calor com anotacoes

**Status:** ✅ Concluido

### 5. Pre-processamento

**Celulas criadas:**
- Imports: `train_test_split`, `MinMaxScaler`, `StandardScaler`, `LabelEncoder`, `Pipeline`
- `LabelEncoder` para `element_type`: beam=0, column=1, footing=2, slab=3
- Separacao X (10 features) e y (1=conforme, 0=nao conforme)
- Holdout 70/30 com `stratify=y` e `random_state=42`

**Conceitos trabalhados:**
- `LabelEncoder` - converter categorias em numeros
- `fit_transform()` - aprender mapeamento + aplicar
- Separacao X/y - features vs target
- `train_test_split` - holdout com estratificacao
- `stratify` - manter proporcao das classes em treino e teste
- Data Leakage - por que nao normalizar antes de dividir
- Pipeline - encadeia scaler + modelo pra evitar vazamento

**Resultado:** 700 treino / 300 teste, proporcoes mantidas.

**Status:** ✅ Concluido

### 6. Modelagem - 4 algoritmos com Pipeline

**Celulas criadas:**
- Markdown com descricao da secao
- Imports dos 4 classificadores + accuracy_score
- Dicionario de Pipelines (StandardScaler + modelo) + loop de treino/avaliacao

**Resultados iniciais (sem otimizacao):**
| Algoritmo | Acuracia |
|-----------|----------|
| KNN | 82.7% |
| Decision Tree | 98.7% |
| Naive Bayes | 85.0% |
| SVM | 86.3% |

**Observacao:** Arvore dominou porque o dataset usa regras de corte (se cobrimento < 2.5 = nao conforme), e Arvore de Decisao faz exatamente isso.

**Status:** ✅ Concluido

### 7. Otimizacao de hiperparametros (GridSearchCV)

**Celulas criadas:**
- Markdown com descricao da secao
- Dicionario `param_grids` com hiperparametros de cada algoritmo
- Loop de GridSearchCV com cv=5 e n_jobs=-1
- Comparacao antes vs depois no conjunto de teste

**Melhores parametros encontrados:**
- KNN: manhattan, k=11, uniform
- Decision Tree: entropy, max_depth=10, min_samples_split=2
- Naive Bayes: var_smoothing=1e-9 (padrao)
- SVM: C=10, rbf, gamma=scale

**Comparacao no teste:**
| Algoritmo | Antes | Depois | Diferenca |
|-----------|-------|--------|-----------|
| KNN | 82.7% | 83.3% | +0.7% |
| Decision Tree | 98.7% | 98.7% | 0% |
| Naive Bayes | 85.0% | 85.0% | 0% |
| SVM | 86.3% | 87.7% | +1.3% |

**Status:** ✅ Concluido

### 8. Avaliacao detalhada (metricas + matriz de confusao)

**Celulas criadas:**
- Markdown com descricao das metricas
- Matrizes de confusao (grade 2x2) dos 4 modelos
- Classification report de cada modelo
- Tabela comparativa com highlight do melhor por metrica

**Resultados detalhados:**
| Modelo | Acuracia | Recall NC | Precisao C | F1 C |
|--------|----------|-----------|-----------|------|
| KNN | 83.3% | 62% | 78% | 0.87 |
| Decision Tree | 98.7% | 98% | 98% | 0.99 |
| Naive Bayes | 85.0% | 72% | 82% | 0.88 |
| SVM | 87.7% | 79% | 86% | 0.90 |

**Conclusao:** Decision Tree domina em todas as metricas. Recall Nao Conforme de 98% = so 2 pecas defeituosas escaparam de 128. Arvore se encaixa perfeitamente em dados baseados em regras de corte (NBR 6118).

**Status:** ✅ Concluido

### 9. Analise final e exportacao do modelo

**Celulas criadas:**
- Markdown com analise final de resultados (ranking, justificativa da escolha)
- Markdown da secao de exportacao
- Code: `joblib.dump()` exportando Pipeline completo (StandardScaler + DecisionTree) como .pkl

**Modelo exportado:** `backend/model/best_model.pkl`
- Pipeline completo: StandardScaler + DecisionTreeClassifier(criterion='entropy', max_depth=10)
- Pronto para ser carregado no backend Flask

**Status:** ✅ Concluido

### 10. Documentacao do notebook e reflexao de seguranca

**Celulas inseridas:**
- "Sobre este Notebook" (sumario narrativo das 7 secoes) - apos o titulo
- "Reflexao sobre Seguranca e Anonimizacao" (secao 7) - apos exportacao do modelo

**Conteudo da reflexao de seguranca:**
- Triade CIA aplicada ao contexto estrutural
- Confidencialidade: dados de projetos como propriedade intelectual
- Integridade: risco de modelo adulterado aprovar pecas defeituosas
- Disponibilidade: impacto em contexto de obra
- Anonimizacao: remocao de identificadores, generalizacao, k-anonimidade, pseudonimizacao
- Validacao de entrada: faixas realistas, prevencao contra injecao

**Secao 3 (Notebook Colab) 100% concluida!**

**Status:** ✅ Concluido

---

## Sessao 04 - 2026-04-11

### 1. Criacao do app.py com Flask

**Arquivo:** `backend/app.py`

**Construcao incremental:**
- Imports iniciais: `Flask`, `joblib`, `numpy`
- Instancia Flask com `Flask(__name__)`
- Carga do modelo com `joblib.load("model/best_model.pkl")`
- Rota raiz GET `/` retornando texto simples

**Teste:** Servidor subiu em `http://localhost:5000/`, texto "StructConformity API rodando" exibido no navegador.

**Conceitos trabalhados:**
- `Flask(__name__)` - instancia do servidor web, `__name__` identifica o modulo
- `@app.route("/")` - decorator que registra funcao como rota
- `if __name__ == "__main__"` - execucao condicional (so roda direto, nao via import)
- `debug=True` - hot reload automatico ao salvar

**Status:** ✅ Concluido

### 2. Endpoint POST /predict

**O que faz:** Recebe dados de um elemento estrutural via JSON, passa para o modelo e retorna "conforme" ou "nao_conforme".

**Construcao:**
- Import de `request` e `jsonify`
- `@app.route("/predict", methods=["POST"])` - rota que aceita POST
- `request.get_json()` - extrai dados do corpo da requisicao
- `np.array([[ ... ]])` - monta array 1x10 na ordem das features do treino
- `model.predict(features)` - Pipeline faz scaler + predicao
- `jsonify()` - converte dicionario Python em resposta JSON

**Teste:** Requisicao POST via curl/Python com viga conforme retornou `{"prediction": "conforme"}`.

**Conceitos trabalhados:**
- Diferenca entre GET (pedir informacao) e POST (enviar dados)
- `request.get_json()` - parsing do corpo da requisicao
- `np.array([[ ]])` - colchetes duplos para formato matricial (1 amostra x N features)
- Mapeamento do LabelEncoder: beam=0, column=1, footing=2, slab=3

**Status:** ✅ Concluido

### 3. Documentacao automatica com Swagger (flask-openapi3)

**Mudancas no codigo:**
- Substituiu `Flask` por `OpenAPI` do `flask-openapi3`
- Adicionou `Info` com titulo e versao da API
- Trocou `@app.route()` por `@app.get()` e `@app.post()` (decorators especificos)
- Criou schema `PredictRequest` com `pydantic.BaseModel` e `Field` para documentar campos
- Parametro `body: PredictRequest` na funcao predict para validacao automatica

**Resultado:** Swagger UI acessivel em `http://localhost:5000/openapi/swagger` com todos os 10 campos documentados e testavel pelo browser.

**Teste pelo Swagger:** Viga com fck=19 retornou "conforme" (falso positivo). Discussao sobre limitacoes do modelo ML vs regras hard-coded da norma.

**Conceitos trabalhados:**
- OpenAPI/Swagger - especificacao que documenta APIs automaticamente
- `pydantic.BaseModel` - schema que define estrutura de dados com tipos e descricoes
- `Field(...)` - campo obrigatorio com metadata
- Diferenca entre regras exatas e aproximacao por ML (recall < 100%)

**Status:** ✅ Concluido

### 4. CORS configurado

**Mudanca:** Adicionou `from flask_cors import CORS` e `CORS(app)` no app.py.

**O que faz:** Permite que o frontend (arquivo HTML aberto no navegador) acesse a API Flask sem ser bloqueado pelo navegador.

**Status:** ✅ Concluido

### 5. Frontend completo (HTML + CSS + JS)

**Arquivos criados:**
- `frontend/index.html` - formulario com 10 campos (select para tipo, fck e bitola; input para os demais)
- `frontend/style.css` - design limpo e responsivo, card centralizado, grid 2 colunas, feedback visual verde/vermelho
- `frontend/script.js` - fetch POST para API, exibicao do resultado com classe CSS dinamica

**Decisoes de design:**
- Campos com `select` para valores discretos (tipo, fck, bitola) - evita entrada invalida
- Campos com `input number` e `step` para valores continuos
- Resultado com fundo verde (conforme) ou vermelho (nao conforme)
- Layout responsivo: 2 colunas em desktop, 1 coluna em mobile
- Botao desabilita durante requisicao para evitar duplo clique

**Status:** ✅ Concluido

### 6. Testes automatizados (PyTest)

**Arquivo:** `backend/test_model.py`

**4 testes criados:**
| Teste | Metrica | Threshold |
|-------|---------|-----------|
| test_accuracy | Acuracia geral | >= 0.85 |
| test_recall_nao_conforme | Recall classe 0 (NC) | >= 0.90 |
| test_precision_conforme | Precisao classe 1 (C) | >= 0.85 |
| test_f1_score | F1 ponderado | >= 0.85 |

**Detalhes de implementacao:**
- Usa `Path(__file__)` para resolver caminhos relativos (roda de qualquer diretorio)
- Reproduz o mesmo split do notebook (70/30, stratify, seed 42)
- Coluna renomeada para `element_type_encoded` (nome que o modelo espera)
- Ordem das features explicita para evitar erro de feature names

**Resultado:** 4/4 testes passando.

**Status:** ✅ Concluido

### 7. README.md do repositorio

**Conteudo:** Descricao do projeto, estrutura de pastas, instrucoes de instalacao e execucao, tabela de features, tecnologias usadas.

**Status:** ✅ Concluido

---

## Sessão 02 — 2026-04-12 — Reestruturação do dataset

### 1. Motivação

Refinar o dataset para focar apenas em vigas e pilares, remover features pouco discriminativas (`steel_rate`) e adicionar regras mais ricas pedagogicamente. Padronizar nomenclatura de dimensões (`dim_a`, `dim_b`, `dim_c`).

### 2. Schema novo

**Features (10):**
```
element_type, dim_a, dim_b, dim_c, fck, cover,
main_rebar_diam, main_rebar_quantity, stirrup_diam, stirrup_spacing
```

**Mudanças:**
- Removido: `steel_rate`, `length_cm`, `width_cm`, `height_cm`, `cover_cm`, `stirrup_spacing_cm`
- Removidos tipos `footing` e `slab` (fora do escopo)
- Adicionado `main_rebar_quantity` (quantidade de barras longitudinais)
- Renomeado dimensões para `dim_a`/`dim_b`/`dim_c` sem sufixo `_cm`
- Bitolas unificadas: `[4.2, 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 22.0, 25.0]`
- `FCK_OPTIONS` expandida para `[10, 15, 20, 25, 30, 35, 40, 45, 50]`

### 3. Regras de conformidade (9)

| # | Regra | Aplica a |
|---|---|---|
| 1 | cover >= 2.5 cm | todos |
| 2 | stirrup_spacing <= min(0.6·dim_b, 30) | todos |
| 3 | stirrup_diam >= 5.0 mm | todos |
| 4 | stirrup_spacing múltiplo de 5 | todos |
| 5 | fck >= 20 MPa | todos |
| 6 | dim_a >= 12 cm | viga |
| 7 | dim_a >= 19 cm | pilar |
| 8 | main_rebar_quantity >= 4 | todos |
| 9 | ρ = As/Ac >= ρmin(fck) (tabela NBR 6118) | viga |

**Premissa:** comprimento de cada barra longitudinal = `dim_c` (ignora ganchos/emendas).

### 4. Arquivos atualizados

- `dataset/generate_dataset.py` — reescrito do zero
- `notebook/struct_conformity_ml.ipynb` — outputs limpos, features renomeadas
- `notebook/train_and_export.py` — novo script de treino autônomo (espelha o notebook)
- `backend/app.py` — schema pydantic novo
- `backend/test_model.py` — `feature_cols` atualizada
- `frontend/index.html` — formulário reconstruído (selects de bitola, fck, etc.)
- `frontend/script.js` — lista de campos e parse int para `element_type`/`main_rebar_quantity`
- `backend/model/best_model.pkl` — retreinado

### 5. Resultados do treino

```
KNN            acc=0.7733
Decision Tree  acc=0.9767  ← selecionado
Naive Bayes    acc=0.8300
SVM            acc=0.8333
```

Decision Tree continua vencendo — esperado, já que a maioria das regras são thresholds e condicionais por categoria.

### 6. Testes automatizados

4/4 passam com thresholds atuais (acc ≥ 0.85, recall_NC ≥ 0.90, precision_C ≥ 0.85, f1 ≥ 0.85).

**Status:** ✅ Concluída
