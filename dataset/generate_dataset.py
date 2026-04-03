"""
Gerador de dataset sintético para o StructConformity.

Gera registros de elementos estruturais (viga, pilar, sapata, laje)
com propriedades variando dentro e fora dos limites da NBR 6118.
Cada registro é classificado como 'conforme' ou 'nao_conforme'
com base em 8 regras extraídas da norma.

Saída: structural_conformity.csv (~1000 registros, ~60/40)
"""

import random
import csv
import os

# ---------------------------------------------------------------------------
# Seed fixa para reprodutibilidade
# ---------------------------------------------------------------------------
random.seed(42)

# ---------------------------------------------------------------------------
# Constantes da NBR 6118 — limiares de conformidade
# ---------------------------------------------------------------------------
MIN_COVER_INTERNAL_CM = 2.5
MIN_COVER_EXTERNAL_CM = 3.0
MIN_STIRRUP_DIAM_MM = 5.0
MAX_STIRRUP_SPACING_FACTOR = 0.6
MAX_STIRRUP_SPACING_ABS_CM = 30.0
MIN_STEEL_RATE_BEAM_KG_M3 = 25.0
MAX_STEEL_RATE_KG_M3 = 200.0
MIN_FCK_MPA = 20.0
MIN_BEAM_WIDTH_CM = 12.0
MIN_COLUMN_WIDTH_CM = 19.0

# ---------------------------------------------------------------------------
# Tipos de elementos e seus ranges de geração
# ---------------------------------------------------------------------------
ELEMENT_TYPES = ["beam", "column", "footing", "slab"]

# Valores discretos realistas para cada feature
WIDTH_OPTIONS = list(range(10, 85, 5))          # 10, 15, 20, ..., 80 (múltiplos de 5)
HEIGHT_OPTIONS = list(range(15, 125, 5))         # 15, 20, 25, ..., 120 (múltiplos de 5)
FCK_OPTIONS = [15, 20, 25, 30, 35, 50]          # Classes de concreto comerciais
COVER_OPTIONS = [i * 0.5 for i in range(0, 10)] # 0, 0.5, 1.0, ..., 4.5 (múltiplos de 0.5)

# Ranges contínuos para features sem restrição discreta
RANGES = {
    "stirrup_spacing_cm": (5, 35),
    "steel_rate": (15, 250),
    "length_cm": (100, 1200),
}

# Bitolas comerciais de aço (mm)
MAIN_REBAR_OPTIONS = [8.0, 10.0, 12.5, 16.0, 20.0, 25.0, 32.0]
STIRRUP_OPTIONS = [4.2, 5.0, 6.3, 8.0, 10.0]


def random_in_range(low, high, decimals=1):
    """Gera valor aleatório no intervalo [low, high] arredondado."""
    return round(random.uniform(low, high), decimals)


def pick_rebar(options):
    """Escolhe uma bitola comercial aleatória."""
    return random.choice(options)


def check_conformity(row):
    """
    Aplica as 8 regras da NBR 6118 e retorna 'conforme' ou 'nao_conforme'.

    Um elemento é conforme APENAS se TODAS as regras aplicáveis forem atendidas.
    Basta uma violação para ser não conforme.
    """
    element_type = row["element_type"]
    width = row["width_cm"]
    height = row["height_cm"]
    fck = row["fck"]
    cover = row["cover_cm"]
    stirrup_diam = row["stirrup_diam"]
    stirrup_spacing = row["stirrup_spacing_cm"]
    steel_rate = row["steel_rate"]

    # Regra 1 — Cobrimento mínimo (simplificado: >= 2.5 para todos)
    if cover < MIN_COVER_INTERNAL_CM:
        return "nao_conforme"

    # Regra 2 — Espaçamento máximo de estribos: <= min(0.6 * h, 30)
    max_spacing = min(height * MAX_STIRRUP_SPACING_FACTOR, MAX_STIRRUP_SPACING_ABS_CM)
    if stirrup_spacing > max_spacing:
        return "nao_conforme"

    # Regra 3 — Diâmetro mínimo de estribo >= 5.0 mm
    if stirrup_diam < MIN_STIRRUP_DIAM_MM:
        return "nao_conforme"

    # Regra 4 — Taxa de armadura mínima para vigas >= 25 kg/m³
    if element_type == "beam" and steel_rate < MIN_STEEL_RATE_BEAM_KG_M3:
        return "nao_conforme"

    # Regra 5 — Taxa de armadura máxima <= 200 kg/m³
    if steel_rate > MAX_STEEL_RATE_KG_M3:
        return "nao_conforme"

    # Regra 6 — fck mínimo >= 20 MPa
    if fck < MIN_FCK_MPA:
        return "nao_conforme"

    # Regra 7 — Largura mínima de vigas >= 12 cm
    if element_type == "beam" and width < MIN_BEAM_WIDTH_CM:
        return "nao_conforme"

    # Regra 8 — Largura mínima de pilares >= 19 cm
    if element_type == "column" and width < MIN_COLUMN_WIDTH_CM:
        return "nao_conforme"

    return "conforme"


