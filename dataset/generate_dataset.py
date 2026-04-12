"""
Gerador de dataset sintético para o StructConformity.

Gera registros de elementos estruturais (viga, pilar) com propriedades
variando dentro e fora dos limites da NBR 6118. Cada registro é
classificado como 'conforme' ou 'nao_conforme' com base nas 9 regras
extraídas da norma.

Schema de features:
    element_type          : "beam" | "column"
    dim_a (cm)            : largura da seção
    dim_b (cm)            : altura da seção
    dim_c (cm)            : comprimento (viga) ou altura em Z (pilar)
    fck (MPa)             : resistência característica do concreto
    cover (cm)            : cobrimento
    main_rebar_diam (mm)  : bitola longitudinal
    main_rebar_quantity   : quantidade de barras longitudinais
    stirrup_diam (mm)     : bitola do estribo
    stirrup_spacing (cm)  : espaçamento dos estribos
    conformity            : 'conforme' | 'nao_conforme'

Premissa de domínio: comprimento de cada barra longitudinal = dim_c.

Saída: structural_conformity.csv
"""

import math
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
MIN_COVER_CM = 2.5
MIN_STIRRUP_DIAM_MM = 5.0
MAX_STIRRUP_SPACING_FACTOR = 0.6
MAX_STIRRUP_SPACING_ABS_CM = 30.0
MIN_FCK_MPA = 20.0
MIN_BEAM_WIDTH_CM = 12.0
MIN_COLUMN_WIDTH_CM = 19.0
MIN_REBAR_QUANTITY = 4

# Taxa de armadura maxima (rho = As/Ac, em %)
# Beam: 4% (NBR 6118, 17.3.5.3.2)
# Column: 8% (NBR 6118, 17.3.5.3.2 - inclui regioes de emenda)
MAX_RHO_BEAM_PCT = 4.0
MAX_RHO_COLUMN_PCT = 8.0

# Caps fisicos para o gerador random (evita combinacoes que nao cabem na secao)
PHYSICAL_CAP_RHO_BEAM_PCT = 6.0
PHYSICAL_CAP_RHO_COLUMN_PCT = 10.0

# Taxa mínima de armadura longitudinal em vigas (ρmin = As/Ac, em %)
# Tabela NBR 6118, truncada em fck = 50 MPa.
RHO_MIN_BY_FCK = {
    20: 0.150, 25: 0.150, 30: 0.150, 35: 0.164,
    40: 0.179, 45: 0.194, 50: 0.208,
}

# ---------------------------------------------------------------------------
# Tipos de elementos e seus ranges de geração
# ---------------------------------------------------------------------------
ELEMENT_TYPES = ["beam", "column"]

# Dimensões de seção (cm) — múltiplos de 5
DIM_A_OPTIONS = list(range(10, 85, 5))
DIM_B_OPTIONS = list(range(15, 125, 5))

# Classes de concreto: inclui 10 e 15 propositalmente para gerar violações
FCK_OPTIONS = [10, 15, 20, 25, 30, 35, 40, 45, 50]

# Cobrimento (cm) — múltiplos de 0.5
COVER_OPTIONS = [i * 0.5 for i in range(0, 10)]

# Bitolas comerciais unificadas (mm) — mesmas opções para longitudinal e estribo
REBAR_OPTIONS = [4.2, 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 22.0, 25.0]

# dim_c por tipo (cm, múltiplos de 5)
DIM_C_BEAM_OPTIONS = list(range(100, 1205, 5))
DIM_C_COLUMN_OPTIONS = list(range(250, 405, 5))

# Range contínuo de espaçamento de estribos (gera valores não-múltiplos de 5
# para alimentar a regra de múltiplo de 5)
STIRRUP_SPACING_RANGE = (5, 35)

# Quantidade de barras longitudinais
REBAR_QUANTITY_RANGE_RANDOM = (2, 20)
REBAR_QUANTITY_RANGE_CONFORME = (MIN_REBAR_QUANTITY, 20)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def random_in_range(low, high, decimals=1):
    """Gera valor aleatório no intervalo [low, high] arredondado."""
    return round(random.uniform(low, high), decimals)


def pick_rebar():
    """Escolhe uma bitola comercial aleatória."""
    return random.choice(REBAR_OPTIONS)


