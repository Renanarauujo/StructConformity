# StructConformity — Data Context Completo

> Documento de referência que consolida todo o conhecimento das disciplinas da pós-graduação
> e os requisitos do MVP. Este documento serve como guia para desenvolvimento e consulta.

---

## 1. Contexto Acadêmico

### 1.1 Disciplinas Abordadas

| Disciplina | Foco | Impacto no MVP |
|-----------|------|----------------|
| Engenharia de Sistemas de Software Inteligentes | Contexto de Data Science, tipos de problemas ML, especificação (ML Canvas, PerSpecML) | Define o tipo de problema (classificação supervisionada) |
| Implementação de Modelos de Machine Learning | Algoritmos, métricas, pipelines, otimização | Core do notebook — todo o pipeline ML |
| Arquitetura e Qualidade de Sistemas Inteligentes | Implantação de modelos, SOLID, Design Patterns, DevOps | Arquitetura do backend (modelo embarcado), qualidade do código |
| Fundamentos de Teste de Software | Fases de teste, técnicas funcionais | Base teórica para os testes automatizados |
| Teste na Prática e TDD | PyTest, testes unitários, testes de integração | Implementação dos testes do modelo |
| Fundamentos de Segurança da Informação | CIA triad, criptografia, controle de acesso | Reflexão sobre segurança dos dados |
| Desenvolvimento de Software Seguro | OWASP, anonimização, boas práticas | Reflexão sobre anonimização aplicada ao problema |
| Cultura de Segurança em Software | Mindset, processos, governança | Complementa reflexão de segurança |
| Revisões e Análise Estática | Linters, code review, qualidade de processo | Qualidade do código Python (PEP-8) |

---

## 2. Fundamentos de Machine Learning (do curso)

### 2.1 Ciência de Dados — Visão Geral

- **Data Science** = coleta de dados de várias fontes para análise e apoio à tomada de decisão
- **KDD (Knowledge Discovery in Databases)** = processo de transformar dados brutos em conhecimento útil
- Etapas de um projeto de Data Science:
  1. Definição do problema
  2. Coleta e análise de dados
  3. Pré-processamento
  4. Modelagem e inferência
  5. Pós-processamento
  6. Apresentação dos resultados
  7. Implantação do modelo e geração de valor

### 2.2 Tipos de Aprendizado

| Tipo | Descrição | Dados | Exemplos |
|------|-----------|-------|----------|
| **Supervisionado** | Pares (entrada, saída desejada) — dados rotulados | Rotulados | Classificação, Regressão |
| **Não supervisionado** | Sem saída desejada — busca regularidades | Não rotulados | Clusterização, Associação |
| **Semissupervisionado** | Combina ambos | Parcialmente rotulados | — |
| **Por reforço** | Agente percebe ambiente, executa ações, recebe recompensas | Interação | Jogos, robótica |

### 2.3 Classificação vs Regressão

| Aspecto | Classificação | Regressão |
|---------|--------------|-----------|
| **Saída** | Categórica (classe) | Numérica (contínua/discreta) |
| **Exemplo** | "Conforme" / "Não conforme" | "Qual o valor do fck?" |
| **Nosso problema** | ✅ Classificação binária | — |

### 2.4 Holdout e Validação Cruzada

**Holdout:**
- Dividir dataset em treino (~70%) e teste (~30%)
- Modelo é treinado com treino e avaliado com teste
- Simples, mas depende da divisão

**Validação Cruzada (k-fold):**
- Dataset dividido em k subconjuntos (folds)
- A cada rodada, 1 fold é teste e k-1 são treino
- Repete k vezes, calcula média e desvio padrão
- Valores comuns de k: 3, 5, 10
- Estratificada: mantém proporção das classes em cada fold
- Mais confiável que holdout simples

### 2.5 Overfitting vs Underfitting

| Problema | O que acontece | Sintoma | Solução |
|----------|---------------|---------|---------|
| **Overfitting** | Modelo memoriza os dados de treino | Erro treino baixo, erro teste alto | Modelo mais simples, mais dados, validação cruzada |
| **Underfitting** | Modelo não aprendeu os padrões | Erro alto em ambos | Modelo mais complexo, mais features |
| **Bom ajuste** | Modelo generaliza bem | Erros similares em treino e teste | — |

