# 09 - Seguranca e Anonimizacao de Dados

> Reflexao sobre seguranca aplicada a dados de engenharia estrutural.

---

## Triade CIA

Os tres pilares da seguranca da informacao:

| Pilar | Significado | Exemplo no StructConformity |
|-------|------------|----------------------------|
| **Confidencialidade** | So quem tem permissao acessa os dados | Dados de projetos sao propriedade intelectual do escritorio |
| **Integridade** | Dados e modelo nao podem ser adulterados | Modelo comprometido poderia aprovar pecas defeituosas |
| **Disponibilidade** | Sistema acessivel quando necessario | Em obra, indisponibilidade atrasa verificacoes criticas |

---

## Riscos especificos em engenharia estrutural

O StructConformity tem um risco que a maioria dos sistemas de ML nao tem: **consequencias fisicas reais**.

- Se o modelo for adulterado e aprovar um elemento nao conforme, isso pode levar a uma falha estrutural
- Se dados de projetos vazarem, informacoes proprietarias do escritorio ficam expostas
- Se o sistema ficar fora do ar durante uma obra, verificacoes criticas atrasam

**Analogia:** A diferenca entre um modelo de ML que recomenda filmes e um que aprova armacao estrutural e que o segundo pode matar gente se errar.

---

## Anonimizacao de dados

Em um cenario com dados reais (nao sinteticos), os registros poderiam conter:
- Nome do cliente
- Endereco da obra
- Projetista responsavel
- Detalhes proprietarios do projeto

Tecnicas de anonimizacao aplicaveis:

| Tecnica | O que faz | Exemplo |
|---------|-----------|---------|
| **Remocao de identificadores** | Exclui campos que identificam diretamente | Remove nome do cliente, endereco |
| **Generalizacao** | Substitui valores exatos por faixas | "Sao Paulo" vira "Sudeste" |
| **K-anonimidade** | Garante que cada registro e indistinguivel de pelo menos k-1 outros | Com k=5, cada combinacao aparece no minimo 5 vezes |
| **Pseudonimizacao** | Substitui identificadores por codigos | "Joao Silva" vira "CLI-0042" (reversivel com chave) |

---

## Validacao de entrada

No frontend, validar dados inseridos pelo usuario:
- fck entre 15-50 MPa (valores comerciais)
- Cobrimento >= 0 cm
- Bitolas dentro dos valores comerciais
- Prevenir injecao de dados maliciosos nos campos do formulario
- Tratamento de erros que nao exponha informacoes internas