def generate_beam_dimensions():
    """
    Gera largura e altura para vigas com proporções realistas.

    Vigas têm altura maior que a largura:
    - width tipicamente entre 10 e 30 cm
    - height entre 1.5x e 4x a largura
    """
    width = random.choice([w for w in WIDTH_OPTIONS if 10 <= w <= 30])
    min_h = max(20, width * 2)
    max_h = min(120, width * 4)
    height_options = [h for h in HEIGHT_OPTIONS if min_h <= h <= max_h]
    height = random.choice(height_options) if height_options else width * 2
    return width, height


def generate_footing_dimensions():
    """
    Gera largura e altura para sapatas com proporções realistas.

    Sapatas têm formato quadrático ou levemente retangular:
    - width e height próximos (diferença máxima de ~30%)
    - height (espessura) tipicamente entre 30 e 80 cm
    """
    width = random.choice([w for w in WIDTH_OPTIONS if w >= 40])
    # Altura próxima da largura (+-30%), limitada a valores realistas
    min_h = max(30, int(width * 0.7))
    max_h = min(120, int(width * 1.3))
    height_options = [h for h in HEIGHT_OPTIONS if min_h <= h <= max_h]
    height = random.choice(height_options) if height_options else width
    return width, height


def generate_record_random():
    """Gera um registro totalmente aleatório (pode ou não ser conforme)."""
    element_type = random.choice(ELEMENT_TYPES)

    # Proporções específicas por tipo de elemento
    if element_type == "footing":
        width, height = generate_footing_dimensions()
    elif element_type == "beam":
        width, height = generate_beam_dimensions()
    else:
        width = random.choice(WIDTH_OPTIONS)
        height = random.choice(HEIGHT_OPTIONS)

    return {
        "element_type": element_type,
        "width_cm": width,
        "height_cm": height,
        "fck": random.choice(FCK_OPTIONS),
        "cover_cm": random.choice(COVER_OPTIONS),
        "main_rebar_diam": pick_rebar(MAIN_REBAR_OPTIONS),
        "stirrup_diam": pick_rebar(STIRRUP_OPTIONS),
        "stirrup_spacing_cm": random_in_range(*RANGES["stirrup_spacing_cm"]),
        "steel_rate": random_in_range(*RANGES["steel_rate"]),
        "length_cm": random_in_range(*RANGES["length_cm"], decimals=0),
    }