---

## 3. Algoritmos de Classificação (obrigatórios no MVP)

### 3.1 KNN (K-Nearest Neighbors)

**O que é:** Algoritmo baseado em distância. Para classificar um novo exemplo, encontra os k vizinhos mais próximos nos dados de treino e atribui a classe mais frequente entre eles.

**Como funciona:**
1. Armazena todo o dataset de treino
2. Para novo exemplo, calcula distância (euclidiana) para todos os exemplos de treino
3. Seleciona os k mais próximos
4. Classe = voto majoritário dos k vizinhos

**Hiperparâmetros:**
- `n_neighbors` (k): número de vizinhos (testar 3, 5, 7, 9, 11)
- `metric`: distância (euclidiana, manhattan, minkowski)
- `weights`: uniforme ou ponderado por distância

**Cuidados:**
- Sensível à escala dos dados → **necessita normalização/padronização**
- Performance lenta em datasets grandes
- Sensível a features irrelevantes

### 3.2 Árvore de Classificação (Decision Tree)

**O que é:** Modelo que cria regras de decisão no formato de árvore. Cada nó interno testa um atributo, cada ramo representa um resultado do teste, cada folha representa uma classe.

**Como funciona:**
1. Seleciona o atributo que melhor separa as classes (maior ganho de informação / menor entropia)
2. Divide os dados recursivamente
3. Para até atingir critério de parada (profundidade máxima, nó puro, etc.)

**Hiperparâmetros:**
- `max_depth`: profundidade máxima da árvore
- `criterion`: gini ou entropy
- `min_samples_split`: mínimo de amostras para dividir um nó
- `min_samples_leaf`: mínimo de amostras em uma folha

**Cuidados:**
- Propensa a overfitting → usar poda (pruning) ou limitar profundidade
- **Não necessita normalização** (baseada em particionamento, não distância)
- Alta interpretabilidade (pode visualizar a árvore)

### 3.3 Naive Bayes

**O que é:** Classificador probabilístico baseado no Teorema de Bayes. Assume independência entre os atributos (hipótese "ingênua").

**Como funciona:**
1. Calcula probabilidades a priori de cada classe P(C)
2. Calcula probabilidades condicionais P(atributo | classe) para cada atributo
3. Para novo exemplo, calcula P(classe | atributos) usando Bayes
4. Classe = a que tiver maior probabilidade

**Hiperparâmetros:**
- `var_smoothing` (GaussianNB): suavização para evitar probabilidade zero

**Cuidados:**
- Rápido e eficiente
- Funciona bem com poucos dados
- Assume independência entre atributos (raramente verdade, mas funciona na prática)
- Bom como baseline

### 3.4 SVM (Support Vector Machine)

**O que é:** Encontra o hiperplano que melhor separa as classes, maximizando a margem entre elas. Usa vetores de suporte (pontos mais próximos da fronteira de decisão).

**Como funciona:**
1. Mapeia dados para espaço de dimensão maior (via kernel)
2. Encontra hiperplano que maximiza a margem entre classes
3. Vetores de suporte = pontos mais difíceis de classificar
4. Classificação = de que lado do hiperplano o novo exemplo cai

**Hiperparâmetros:**
- `C`: rigidez da margem (regularização). C pequeno = margem maior/mais flexível. C grande = margem menor/mais rígida
- `kernel`: linear, poly, rbf, sigmoid
- `gamma`: coeficiente do kernel (rbf, poly, sigmoid)

**Cuidados:**
- **Necessita normalização/padronização** (baseado em distância/produto interno)
- Treinamento lento em datasets grandes
- Menos propenso a overfitting
- Pode modelar fronteiras não-lineares (com kernel rbf)

---

## 4. Pré-processamento

### 4.1 Normalização (MinMaxScaler)

Redimensiona cada atributo para o intervalo [0, 1]:
```
X_normalizado = (X - X_min) / (X_max - X_min)
```
- Preserva a distribuição original dos dados
- Sensível a outliers

