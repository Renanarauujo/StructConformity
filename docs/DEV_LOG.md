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
- 45% dos registros são gerados propositalmente dentro dos limites (conformes)
- 55% são gerados aleatoriamente (maioria cai como não conforme)
- O mix resulta em ~60/40 conforme/não conforme

**Decisões importantes:**
- Seed fixa (`random.seed(42)`) para reprodutibilidade
- Bitolas de aço usam valores comerciais reais (8, 10, 12.5, 16, 20, 25, 32 mm)
- Ranges de geração incluem valores fora da norma para criar exemplos negativos realistas

**Status:** ✅ Concluído

### 3. Geração do CSV

**Comando:**
```
python dataset/generate_dataset.py
```

**Resultado:**
- 1000 registros gerados
- 617 conformes (61.7%)
- 383 não conformes (38.3%)
- Distribuição equilibrada entre os 4 tipos de elementos
- Salvo em `dataset/structural_conformity.csv`

**Status:** ✅ Concluído