def bar_area_cm2(diam_mm):
    """Área da seção de uma barra (cm²) dada a bitola em mm."""
    # diam_mm / 10 → cm; raio = diam_cm / 2 → diam_mm / 20
    return math.pi * (diam_mm / 20.0) ** 2


def rho_percent(main_rebar_diam, main_rebar_quantity, dim_a, dim_b):
    """Taxa de armadura ρ = As/Ac em porcentagem."""
    as_total = main_rebar_quantity * bar_area_cm2(main_rebar_diam)
    ac = dim_a * dim_b
    return (as_total / ac) * 100.0


def is_multiple_of_5(value, tol=1e-6):
    """Testa se um float é múltiplo de 5 dentro de uma tolerância."""
    return abs(value - round(value / 5.0) * 5.0) < tol


# ---------------------------------------------------------------------------
# Regras de conformidade
# ---------------------------------------------------------------------------
def check_conformity(row):
    """
    Aplica as 9 regras da NBR 6118 e retorna 'conforme' ou 'nao_conforme'.

    Basta uma violação para ser não conforme.
    """
    element_type = row["element_type"]
    dim_a = row["dim_a"]
    dim_b = row["dim_b"]
    fck = row["fck"]
    cover = row["cover"]
    main_rebar_diam = row["main_rebar_diam"]
    main_rebar_quantity = row["main_rebar_quantity"]
    stirrup_diam = row["stirrup_diam"]
    stirrup_spacing = row["stirrup_spacing"]

    # Regra 1 — Cobrimento mínimo >= 2.5 cm
    if cover < MIN_COVER_CM:
        return "nao_conforme"

    # Regra 2 — Espaçamento máximo de estribos: <= min(0.6 * dim_b, 30)
    max_spacing = min(dim_b * MAX_STIRRUP_SPACING_FACTOR, MAX_STIRRUP_SPACING_ABS_CM)
    if stirrup_spacing > max_spacing:
        return "nao_conforme"

    # Regra 3 — Diâmetro mínimo de estribo >= 5.0 mm
    if stirrup_diam < MIN_STIRRUP_DIAM_MM:
        return "nao_conforme"

    # Regra 4 — Espaçamento de estribo deve ser múltiplo de 5 cm
    #           (padronização construtiva; evita cortes irregulares em obra)
    if not is_multiple_of_5(stirrup_spacing):
        return "nao_conforme"

    # Regra 5 — fck mínimo >= 20 MPa
    if fck < MIN_FCK_MPA:
        return "nao_conforme"

    # Regra 6 — Largura mínima de vigas >= 12 cm
    if element_type == "beam" and dim_a < MIN_BEAM_WIDTH_CM:
        return "nao_conforme"

    # Regra 7 — Largura mínima de pilares >= 19 cm
    if element_type == "column" and dim_a < MIN_COLUMN_WIDTH_CM:
        return "nao_conforme"

    # Regra 8 — Quantidade mínima de barras longitudinais >= 4
    if main_rebar_quantity < MIN_REBAR_QUANTITY:
        return "nao_conforme"

    # Regra 9 — Taxa mínima de armadura em VIGAS (ρ >= ρmin(fck), NBR 6118)
    rho = rho_percent(main_rebar_diam, main_rebar_quantity, dim_a, dim_b)
    if element_type == "beam" and fck in RHO_MIN_BY_FCK:
        if rho < RHO_MIN_BY_FCK[fck]:
            return "nao_conforme"

    # Regra 10 — Taxa máxima de armadura
    #   Viga:  ρ <= 4%  (NBR 6118, 17.3.5.3.2)
    #   Pilar: ρ <= 8%  (limite incluindo regiões de emenda)
    if element_type == "beam" and rho > MAX_RHO_BEAM_PCT:
        return "nao_conforme"
    if element_type == "column" and rho > MAX_RHO_COLUMN_PCT:
        return "nao_conforme"

    return "conforme"


