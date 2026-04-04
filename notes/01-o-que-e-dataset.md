# O que e um Dataset?

## Analogia com Engenharia Civil

Voce e engenheiro estrutural e precisa decidir se uma viga esta conforme a norma.
O que voce faz? Olha as propriedades dela (largura, altura, fck, cobrimento) e compara
com os limites da NBR 6118.

Um **dataset** e exatamente isso: uma tabela organizada com varios "casos" que voce
ja conhece a resposta. Cada linha e um caso. Cada coluna e uma propriedade.
A ultima coluna e a resposta que voce ja sabe.

Na engenharia civil, seria como pegar 1000 fichas de verificacao de elementos
estruturais de obras passadas, cada uma com as medicoes e o carimbo
"CONFORME" ou "NAO CONFORME" do engenheiro fiscal.

A diferenca? Em vez de um engenheiro analisar cada ficha, voce vai ensinar
um algoritmo a fazer isso sozinho, olhando os padroes dessas 1000 fichas.

## Termos Fundamentais

| Termo | Analogia | No nosso projeto |
|-------|----------|------------------|
| **Feature** (caracteristica) | As medicoes que voce coleta na obra | width_cm, height_cm, fck, cover_cm... |
| **Target** (rotulo) | O parecer do engenheiro fiscal | conformity (conforme / nao_conforme) |
| **Registro** (amostra) | Uma ficha de verificacao | Cada linha do CSV |

## Por que sintetico?

Em projetos reais de ML, voce coleta dados de obras reais. No nosso caso,
nao temos acesso a 1000 laudos reais de verificacao estrutural. Entao
**geramos os dados artificialmente** usando as regras da NBR 6118 como
"engenheiro fiscal automatizado".

Isso e comum em projetos academicos e ate em producao quando dados reais
sao escassos ou confidenciais.
