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