# ---------------------------------------------------------------------------
# Geradores de dimensões por tipo de elemento
# ---------------------------------------------------------------------------
def generate_beam_dimensions():
    """
    Gera dim_a (largura) e dim_b (altura) de vigas com proporções realistas.

    Vigas têm altura maior que a largura:
    - dim_a tipicamente entre 10 e 30 cm
    - dim_b entre 1.5x e 4x a largura
    """
    dim_a = random.choice([w for w in DIM_A_OPTIONS if 10 <= w <= 30])
    min_b = max(20, dim_a * 2)
    max_b = min(120, dim_a * 4)
    dim_b_options = [h for h in DIM_B_OPTIONS if min_b <= h <= max_b]
    dim_b = random.choice(dim_b_options) if dim_b_options else dim_a * 2
    return dim_a, dim_b


def generate_column_dimensions():
    """Gera dim_a e dim_b de pilares (seção quadrada/retangular)."""
    dim_a = random.choice(DIM_A_OPTIONS)
    dim_b = random.choice(DIM_B_OPTIONS)
    return dim_a, dim_b


def generate_dim_c(element_type):
    """dim_c = comprimento (viga) ou altura em Z (pilar)."""
    if element_type == "beam":
        return random.choice(DIM_C_BEAM_OPTIONS)
    return random.choice(DIM_C_COLUMN_OPTIONS)


# ---------------------------------------------------------------------------
# Geradores de registros
# ---------------------------------------------------------------------------
def generate_record_random():
    """
    Gera um registro totalmente aleatório (pode ou não ser conforme).

    Aplica cap físico em ρ para evitar combinações impossíveis
    (ex.: 20 barras de 25mm em seção 10x20 — não caberiam).
    Reamostra (diam, qty) até ρ ficar abaixo do cap físico.
    """
    element_type = random.choice(ELEMENT_TYPES)

    if element_type == "beam":
        dim_a, dim_b = generate_beam_dimensions()
        cap = PHYSICAL_CAP_RHO_BEAM_PCT
    else:
        dim_a, dim_b = generate_column_dimensions()
        cap = PHYSICAL_CAP_RHO_COLUMN_PCT

    # Reamostra (diam, qty) até respeitar cap físico
    for _ in range(100):
        main_diam = pick_rebar()
        main_qty = random.randint(*REBAR_QUANTITY_RANGE_RANDOM)
        if rho_percent(main_diam, main_qty, dim_a, dim_b) <= cap:
            break

    return {
        "element_type": element_type,
        "dim_a": dim_a,
        "dim_b": dim_b,
        "dim_c": generate_dim_c(element_type),
        "fck": random.choice(FCK_OPTIONS),
        "cover": random.choice(COVER_OPTIONS),
        "main_rebar_diam": main_diam,
        "main_rebar_quantity": main_qty,
        "stirrup_diam": pick_rebar(),
        "stirrup_spacing": random_in_range(*STIRRUP_SPACING_RANGE),
    }


def _pick_conforme_rebar_combo(element_type, dim_a, dim_b, fck):
    """
    Escolhe (main_rebar_diam, main_rebar_quantity) que atenda à Regra 9
    (ρ >= ρmin) quando o elemento é viga. Para pilar, qualquer combo
    dentro do range conforme serve.

    Tenta até 50 sorteios; se nenhum satisfizer, retorna o par máximo
    (maior bitola e maior quantidade).
    """
    qty_lo, qty_hi = REBAR_QUANTITY_RANGE_CONFORME
    rebar_long_options = [d for d in REBAR_OPTIONS if d >= 8.0]

    rho_min = RHO_MIN_BY_FCK.get(fck, 0.0) if element_type == "beam" else 0.0
    rho_max = MAX_RHO_BEAM_PCT if element_type == "beam" else MAX_RHO_COLUMN_PCT

    for _ in range(100):
        diam = random.choice(rebar_long_options)
        qty = random.randint(qty_lo, qty_hi)
        rho = rho_percent(diam, qty, dim_a, dim_b)
        if rho_min <= rho <= rho_max:
            return diam, qty

    # Fallback: menor combo que cumpre rho_min (prioriza respeitar ρmax)
    for diam in rebar_long_options:
        for qty in range(qty_lo, qty_hi + 1):
            rho = rho_percent(diam, qty, dim_a, dim_b)
            if rho_min <= rho <= rho_max:
                return diam, qty
    return rebar_long_options[0], qty_lo


