# StructConformity — Progresso do MVP

> Classificação de conformidade estrutural via Machine Learning
> Pós-graduação em Engenharia de Software — PUC-RJ

---

## Visão Geral [██░░░░░░░░] 9/47

---

## 1. Setup do Projeto [██████████] 7/7 ✅

- ✅ Abrir projeto no VS Code
- ✅ Criar ambiente virtual (python -m venv venv)
- ✅ Ativar venv
- ✅ Instalar dependências (flask, scikit-learn, pandas, numpy, pytest)
- ✅ Congelar versões (pip freeze > requirements.txt)
- ✅ Criar estrutura de pastas (backend, frontend, notebook, dataset, docs)
- ✅ Criar .gitignore

## 2. Dataset [░░░░░░░░░░] 0/5

- ⬜ Definir regras de conformidade da NBR 6118
- ⬜ Criar script Python para gerar dataset sintético
- ⬜ Gerar CSV (~1000 registros, ~60/40 conforme/não conforme)
- ⬜ Subir CSV no GitHub
- ⬜ Validar carga via URL raw do GitHub

## 3. Notebook Colab — ML [░░░░░░░░░░] 0/12

### 3.1 Carga e Exploração [░░░░░░░░░░] 0/3
- ⬜ Carregar dataset via URL
- ⬜ Análise exploratória (shape, describe, distribuição das classes)
- ⬜ Visualizações (histogramas, correlações)

### 3.2 Pré-processamento [░░░░░░░░░░] 0/3
- ⬜ Separação treino/teste (holdout)
- ⬜ Normalização (MinMaxScaler) e Padronização (StandardScaler)
- ⬜ Criar Pipelines (scaler + modelo) para evitar Data Leakage

### 3.3 Modelagem [░░░░░░░░░░] 0/4
- ⬜ Treinar KNN (com Pipeline)
- ⬜ Treinar Árvore de Classificação (com Pipeline)
- ⬜ Treinar Naive Bayes (com Pipeline)
- ⬜ Treinar SVM (com Pipeline)

### 3.4 Otimização [░░░░░░░░░░] 0/2
- ⬜ GridSearchCV com cross-validation para cada algoritmo
- ⬜ Comparar melhores hiperparâmetros de cada modelo

### 3.5 Avaliação [░░░░░░░░░░] 0/3
- ⬜ Matriz de confusão para cada modelo
- ⬜ Métricas: acurácia, precisão, recall, F1 — tabela comparativa
- ⬜ Análise final de resultados (bloco de texto com conclusões)

### 3.6 Exportação [░░░░░░░░░░] 0/1
- ⬜ Exportar melhor modelo como .pkl (pickle)

### 3.7 Documentação do Notebook [░░░░░░░░░░] 0/2
- ⬜ Blocos de texto explicando cada etapa (conta uma história)
- ⬜ Reflexão sobre segurança e anonimização de dados

## 4. Backend — API Flask [░░░░░░░░░░] 0/6

- ⬜ Criar app.py com Flask
- ⬜ Carregar modelo .pkl ao iniciar
- ⬜ Endpoint POST /predict (recebe dados, retorna predição)
- ⬜ Documentação automática (Swagger via flask-openapi3)
- ⬜ CORS configurado para o frontend
- ⬜ Testar via Swagger no browser

## 5. Frontend — HTML+CSS+JS [░░░░░░░░░░] 0/5

- ⬜ Criar index.html com formulário de entrada
- ⬜ Campos: tipo elemento, largura, altura, fck, cobrimento, bitolas, espaçamento, taxa
- ⬜ Estilizar com style.css
- ⬜ script.js — fetch para API, exibir resultado
- ⬜ Exibir "Conforme" ou "Não Conforme" com destaque visual

## 6. Testes — PyTest [░░░░░░░░░░] 0/4

- ⬜ Criar test_model.py
- ⬜ Teste de acurácia >= threshold
- ⬜ Teste de recall "Não Conforme" >= threshold
- ⬜ Rodar pytest e validar que todos passam

## 7. Repositório e Entrega [██░░░░░░░░] 1/5

- ✅ Inicializar Git e criar repositório no GitHub (privado — trocar para public na entrega)
- ⬜ Salvar notebook no Colab via "Salvar cópia no GitHub"
- ⬜ README.md com descrição do projeto
- ⬜ Gravar vídeo de 3 minutos
- ⬜ Validar que tudo roda (notebook executa sem erros, app funciona, testes passam)

## 8. Documentação Complementar [██░░░░░░░░] 1/3

- ✅ DATA_CONTEXT.md (referência completa das disciplinas)
- ⬜ DEV_LOG.md completo (registro de todas as sessões)
- ⬜ README.md do repositório