### 4.2 Padronização (StandardScaler)

Transforma cada atributo para média 0 e desvio padrão 1:
```
X_padronizado = (X - média) / desvio_padrão
```
- Transforma em distribuição normal padrão
- Menos sensível a outliers que normalização

### 4.3 Data Leakage — O que evitar

**Data Leakage** = "vazamento" de informações do teste para o treino. Ocorre quando:
- Normaliza/padroniza TODO o dataset antes de dividir treino/teste
- Parâmetros do pré-processamento são calculados com dados de teste

**Como evitar:**
1. Primeiro dividir treino/teste (holdout)
2. Calcular parâmetros de transformação APENAS com dados de treino
3. Aplicar transformação separadamente em treino e teste
4. **Usar Pipeline do Scikit-Learn** — garante automaticamente que não há vazamento

### 4.4 Pipeline (Scikit-Learn)

Encadeia pré-processamento + modelo em uma sequência:
```python
pipeline = Pipeline([
    ('scaler', StandardScaler()),
    ('classifier', SVC())
])
```
- Garante que transformação e treino usam apenas dados corretos
- Compatível com cross-validation e GridSearch
- **Obrigatório no MVP** conforme material do curso

---

## 5. Otimização de Hiperparâmetros

### 5.1 Grid Search

Busca exaustiva pela melhor combinação de hiperparâmetros:
```python
param_grid = {
    'classifier__n_neighbors': [3, 5, 7],
    'classifier__metric': ['euclidean', 'manhattan']
}
grid_search = GridSearchCV(pipeline, param_grid, cv=5, scoring='accuracy')
```
- Testa TODAS as combinações do grid
- Usa cross-validation para avaliar cada combinação
- Retorna melhor combinação e melhor score
- **Obrigatório no MVP** — otimizar cada um dos 4 algoritmos

---

## 6. Métricas de Avaliação

### 6.1 Matriz de Confusão

```
                Predito Conforme    Predito Não Conforme
Real Conforme       VP (True Pos)       FN (False Neg)
Real Não Conforme   FP (False Pos)      VN (True Neg)
```

### 6.2 Métricas derivadas

| Métrica | Fórmula | O que mede |
|---------|---------|------------|
| **Acurácia** | (VP + VN) / Total | Taxa de acerto geral |
| **Precisão** | VP / (VP + FP) | Dos que disse "conforme", quantos realmente são |
| **Recall** | VP / (VP + FN) | Dos que são conforme, quantos identificou |
| **F1-Score** | 2 × (Precisão × Recall) / (Precisão + Recall) | Média harmônica entre precisão e recall |

### 6.3 No contexto do StructConformity

- **Recall alto para "Não Conforme"** é crítico — não podemos deixar passar um elemento que viola a norma
- **Precisão alta para "Conforme"** é desejável — evitar alarmes falsos
- **F1-Score** equilibra ambos

---

## 7. Arquitetura do MVP

### 7.1 Forma de implantação: Modelo Embarcado

Conforme o material do curso, o modelo será **embarcado no backend**:
- Backend Python (Flask) carrega o arquivo `.pkl` ao iniciar
- Frontend envia dados via requisição HTTP
- Backend faz a predição e retorna resultado
- Modelo NÃO é um serviço separado

### 7.2 Exportação do modelo (pickle)

```python
import pickle
# Salvar
with open('modelo.pkl', 'wb') as f:
    pickle.dump(modelo, f)

# Carregar
with open('modelo.pkl', 'rb') as f:
    modelo = pickle.load(f)

# Predição
resultado = modelo.predict([[20, 50, 30, 3.0, 12.5, 5.0, 15]])
```

### 7.3 Princípios SOLID aplicados (conforme curso)

O código do notebook e do backend deve seguir SOLID. O curso exemplificou com classes:

| Classe | Responsabilidade (SRP) |
|--------|----------------------|
| `Carregador` | Carga dos dados (CSV via URL) |
| `PreProcessador` | Limpeza, seleção de features, holdout, normalização |
| `Modelo` | Treinamento do algoritmo (Pipeline + GridSearch) |
| `Avaliador` | Métricas de avaliação (acurácia, precisão, recall, F1) |