def generate_record_conforme():
    """
    Gera um registro propositalmente dentro dos limites da NBR 6118.

    Garante que todas as 8 regras sejam atendidas, com variação
    realista nos valores para que o modelo aprenda padrões, não decorar.
    """
    element_type = random.choice(ELEMENT_TYPES)

    # Largura respeitando mínimos por tipo (múltiplos de 5)
    if element_type == "footing":
        width, height = generate_footing_dimensions()
    elif element_type == "beam":
        width, height = generate_beam_dimensions()
    elif element_type == "column":
        width = random.choice([w for w in WIDTH_OPTIONS if w >= 20])
        height = random.choice([h for h in HEIGHT_OPTIONS if h >= 20])
    else:
        width = random.choice([w for w in WIDTH_OPTIONS if w >= 15])
        height = random.choice([h for h in HEIGHT_OPTIONS if h >= 20])

    # fck >= 20 MPa (exclui 15)
    fck = random.choice([f for f in FCK_OPTIONS if f >= 20])

    # Cobrimento >= 2.5 cm (múltiplos de 0.5)
    cover = random.choice([c for c in COVER_OPTIONS if c >= 2.5])

    # Bitola de estribo >= 5.0 mm (exclui 4.2)
    stirrup_diam = random.choice([5.0, 6.3, 8.0, 10.0])

    # Espaçamento de estribos <= min(0.6*h, 30)
    max_spacing = min(height * MAX_STIRRUP_SPACING_FACTOR, MAX_STIRRUP_SPACING_ABS_CM)
    stirrup_spacing = random_in_range(5, max_spacing)

    # Taxa de armadura: entre 25 e 200 (atende vigas e o limite máximo)
    steel_rate = random_in_range(25, 200)

    return {
        "element_type": element_type,
        "width_cm": width,
        "height_cm": height,
        "fck": fck,
        "cover_cm": cover,
        "main_rebar_diam": pick_rebar(MAIN_REBAR_OPTIONS),
        "stirrup_diam": stirrup_diam,
        "stirrup_spacing_cm": stirrup_spacing,
        "steel_rate": steel_rate,
        "length_cm": random_in_range(100, 1200, decimals=0),
    }


def generate_dataset(n=1000, target_conforme_ratio=0.60):
    """
    Gera o dataset completo com n registros, balanceado ~60/40.

    Estratégia de balanceamento:
    - 60% dos registros são gerados propositalmente conformes
    - 40% são gerados aleatoriamente (maioria será não conforme)
    - Registros aleatórios que caírem como conformes ajudam na variabilidade
    """
    n_conforme_target = int(n * target_conforme_ratio)
    n_random = n - n_conforme_target

    records = []

    # Gera registros propositalmente conformes
    for _ in range(n_conforme_target):
        record = generate_record_conforme()
        record["conformity"] = check_conformity(record)
        records.append(record)

    # Gera registros aleatórios (maioria será não conforme)
    for _ in range(n_random):
        record = generate_record_random()
        record["conformity"] = check_conformity(record)
        records.append(record)

    # Embaralha para não ter padrão posicional
    random.shuffle(records)

    return records


def save_csv(records, filepath):
    """Salva a lista de registros como CSV."""
    fieldnames = [
        "element_type",
        "width_cm",
        "height_cm",
        "fck",
        "cover_cm",
        "main_rebar_diam",
        "stirrup_diam",
        "stirrup_spacing_cm",
        "steel_rate",
        "length_cm",
        "conformity",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    """Ponto de entrada: gera dataset e exibe estatísticas."""
    records = generate_dataset(n=1000, target_conforme_ratio=0.50)

    # Estatísticas
    total = len(records)
    conformes = sum(1 for r in records if r["conformity"] == "conforme")
    nao_conformes = total - conformes

    print(f"Total de registros: {total}")
    print(f"Conformes:          {conformes} ({100 * conformes / total:.1f}%)")
    print(f"Não conformes:      {nao_conformes} ({100 * nao_conformes / total:.1f}%)")

    # Distribuição por tipo de elemento
    print("\nDistribuição por tipo de elemento:")
    for etype in ELEMENT_TYPES:
        count = sum(1 for r in records if r["element_type"] == etype)
        conf = sum(
            1
            for r in records
            if r["element_type"] == etype and r["conformity"] == "conforme"
        )
        print(f"  {etype:10s}: {count} registros ({conf} conformes, {count - conf} não conformes)")

    # Salvar
    output_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(output_dir, "structural_conformity.csv")
    save_csv(records, filepath)
    print(f"\nDataset salvo em: {filepath}")


if __name__ == "__main__":
    main()