def generate_record_conforme():
    """
    Gera um registro propositalmente dentro dos limites da NBR 6118.

    Respeita todas as 9 regras aplicáveis.
    """
    element_type = random.choice(ELEMENT_TYPES)

    if element_type == "beam":
        dim_a, dim_b = generate_beam_dimensions()
        # Garante Regra 6 (viga: dim_a >= 12)
        if dim_a < MIN_BEAM_WIDTH_CM:
            dim_a = MIN_BEAM_WIDTH_CM
    else:
        dim_a, dim_b = generate_column_dimensions()
        # Garante Regra 7 (pilar: dim_a >= 19)
        while dim_a < MIN_COLUMN_WIDTH_CM:
            dim_a = random.choice(DIM_A_OPTIONS)

    dim_c = generate_dim_c(element_type)

    # Regra 5 — fck >= 20 (exclui 10 e 15)
    fck = random.choice([f for f in FCK_OPTIONS if f >= MIN_FCK_MPA])

    # Regra 1 — cobrimento >= 2.5 (múltiplos de 0.5)
    cover = random.choice([c for c in COVER_OPTIONS if c >= MIN_COVER_CM])

    # Regra 3 — estribo >= 5.0 mm (exclui 4.2)
    stirrup_diam = random.choice([d for d in REBAR_OPTIONS if d >= MIN_STIRRUP_DIAM_MM])

    # Regras 2 e 4 — espaçamento múltiplo de 5 e <= min(0.6*dim_b, 30)
    max_spacing = min(dim_b * MAX_STIRRUP_SPACING_FACTOR, MAX_STIRRUP_SPACING_ABS_CM)
    spacing_options = [s for s in range(5, 35, 5) if s <= max_spacing]
    stirrup_spacing = random.choice(spacing_options)

    # Regras 8 e 9 — quantidade >= 4 e (se viga) ρ >= ρmin(fck)
    main_rebar_diam, main_rebar_quantity = _pick_conforme_rebar_combo(
        element_type, dim_a, dim_b, fck
    )

    return {
        "element_type": element_type,
        "dim_a": dim_a,
        "dim_b": dim_b,
        "dim_c": dim_c,
        "fck": fck,
        "cover": cover,
        "main_rebar_diam": main_rebar_diam,
        "main_rebar_quantity": main_rebar_quantity,
        "stirrup_diam": stirrup_diam,
        "stirrup_spacing": float(stirrup_spacing),
    }


# ---------------------------------------------------------------------------
# Pipeline do dataset
# ---------------------------------------------------------------------------
def generate_dataset(n=1000, target_conforme_ratio=0.50):
    """Gera o dataset completo, balanceado conforme/não conforme."""
    n_conforme_target = int(n * target_conforme_ratio)
    n_random = n - n_conforme_target

    records = []

    for _ in range(n_conforme_target):
        record = generate_record_conforme()
        record["conformity"] = check_conformity(record)
        records.append(record)

    for _ in range(n_random):
        record = generate_record_random()
        record["conformity"] = check_conformity(record)
        records.append(record)

    random.shuffle(records)
    return records


def save_csv(records, filepath):
    """Salva a lista de registros como CSV."""
    fieldnames = [
        "element_type",
        "dim_a",
        "dim_b",
        "dim_c",
        "fck",
        "cover",
        "main_rebar_diam",
        "main_rebar_quantity",
        "stirrup_diam",
        "stirrup_spacing",
        "conformity",
    ]

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def main():
    """Ponto de entrada: gera dataset e exibe estatísticas."""
    records = generate_dataset(n=1000, target_conforme_ratio=0.50)

    total = len(records)
    conformes = sum(1 for r in records if r["conformity"] == "conforme")
    nao_conformes = total - conformes

    print(f"Total de registros: {total}")
    print(f"Conformes:          {conformes} ({100 * conformes / total:.1f}%)")
    print(f"Não conformes:      {nao_conformes} ({100 * nao_conformes / total:.1f}%)")

    print("\nDistribuição por tipo de elemento:")
    for etype in ELEMENT_TYPES:
        count = sum(1 for r in records if r["element_type"] == etype)
        conf = sum(
            1
            for r in records
            if r["element_type"] == etype and r["conformity"] == "conforme"
        )
        print(f"  {etype:8s}: {count} registros ({conf} conformes, {count - conf} não conformes)")

    output_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(output_dir, "structural_conformity.csv")
    save_csv(records, filepath)
    print(f"\nDataset salvo em: {filepath}")


if __name__ == "__main__":
    main()