**Observação:** O requisito diz que NÃO é obrigatório usar classes no notebook, mas é recomendado seguir boas práticas de OOP.

---

## 8. Testes Automatizados (PyTest)

### 8.1 O que o curso exige

Conforme PDF "Arquitetura e Qualidade":
> "Para testar as predições dos modelos é preciso escolher **métricas adequadas** e **thresholds (valores limite)** aceitáveis para o desempenho do modelo, para determinar se o teste passou ou falhou."

### 8.2 Estrutura do teste

```python
# test_model.py
import pytest
import pickle

def test_model_accuracy():
    """Verifica se o modelo atende ao threshold mínimo de acurácia."""
    # Carregar modelo e dados de teste
    # Fazer predições
    # Calcular métricas
    assert accuracy >= 0.85, f"Acurácia {accuracy} abaixo do threshold 0.85"

def test_model_recall_nao_conforme():
    """Verifica se o recall para 'Não Conforme' é aceitável."""
    assert recall >= 0.90, f"Recall {recall} abaixo do threshold 0.90"
```

### 8.3 Propósito

> "Este teste deverá permitir, no caso da **substituição do modelo**, evitar a implantação de um modelo que não atenda aos requisitos de desempenho."

Se trocar o `.pkl` por um modelo pior → o teste falha → não vai para produção.

---

## 9. Segurança (Reflexão)

### 9.1 Tópicos das disciplinas de segurança

**Fundamentos:**
- Tríade CIA: Confidencialidade, Integridade, Disponibilidade
- Criptografia (simétrica/assimétrica), hashing
- Controle de acesso (autenticação, autorização)

**Desenvolvimento Seguro:**
- OWASP Top 10 (SQL Injection, XSS, CSRF, etc.)
- Validação de entrada
- Tratamento de erros seguro
- Gerenciamento de sessão
- Anonimização de dados

**Cultura de Segurança:**
- Security by design
- Threat modeling
- Resposta a incidentes

### 9.2 Aplicação ao StructConformity

Reflexão que deve constar no notebook:
- **Anonimização:** Dados de projetos estruturais podem conter informações sensíveis (localização da obra, nome do cliente, projetista). Técnicas: remoção de identificadores, generalização, k-anonimidade.
- **Integridade:** O modelo não pode ser adulterado — um modelo comprometido poderia aprovar elementos não conformes, com risco à segurança estrutural.
- **Confidencialidade:** Dados de projetos podem ser propriedade intelectual do escritório de engenharia.
- **Validação de entrada:** No frontend, validar que os valores inseridos fazem sentido (fck positivo, bitola dentro dos comerciais, etc.) — prevenção contra injection.

---

## 10. Requisitos do MVP — Checklist de Entrega

### 10.1 Notebook Colab (4,0 pts)

- [ ] Executa sem erros do início ao fim no Google Colab (1,0 pt)
- [ ] Dataset carregado via URL (raw GitHub)
- [ ] Blocos de texto explicando cada etapa — conta uma história (2,0 pts)
- [ ] Separação treino/teste (holdout)
- [ ] Normalização e/ou padronização
- [ ] Pipeline Scikit-Learn (evitar Data Leakage)
- [ ] 4 algoritmos: KNN, Árvore, Naive Bayes, SVM
- [ ] Otimização de hiperparâmetros (GridSearchCV)
- [ ] Cross-validation
- [ ] Comparação de resultados entre os 4 modelos
- [ ] Exportação do melhor modelo (.pkl)
- [ ] Análise final de resultados — resumo dos achados (1,0 pt)

### 10.2 Aplicação Full Stack (2,0 pts)

- [ ] Backend Python (Flask ou FastAPI)
- [ ] Carrega .pkl ao iniciar
- [ ] Endpoint que recebe dados e retorna predição
- [ ] Frontend HTML + CSS + JS
- [ ] Formulário com campos de entrada
- [ ] Exibe resultado da predição na tela

### 10.3 Teste Automatizado (1,0 pt)

- [ ] PyTest
- [ ] Testa métricas do modelo (accuracy, precision, recall, F1)
- [ ] Thresholds definidos
- [ ] Se trocar modelo por um pior, teste falha

### 10.4 Reflexão de Segurança (1,0 pt)

- [ ] Bloco de texto no notebook
- [ ] Mencionar técnicas de anonimização aplicáveis
- [ ] Considerar integridade, confidencialidade e disponibilidade

### 10.5 Entregáveis finais

- [ ] Repositório público no GitHub
- [ ] Notebook em formato Colab (salvo via "Salvar cópia no GitHub")
- [ ] Código completo da aplicação full stack
- [ ] Teste do modelo
- [ ] Vídeo de até 3 minutos
- [ ] Arquivos auxiliares necessários
- [ ] Link funcional

---

## 11. Boas Práticas de Notebooks (do curso)

- Títulos descritivos
- Imports no início do notebook
- Celulas markdown explicando cada etapa
- Caminhos relativos ou URLs para dados
- Declarar dependências (requirements.txt)
- Reexecutar do início ao fim antes de entregar
- Abstrair funções reutilizáveis
- Fixar versões de bibliotecas

---

## 12. Desenvolvimento Full Stack Básico (disciplina complementar)

### 12.1 Arquitetura Web e REST

**Restrições de Fielding para sistemas web escaláveis:**
- **Cliente-servidor:** separação de responsabilidades entre front e back
- **Uniformidade de interfaces:** comunicação via interfaces padronizadas (HTTP, URLs, status codes)
- **Sistema em camadas:** Camada 0 (browser) → Camada 1 (servidor de aplicação) → Camada 2 (banco de dados)
- **Stateless:** servidor não memoriza estado do cliente; toda informação vem na requisição
- **Cache:** servidor declara se dado é cacheável para reduzir latência
- **Code-on-demand:** servidor pode enviar scripts ao cliente (opcional)

**Protocolo HTTP:**
- Requisição: URL + Método (GET, POST, PUT, DELETE) + Cabeçalho + Corpo
- Resposta: Status code + Cabeçalho + Corpo
- Status codes: 1xx (info), 2xx (sucesso), 3xx (redirecionamento), 4xx (erro cliente), 5xx (erro servidor)

**Padrão MVC:**
- Model (dados), View (apresentação), Controller (lógica de controle)
- Separação de responsabilidades entre camadas

### 12.2 Frontend — HTML, CSS, JavaScript

**HTML:**
- Linguagem de marcação interpretada pelo navegador
- Tags com abertura e fechamento
- Estrutura: `<html>`, `<head>`, `<body>`

**CSS:**
- Linguagem de estilo para apresentação visual
- Seletores: elemento, classe (`.nome`), id (`#nome`)
- Box model: conteúdo → padding → border → margin
- Arquivo `.css` separado referenciado via `<link>`

**JavaScript:**
- Linguagem para interatividade no browser
- Interpretada em tempo real
- DOM (Document Object Model) = árvore de elementos HTML
- Arquivo `.js` separado referenciado via `<script>`
- `fetch()` para chamadas HTTP à API

**Frameworks/Bibliotecas de mercado:**
- React (Facebook, 2013), Vue, Angular
- Material UI (Google), Bootstrap (responsividade)
- Node.js + NPM para gerenciamento de pacotes

### 12.3 Backend Python — Flask

**Flask:**
- Micro-framework web para Python
- Padrão MVC adaptado
- Rotas decoradas com `@app.route()`
- Retorno JSON para APIs
- Integração com Flask-OpenAPI3 para documentação automática

**FastAPI como alternativa:**
- Mais moderno, tipagem com Pydantic
- Documentação automática (Swagger) inclusa
- Performance superior ao Flask

### 12.4 Documentação de API

**OpenAPI / Swagger:**
- Especificação para descrever APIs HTTP
- Padrões de visualização: Swagger UI, ReDoc, RapiDoc
- Documenta: recursos, rotas, métodos, estrutura de resposta
- Flask-OpenAPI3 ou FastAPI geram automaticamente

**Boas práticas de documentação:**
- Código é mais lido que escrito (Guido van Rossum)
- Clean Code (Robert C. Martin): nomes significativos, sem números mágicos
- PEP 8 (estilo) + PEP 257 (docstrings) para Python
- Comentários explicam o PORQUÊ, não o QUÊ

### 12.5 Deploy e Publicação

**4 etapas de deploy:**
1. Verificação de código (análise sintática/semântica, PEP 8, linters)
2. Execução de testes (unitários e de aceitação)
3. Geração de imagem (Docker, Kubernetes)
4. Publicação da imagem (variáveis de ambiente, monitoramento)

**3 ambientes:**
- TST (teste — equipe de desenvolvimento)
- HMG (homologação — teste com clientes)
- PRD (produção — cliente final)

### 12.6 Python e Orientação a Objetos

**Fundamentos Python:**
- Linguagem interpretada, tipagem dinâmica
- Variáveis criadas ao atribuir valor, sem declaração de tipo
- Tipos: int, float, bool, str
- Coleções: list, tuple, dict
- Controle: if/elif/else, for, while, break, continue
- Funções: `def nome(params):`, retorno com `return`

**Classes e Objetos:**
- Classe = molde, Objeto = instância
- `class NomeDaClasse:` (CamelCase)
- `__init__` = construtor, `self` = referência ao objeto
- Atributos de classe (compartilhados) vs atributos de instância

**4 Pilares da OOP:**

| Pilar | Conceito | Em Python |
|-------|----------|-----------|
| **Encapsulamento** | Agrupar dados e comportamento, proteger de acesso externo | `__atributo` (non-public) |
| **Herança** | Subclasse herda da superclasse | `class Filho(Pai):` |
| **Polimorfismo** | Objeto referenciado de várias formas | Método espera `Animal`, recebe `Cachorro` |
| **Abstração** | Classe que nunca é instanciada, define contrato | `from abc import ABC, abstractmethod` |

**Relacionamentos entre objetos:**
- **Associação:** objetos existem independentemente
- **Agregação:** todo e parte existem separados (revista e artigo)
- **Composição:** parte não existe sem o todo (livro e capítulo)

### 12.7 SOLID em Python (reforço)

| Princípio | Regra | Exemplo |
|-----------|-------|---------|
| **SRP** | Uma classe, uma responsabilidade | Separar `Animal` de `AnimalDAO` |
| **OCP** | Aberta para extensão, fechada para modificação | Subclasses em vez de ifs |
| **LSP** | Subclasse substituível pela superclasse | Métodos públicos na superclasse |
| **ISP** | Interfaces específicas > interface genérica | Separar Impressora, Digitalizadora, Fax |
| **DIP** | Depender de abstrações, não implementações | `passear(animal: Animal)` |

### 12.8 Bancos de Dados Relacionais

**Conceitos fundamentais:**
- SGBD gerencia dados com segurança e persistência
- Modelo Relacional (Codd, 1970): dados em tabelas (relações)
- Tupla = linha, Atributo = coluna, Domínio = tipo de dado
- Valores atômicos, NULL para desconhecido/inaplicável
- Esquema (estrutura) vs Instância (dados)

**Chaves:**
- Chave primária (PK): identifica unicamente cada tupla
- Chave estrangeira (FK): referência à PK de outra tabela
- Chave candidata, super-chave, chave composta, chave artificial (surrogate)

**Restrições de integridade:**
- De chave (unicidade)
- De entidade (PK não pode ser NULL)
- De domínio (tipo correto)
- Referencial (FK aponta para PK existente)

**Modelagem (MER → Relacional):**
- Entidades → tabelas
- Relacionamento 1:N → FK no lado N
- Relacionamento N:N → tabela associativa com PKs
- Relacionamento 1:1 → fusão ou FK
- Generalização/especialização (IS-A) → várias estratégias

**Normalização:**
- Dependências funcionais (X → Y)
- Formas normais para qualidade de esquemas
- Objetivo: eliminar redundância e anomalias

**Transações (ACID):**
- **A**tomicidade: tudo ou nada
- **C**onsistência: estado válido antes e depois
- **I**solamento: transações não interferem entre si
- **D**urabilidade: commit é permanente

### 12.9 SQL Completo

**DDL (Data Definition Language):**
```sql
CREATE TABLE elemento (
    id INTEGER PRIMARY KEY,
    nome VARCHAR(50) NOT NULL,
    fck INTEGER CHECK (fck >= 20),
    FOREIGN KEY (projeto_id) REFERENCES projeto(id)
);
ALTER TABLE elemento ADD COLUMN peso NUMERIC;
DROP TABLE elemento;
```

**DML (Data Manipulation Language):**
```sql
INSERT INTO elemento VALUES (1, 'V1', 30);
UPDATE elemento SET fck = 35 WHERE id = 1;
DELETE FROM elemento WHERE id = 1;
```

**Consultas:**
```sql
SELECT DISTINCT tipo, COUNT(*) as qtd
FROM elemento
WHERE fck >= 25
GROUP BY tipo
HAVING COUNT(*) > 5
ORDER BY qtd DESC;
```

**Junções:**
- INNER JOIN: apenas correspondências
- LEFT/RIGHT OUTER JOIN: inclui tuplas sem correspondência
- NATURAL JOIN: por atributos de mesmo nome
- Self-join: tabela consigo mesma (aliases obrigatórios)

**Operadores de conjunto:** UNION, INTERSECT, EXCEPT

**Funções agregadas:** MAX, MIN, AVG, SUM, COUNT

**Views:**
```sql
CREATE VIEW vigas_conformes AS
SELECT * FROM elemento WHERE tipo = 'beam' AND conforme = true;
```

**Índices:**
- Primário: criado com PK
- Secundário: `CREATE INDEX idx_nome ON tabela(coluna);`
- B-tree para busca eficiente
- Bom para consultas, pode impactar atualizações

---

## 13. Dataset StructConformity

### 12.1 Definição

Dataset **sintético** gerado a partir das regras da NBR 6118 para classificar elementos estruturais como **conformes** ou **não conformes**.

### 12.2 Features (atributos de entrada)

| Feature | Tipo | Unidade | Descrição |
|---------|------|---------|-----------|
| `element_type` | categórico | — | Tipo: beam, column, footing, slab |
| `width_cm` | numérico | cm | Largura da seção |
| `height_cm` | numérico | cm | Altura da seção |
| `fck` | numérico | MPa | Resistência característica do concreto |
| `cover_cm` | numérico | cm | Cobrimento da armadura |
| `main_rebar_diam` | numérico | mm | Bitola da armadura longitudinal |
| `stirrup_diam` | numérico | mm | Bitola do estribo |
| `stirrup_spacing_cm` | numérico | cm | Espaçamento dos estribos |
| `steel_rate` | numérico | kg/m³ | Taxa de armadura |
| `length_cm` | numérico | cm | Comprimento do elemento |

### 12.3 Target (saída)

| Feature | Tipo | Valores |
|---------|------|---------|
| `conformity` | binário | `conforme` / `nao_conforme` |

### 12.4 Regras de conformidade (baseadas na NBR 6118)

| Regra | Condição de conformidade |
|-------|-------------------------|
| Cobrimento mínimo | cover_cm >= 2.5 (interno) ou >= 3.0 (externo) |
| Espaçamento máximo de estribos | stirrup_spacing_cm <= min(height_cm * 0.6, 30) |
| Bitola mínima de estribo | stirrup_diam >= 5.0 |
| Taxa de armadura mínima | steel_rate >= 25 kg/m³ (vigas) |
| Taxa de armadura máxima | steel_rate <= 200 kg/m³ |
| fck mínimo | fck >= 20 MPa |
| Seção mínima de viga | width_cm >= 12 |
| Seção mínima de pilar | width_cm >= 19 (menor dimensão) |

### 12.5 Geração do dataset

- ~1000 registros
- ~60% conformes, ~40% não conformes (leve desbalanceamento)
- Valores gerados com variação aleatória dentro e fora dos limites da norma
- Será hospedado no repositório GitHub e carregado via URL raw

