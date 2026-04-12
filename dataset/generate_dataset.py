"""
Gerador de dataset sintetico para o StructConformity.

Gera registros de vigas e pilares com propriedades variando dentro e fora
dos limites da NBR 6118. Cada registro e classificado como 'conforme' ou
'nao_conforme' com base em regras geometricas e normativas.

Diferencas desta versao:
- Distribuicao perimetral de barras para PILARES (4 faces, nao linear).
- Espacamento minimo entre barras inclui criterio do agregado graudo
  (NBR 6118, 18.3.2.2): s_min = max(phi, 2 cm, 1.2 * diam agregado).
- Estribos de pilar seguem criterio especifico:
    s_max = min(20 cm, menor dimensao, 12 * phi_longitudinal).
- `check_conformity` retorna status + motivo (reason) para debugging.
- Regra de "multiplo de 5 cm" rebaixada a alerta construtivo (nao reprova).
- Geracao inclui casos limitrofes (proximos dos limites) para melhorar ML.
- Cap fisico substituido por validacao geometrica real
  (reamostragem por `validate_rebar_spacing_*`).

Schema das features (10):
    element_type, dim_a, dim_b, dim_c, fck, cover,
    main_rebar_diam, main_rebar_quantity, stirrup_diam, stirrup_spacing

Premissa de dominio: comprimento de cada barra longitudinal = dim_c.
Saida: structural_conformity.csv
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
# Constantes NBR 6118 / boas praticas
# ---------------------------------------------------------------------------
# Geral
MIN_COVER_CM = 2.5
MIN_FCK_MPA = 20.0

# Secao minima por tipo
MIN_BEAM_WIDTH_CM = 12.0
MIN_COLUMN_WIDTH_CM = 19.0

# Estribos
MIN_STIRRUP_DIAM_MM = 5.0
MAX_STIRRUP_DIAM_MM = 10.0  # acima de 10 e inviavel dobrar em obra
#   Viga: s_max_beam = min(0.6 * dim_b, 30)
MAX_STIRRUP_SPACING_BEAM_FACTOR = 0.6
MAX_STIRRUP_SPACING_BEAM_ABS_CM = 30.0
#   Pilar: s_max_col = min(20 cm, menor dim, 12 * phi_long)
MAX_STIRRUP_SPACING_COLUMN_ABS_CM = 20.0
STIRRUP_SPACING_COLUMN_PHI_FACTOR = 12.0

# Armadura longitudinal
MIN_REBAR_QUANTITY = 4

# Bitola longitudinal minima (NBR 6118)
#   Viga:  phi >= 8 mm  (caso especifico; ideal >= 10)
#   Pilar: phi >= 10 mm (nao se permite 8 mm)
MIN_MAIN_REBAR_DIAM_BEAM_MM = 8.0
MIN_MAIN_REBAR_DIAM_COLUMN_MM = 10.0

#   Taxa minima em vigas (rho = As/Ac, em %) — NBR 6118, tabela por fck
RHO_MIN_BEAM_BY_FCK = {
    20: 0.150, 25: 0.150, 30: 0.150, 35: 0.164,
    40: 0.179, 45: 0.194, 50: 0.208,
}
#   Taxa maxima/minima por tipo
MAX_RHO_BEAM_PCT = 4.0
MAX_RHO_COLUMN_PCT = 8.0
MIN_RHO_COLUMN_PCT = 0.4

# Espacamento entre barras (NBR 6118, 18.3.2.2)
MAX_AGGREGATE_MM = 19  # brita 1
MIN_BAR_SPACING_ABS_CM = 2.0
MIN_BAR_SPACING_AGG_FACTOR = 1.2
MAX_REBAR_LAYERS_BEAM = 4  # camadas em vigas

# ---------------------------------------------------------------------------
# Opcoes discretas
# ---------------------------------------------------------------------------
ELEMENT_TYPES = ["beam", "column"]

DIM_A_OPTIONS = list(range(10, 85, 5))     # cm
DIM_B_OPTIONS = list(range(15, 125, 5))    # cm

FCK_OPTIONS = [10, 15, 20, 25, 30, 35, 40, 45, 50]
COVER_OPTIONS = [i * 0.5 for i in range(0, 10)]

REBAR_OPTIONS = [4.2, 5.0, 6.3, 8.0, 10.0, 12.5, 16.0, 20.0, 22.0, 25.0]
STIRRUP_OPTIONS = [d for d in REBAR_OPTIONS if d <= MAX_STIRRUP_DIAM_MM]

DIM_C_BEAM_OPTIONS = list(range(100, 1205, 5))
DIM_C_COLUMN_OPTIONS = list(range(250, 405, 5))

STIRRUP_SPACING_RANGE = (5, 35)  # cm (continuo)

REBAR_QUANTITY_RANGE_RANDOM = (2, 20)
REBAR_QUANTITY_RANGE_CONFORME = (MIN_REBAR_QUANTITY, 20)


# ---------------------------------------------------------------------------
# Helpers numericos
# ---------------------------------------------------------------------------
def random_in_range(low, high, decimals=1):
    """Valor aleatorio no intervalo [low, high] arredondado."""
    return round(random.uniform(low, high), decimals)


def bar_area_cm2(diam_mm):
    """Area (cm^2) da secao de uma barra dada a bitola em mm."""
    return math.pi * (diam_mm / 20.0) ** 2


def rho_percent(main_rebar_diam, main_rebar_quantity, dim_a, dim_b):
    """Taxa de armadura rho = As/Ac, em %."""
    as_total = main_rebar_quantity * bar_area_cm2(main_rebar_diam)
    ac = dim_a * dim_b
    return (as_total / ac) * 100.0


def is_multiple_of_5(value, tol=1e-6):
    """Testa se um float e multiplo de 5 (dentro de tolerancia)."""
    return abs(value - round(value / 5.0) * 5.0) < tol


def min_bar_spacing_cm(main_rebar_diam_mm):
    """
    Espacamento minimo entre barras longitudinais (NBR 6118, 18.3.2.2).

        s_min = max(phi_barra, 2.0 cm, 1.2 * diam_agregado)
    """
    phi_cm = main_rebar_diam_mm / 10.0
    agg_cm = MAX_AGGREGATE_MM / 10.0
    return max(phi_cm, MIN_BAR_SPACING_ABS_CM, MIN_BAR_SPACING_AGG_FACTOR * agg_cm)


# ---------------------------------------------------------------------------
# Validacoes geometricas
# ---------------------------------------------------------------------------
def _face_util(dim_cm, cover_cm, stirrup_diam_cm):
    """Comprimento util de uma face = dim - 2*(cover + phi_estribo)."""
    return dim_cm - 2.0 * (cover_cm + stirrup_diam_cm)


def _fits_in_face(face_util_cm, n_bars, phi_main_cm, s_min_cm):
    """
    Testa se n_bars cabem numa face com folga >= s_min.

    Se n == 1 -> basta caber a barra.
    """
    if n_bars < 1:
        return False, None
    if phi_main_cm > face_util_cm:
        return False, None
    if n_bars == 1:
        return True, None
    s_real = (face_util_cm - n_bars * phi_main_cm) / (n_bars - 1)
    return s_real >= s_min_cm, s_real


def validate_rebar_spacing_beam(
    dim_a, dim_b, cover, stirrup_diam, main_rebar_diam, main_rebar_quantity,
):
    """
    Viga: distribuicao em camadas horizontais na base.

    Testa 1 a MAX_REBAR_LAYERS_BEAM camadas; retorna conforme se alguma
    camada acomodar a quantidade total respeitando espacamento minimo.
    Usa bw = min(dim_a, dim_b) como base da viga (caso canto).
    """
    phi_main_cm = main_rebar_diam / 10.0
    stirrup_diam_cm = stirrup_diam / 10.0
    bw = min(dim_a, dim_b)
    bw_util = _face_util(bw, cover, stirrup_diam_cm)

    result = {
        "status": "nao_conforme",
        "reason": "espacamento_insuficiente",
        "bw": bw, "bw_util": bw_util,
        "layers_used": None, "n_per_layer": None, "s_real": None,
    }

    if bw_util <= 0:
        result["reason"] = "geometria_invalida"
        return result

    s_min = min_bar_spacing_cm(main_rebar_diam)

    for layers in range(1, MAX_REBAR_LAYERS_BEAM + 1):
        n = math.ceil(main_rebar_quantity / layers)
        fits, s_real = _fits_in_face(bw_util, n, phi_main_cm, s_min)
        if fits:
            return {
                "status": "conforme",
                "reason": None,
                "bw": bw, "bw_util": bw_util,
                "layers_used": layers, "n_per_layer": n, "s_real": s_real,
            }

    return result


def validate_rebar_spacing_column(
    dim_a, dim_b, cover, stirrup_diam, main_rebar_diam, main_rebar_quantity,
):
    """
    Pilar: distribuicao perimetral em 4 faces.

    Considera grid retangular (n_a barras nas faces paralelas a dim_a,
    n_b barras nas faces paralelas a dim_b). Total = 2*(n_a+n_b) - 4
    (cantos compartilhados). Valida espacamento em cada direcao.

    Retorna conforme se existir algum par (n_a, n_b) com:
        2*(n_a + n_b) - 4 >= main_rebar_quantity
        espacamento em ambas direcoes >= s_min
    """
    phi_main_cm = main_rebar_diam / 10.0
    stirrup_diam_cm = stirrup_diam / 10.0

    face_a_util = _face_util(dim_a, cover, stirrup_diam_cm)
    face_b_util = _face_util(dim_b, cover, stirrup_diam_cm)

    result = {
        "status": "nao_conforme",
        "reason": "espacamento_insuficiente",
        "face_a_util": face_a_util, "face_b_util": face_b_util,
        "n_a": None, "n_b": None, "s_a": None, "s_b": None,
    }

    if face_a_util <= 0 or face_b_util <= 0:
        result["reason"] = "geometria_invalida"
        return result
    if main_rebar_quantity < 4:
        result["reason"] = "quantidade_insuficiente"
        return result

    s_min = min_bar_spacing_cm(main_rebar_diam)

    # Busca par (n_a, n_b) com total >= qty (permite margem de 1 barra)
    best = None
    for n_a in range(2, main_rebar_quantity + 1):
        for n_b in range(2, main_rebar_quantity + 1):
            total = 2 * (n_a + n_b) - 4
            if total < main_rebar_quantity:
                continue
            fits_a, s_a = _fits_in_face(face_a_util, n_a, phi_main_cm, s_min)
            fits_b, s_b = _fits_in_face(face_b_util, n_b, phi_main_cm, s_min)
            if fits_a and fits_b:
                candidate = {
                    "status": "conforme", "reason": None,
                    "face_a_util": face_a_util, "face_b_util": face_b_util,
                    "n_a": n_a, "n_b": n_b, "s_a": s_a, "s_b": s_b,
                    "total_bars": total,
                }
                # Prefere total igual a qty (sem excesso)
                if best is None or abs(total - main_rebar_quantity) < abs(best["total_bars"] - main_rebar_quantity):
                    best = candidate

    return best if best else result


def validate_rebar_spacing(
    element_type, dim_a, dim_b, cover, stirrup_diam, main_rebar_diam, main_rebar_quantity,
):
    """Dispatcher: chama a validacao de viga ou pilar conforme tipo."""
    if element_type == "beam":
        return validate_rebar_spacing_beam(
            dim_a, dim_b, cover, stirrup_diam, main_rebar_diam, main_rebar_quantity,
        )
    return validate_rebar_spacing_column(
        dim_a, dim_b, cover, stirrup_diam, main_rebar_diam, main_rebar_quantity,
    )


def max_stirrup_spacing(element_type, dim_a, dim_b, main_rebar_diam):
    """
    Espacamento maximo de estribos segundo NBR 6118.

    Viga:  s_max = min(0.6 * dim_b, 30 cm)
    Pilar: s_max = min(20 cm, menor_dim, 12 * phi_long_cm)
    """
    if element_type == "beam":
        return min(dim_b * MAX_STIRRUP_SPACING_BEAM_FACTOR, MAX_STIRRUP_SPACING_BEAM_ABS_CM)
    phi_long_cm = main_rebar_diam / 10.0
    return min(
        MAX_STIRRUP_SPACING_COLUMN_ABS_CM,
        min(dim_a, dim_b),
        STIRRUP_SPACING_COLUMN_PHI_FACTOR * phi_long_cm,
    )


# ---------------------------------------------------------------------------
# Regras de conformidade — retornam (status, reason)
# ---------------------------------------------------------------------------
REASONS = (
    "cobrimento_insuficiente",
    "stirrup_spacing_excedido",
    "stirrup_diam_invalido",
    "fck_invalido",
    "geometria_invalida",
    "quantidade_insuficiente",
    "rho_insuficiente",
    "rho_excedido",
    "espacamento_insuficiente",
    "main_rebar_diam_invalido",
)


def check_conformity_detailed(row):
    """
    Aplica as regras e retorna dict com status, reason e flags.

    - status: 'conforme' | 'nao_conforme'
    - reason: None ou uma das strings de REASONS
    - alerta_construtivo: True se stirrup_spacing nao for multiplo de 5
      (nao reprova; apenas sinaliza).
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

    def fail(reason):
        return {"status": "nao_conforme", "reason": reason, "alerta_construtivo": False}

    # Regra 1 — cobrimento
    if cover < MIN_COVER_CM:
        return fail("cobrimento_insuficiente")

    # Regra 2 — fck
    if fck < MIN_FCK_MPA:
        return fail("fck_invalido")

    # Regra 3 — geometria minima por tipo
    if element_type == "beam" and dim_a < MIN_BEAM_WIDTH_CM:
        return fail("geometria_invalida")
    if element_type == "column" and dim_a < MIN_COLUMN_WIDTH_CM:
        return fail("geometria_invalida")

    # Regra 4 — quantidade minima de barras
    if main_rebar_quantity < MIN_REBAR_QUANTITY:
        return fail("quantidade_insuficiente")

    # Regra 5 — estribo bitola minima
    if stirrup_diam < MIN_STIRRUP_DIAM_MM:
        return fail("stirrup_diam_invalido")

    # Regra 5b — bitola longitudinal minima por tipo (NBR 6118)
    if element_type == "beam" and main_rebar_diam < MIN_MAIN_REBAR_DIAM_BEAM_MM:
        return fail("main_rebar_diam_invalido")
    if element_type == "column" and main_rebar_diam < MIN_MAIN_REBAR_DIAM_COLUMN_MM:
        return fail("main_rebar_diam_invalido")

    # Regra 6 — estribo espacamento maximo (criterio por tipo)
    s_max = max_stirrup_spacing(element_type, dim_a, dim_b, main_rebar_diam)
    if stirrup_spacing > s_max:
        return fail("stirrup_spacing_excedido")

    # Regra 7 — taxa de armadura
    rho = rho_percent(main_rebar_diam, main_rebar_quantity, dim_a, dim_b)
    if element_type == "beam":
        rho_min = RHO_MIN_BEAM_BY_FCK.get(fck, 0.0)
        if rho < rho_min:
            return fail("rho_insuficiente")
        if rho > MAX_RHO_BEAM_PCT:
            return fail("rho_excedido")
    else:  # column
        if rho < MIN_RHO_COLUMN_PCT:
            return fail("rho_insuficiente")
        if rho > MAX_RHO_COLUMN_PCT:
            return fail("rho_excedido")

    # Regra 8 — espacamento geometrico real (cabem as barras?)
    geom = validate_rebar_spacing(
        element_type, dim_a, dim_b, cover,
        stirrup_diam, main_rebar_diam, main_rebar_quantity,
    )
    if geom["status"] != "conforme":
        return fail(geom.get("reason", "espacamento_insuficiente"))

    # Conforme. Sinaliza alerta construtivo se spacing nao for multiplo de 5
    alerta = not is_multiple_of_5(stirrup_spacing)
    return {"status": "conforme", "reason": None, "alerta_construtivo": alerta}


def check_conformity(row):
    """Wrapper compativel com o pipeline: retorna apenas a string de status."""
    return check_conformity_detailed(row)["status"]


# ---------------------------------------------------------------------------
# Geradores de dimensoes e dim_c
# ---------------------------------------------------------------------------
def generate_beam_dimensions():
    """dim_a (largura) e dim_b (altura) de viga."""
    dim_a = random.choice([w for w in DIM_A_OPTIONS if 10 <= w <= 30])
    min_b = max(20, dim_a * 2)
    max_b = min(120, dim_a * 4)
    opts = [h for h in DIM_B_OPTIONS if min_b <= h <= max_b]
    dim_b = random.choice(opts) if opts else dim_a * 2
    return dim_a, dim_b


def generate_column_dimensions():
    """dim_a e dim_b de pilar."""
    dim_a = random.choice(DIM_A_OPTIONS)
    dim_b = random.choice(DIM_B_OPTIONS)
    return dim_a, dim_b


def generate_dim_c(element_type):
    """Comprimento (viga) ou altura Z (pilar), em cm."""
    if element_type == "beam":
        return random.choice(DIM_C_BEAM_OPTIONS)
    return random.choice(DIM_C_COLUMN_OPTIONS)


# ---------------------------------------------------------------------------
# Geradores de registros
# ---------------------------------------------------------------------------
def _long_options_for(element_type):
    """Bitolas longitudinais permitidas por tipo (respeita regra 5b)."""
    phi_min = MIN_MAIN_REBAR_DIAM_COLUMN_MM if element_type == "column" else MIN_MAIN_REBAR_DIAM_BEAM_MM
    return [d for d in REBAR_OPTIONS if d >= phi_min]


def _sample_geometric_combo(element_type, dim_a, dim_b, cover, stirrup_diam, max_tries=200):
    """
    Sorteia (main_rebar_diam, main_rebar_quantity) que passe na validacao
    geometrica (cabem na secao). Retorna None se nao achar.
    """
    long_options = _long_options_for(element_type)
    qty_lo, qty_hi = REBAR_QUANTITY_RANGE_CONFORME

    for _ in range(max_tries):
        diam = random.choice(long_options)
        qty = random.randint(qty_lo, qty_hi)
        geom = validate_rebar_spacing(element_type, dim_a, dim_b, cover, stirrup_diam, diam, qty)
        if geom["status"] == "conforme":
            return diam, qty
    return None


def _sample_conforme_rebar_combo(element_type, dim_a, dim_b, fck, cover, stirrup_diam, max_tries=300):
    """
    Sorteia (diam, qty) que satisfaca simultaneamente:
      - taxa de armadura (rho_min <= rho <= rho_max)
      - validacao geometrica
    """
    long_options = _long_options_for(element_type)
    qty_lo, qty_hi = REBAR_QUANTITY_RANGE_CONFORME

    if element_type == "beam":
        rho_min = RHO_MIN_BEAM_BY_FCK.get(fck, 0.0)
        rho_max = MAX_RHO_BEAM_PCT
    else:
        rho_min = MIN_RHO_COLUMN_PCT
        rho_max = MAX_RHO_COLUMN_PCT

    for _ in range(max_tries):
        diam = random.choice(long_options)
        qty = random.randint(qty_lo, qty_hi)
        rho = rho_percent(diam, qty, dim_a, dim_b)
        if not (rho_min <= rho <= rho_max):
            continue
        geom = validate_rebar_spacing(element_type, dim_a, dim_b, cover, stirrup_diam, diam, qty)
        if geom["status"] == "conforme":
            return diam, qty
    return None


def generate_record_random():
    """Registro totalmente aleatorio (pode ou nao ser conforme).

    Aplica validacao geometrica como cap fisico: reamostra se o arranjo
    de barras nao cabe na secao.
    """
    element_type = random.choice(ELEMENT_TYPES)

    if element_type == "beam":
        dim_a, dim_b = generate_beam_dimensions()
    else:
        dim_a, dim_b = generate_column_dimensions()

    cover = random.choice(COVER_OPTIONS)
    stirrup_diam = random.choice(STIRRUP_OPTIONS)

    combo = _sample_geometric_combo(element_type, dim_a, dim_b, cover, stirrup_diam)
    if combo is None:
        # Fallback: menor combo viavel
        main_diam, main_qty = 8.0, MIN_REBAR_QUANTITY
    else:
        main_diam, main_qty = combo

    return {
        "element_type": element_type,
        "dim_a": dim_a,
        "dim_b": dim_b,
        "dim_c": generate_dim_c(element_type),
        "fck": random.choice(FCK_OPTIONS),
        "cover": cover,
        "main_rebar_diam": main_diam,
        "main_rebar_quantity": main_qty,
        "stirrup_diam": stirrup_diam,
        "stirrup_spacing": random_in_range(*STIRRUP_SPACING_RANGE),
    }


def generate_record_conforme():
    """Registro propositalmente dentro de todos os limites."""
    element_type = random.choice(ELEMENT_TYPES)

    if element_type == "beam":
        dim_a, dim_b = generate_beam_dimensions()
        if dim_a < MIN_BEAM_WIDTH_CM:
            dim_a = MIN_BEAM_WIDTH_CM
    else:
        dim_a, dim_b = generate_column_dimensions()
        while dim_a < MIN_COLUMN_WIDTH_CM:
            dim_a = random.choice(DIM_A_OPTIONS)

    dim_c = generate_dim_c(element_type)
    fck = random.choice([f for f in FCK_OPTIONS if f >= MIN_FCK_MPA])
    cover = random.choice([c for c in COVER_OPTIONS if c >= MIN_COVER_CM])
    stirrup_diam = random.choice([d for d in STIRRUP_OPTIONS if d >= MIN_STIRRUP_DIAM_MM])

    combo = _sample_conforme_rebar_combo(element_type, dim_a, dim_b, fck, cover, stirrup_diam)
    if combo is None:
        main_diam, main_qty = 10.0, MIN_REBAR_QUANTITY
    else:
        main_diam, main_qty = combo

    s_max = max_stirrup_spacing(element_type, dim_a, dim_b, main_diam)
    # Gera spacing dentro do limite (nao precisa ser multiplo de 5)
    stirrup_spacing = round(random.uniform(5, max(5.1, s_max)), 1)

    return {
        "element_type": element_type,
        "dim_a": dim_a,
        "dim_b": dim_b,
        "dim_c": dim_c,
        "fck": fck,
        "cover": cover,
        "main_rebar_diam": main_diam,
        "main_rebar_quantity": main_qty,
        "stirrup_diam": stirrup_diam,
        "stirrup_spacing": stirrup_spacing,
    }


def generate_record_phi42_violation():
    """
    Registro com bitola longitudinal 4,2 mm — bitola CA-60 usada em
    malhas/armadura de distribuicao, inadequada como armadura principal
    de viga/pilar. Quase sempre resulta em rho_insuficiente.

    Gera combinacoes VALIDAS geometricamente e em cobrimento/fck/estribo
    para que a unica violacao seja a taxa de armadura (rho_min).
    """
    element_type = random.choice(ELEMENT_TYPES)

    if element_type == "beam":
        dim_a, dim_b = generate_beam_dimensions()
    else:
        dim_a, dim_b = generate_column_dimensions()
        while dim_a < MIN_COLUMN_WIDTH_CM:
            dim_a = random.choice(DIM_A_OPTIONS)

    # Tudo conforme EXCETO rho (que sera insuficiente com phi 4,2)
    cover = random.choice([c for c in COVER_OPTIONS if c >= MIN_COVER_CM])
    fck = random.choice([f for f in FCK_OPTIONS if f >= MIN_FCK_MPA])
    stirrup_diam = random.choice([d for d in STIRRUP_OPTIONS if d >= MIN_STIRRUP_DIAM_MM])
    main_diam = 4.2
    main_qty = random.randint(MIN_REBAR_QUANTITY, 12)
    s_max = max_stirrup_spacing(element_type, dim_a, dim_b, main_diam)
    stirrup_spacing = round(random.uniform(5, max(5.1, s_max)), 1)

    return {
        "element_type": element_type,
        "dim_a": dim_a,
        "dim_b": dim_b,
        "dim_c": generate_dim_c(element_type),
        "fck": fck,
        "cover": cover,
        "main_rebar_diam": main_diam,
        "main_rebar_quantity": main_qty,
        "stirrup_diam": stirrup_diam,
        "stirrup_spacing": stirrup_spacing,
    }


def generate_record_borderline():
    """
    Registro proximo de algum limite — importante para ML aprender a
    fronteira de decisao.

    Variacoes sorteadas:
      - rho proximo do maximo ou minimo
      - stirrup_spacing proximo do s_max
      - cover proximo de 2.5
    """
    base = generate_record_conforme()
    strategy = random.choice(["rho_max", "rho_min", "spacing_max", "cover_edge"])

    if strategy == "cover_edge":
        base["cover"] = random.choice([2.5, 3.0])
    elif strategy == "spacing_max":
        s_max = max_stirrup_spacing(
            base["element_type"], base["dim_a"], base["dim_b"], base["main_rebar_diam"]
        )
        base["stirrup_spacing"] = round(max(5.0, s_max - random.uniform(0.0, 1.0)), 1)
    elif strategy in ("rho_max", "rho_min"):
        # Tenta ajustar qty para ficar perto do limite
        rho_target = MAX_RHO_BEAM_PCT if base["element_type"] == "beam" and strategy == "rho_max" else (
            MAX_RHO_COLUMN_PCT if strategy == "rho_max" else (
                RHO_MIN_BEAM_BY_FCK.get(base["fck"], 0.15) if base["element_type"] == "beam"
                else MIN_RHO_COLUMN_PCT
            )
        )
        ac = base["dim_a"] * base["dim_b"]
        target_as = (rho_target / 100.0) * ac
        diam = base["main_rebar_diam"]
        qty = max(MIN_REBAR_QUANTITY, min(20, round(target_as / bar_area_cm2(diam))))
        base["main_rebar_quantity"] = qty
    return base


# ---------------------------------------------------------------------------
# Pipeline do dataset
# ---------------------------------------------------------------------------
def generate_dataset(
    n=2000,
    target_conforme_ratio=0.50,
    borderline_ratio=0.30,
    phi42_ratio=0.15,
    max_attempts_factor=10,
):
    """
    Gera o dataset balanceado conforme/nao_conforme.

    Estrategia:
      - ~50% conformes (inclui fracao borderline proximos dos limites).
      - ~50% nao-conformes (random rejeitado via retry).
    """
    n_conf_target = int(n * target_conforme_ratio)
    n_nc_target = n - n_conf_target
    n_borderline = int(n_conf_target * borderline_ratio)
    n_plain_conf = n_conf_target - n_borderline

    max_attempts = n * max_attempts_factor
    conformes = []
    nao_conformes = []

    # Conformes "comuns"
    attempts = 0
    while len(conformes) < n_plain_conf and attempts < max_attempts:
        rec = generate_record_conforme()
        rec["conformity"] = check_conformity(rec)
        if rec["conformity"] == "conforme":
            conformes.append(rec)
        attempts += 1

    # Conformes "borderline"
    attempts = 0
    while len(conformes) < n_conf_target and attempts < max_attempts:
        rec = generate_record_borderline()
        rec["conformity"] = check_conformity(rec)
        if rec["conformity"] == "conforme":
            conformes.append(rec)
        attempts += 1

    # Nao conformes: parcela dedicada a violacoes com phi 4,2 (hard negatives)
    n_phi42 = int(n_nc_target * phi42_ratio)
    attempts = 0
    while sum(1 for r in nao_conformes) < n_phi42 and attempts < max_attempts:
        rec = generate_record_phi42_violation()
        rec["conformity"] = check_conformity(rec)
        if rec["conformity"] == "nao_conforme":
            nao_conformes.append(rec)
        attempts += 1

    # Restante via random
    attempts = 0
    while len(nao_conformes) < n_nc_target and attempts < max_attempts:
        rec = generate_record_random()
        rec["conformity"] = check_conformity(rec)
        if rec["conformity"] == "nao_conforme":
            nao_conformes.append(rec)
        attempts += 1

    records = conformes + nao_conformes
    random.shuffle(records)
    return records


def save_csv(records, filepath):
    """Salva os registros como CSV (schema fixo)."""
    fieldnames = [
        "element_type",
        "dim_a", "dim_b", "dim_c",
        "fck", "cover",
        "main_rebar_diam", "main_rebar_quantity",
        "stirrup_diam", "stirrup_spacing",
        "conformity",
    ]
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)


def main():
    """Gera dataset e exibe estatisticas."""
    records = generate_dataset(n=6000, target_conforme_ratio=0.50)

    total = len(records)
    conformes = sum(1 for r in records if r["conformity"] == "conforme")
    nao_conformes = total - conformes

    print(f"Total de registros: {total}")
    print(f"Conformes:          {conformes} ({100 * conformes / total:.1f}%)")
    print(f"Nao conformes:      {nao_conformes} ({100 * nao_conformes / total:.1f}%)")

    print("\nDistribuicao por tipo de elemento:")
    for etype in ELEMENT_TYPES:
        count = sum(1 for r in records if r["element_type"] == etype)
        conf = sum(
            1 for r in records
            if r["element_type"] == etype and r["conformity"] == "conforme"
        )
        print(f"  {etype:8s}: {count} registros ({conf} conformes, {count - conf} nao conformes)")

    # Distribuicao de motivos nos nao-conformes (para diagnostico)
    from collections import Counter
    reasons = Counter()
    for r in records:
        detail = check_conformity_detailed(r)
        if detail["status"] == "nao_conforme":
            reasons[detail["reason"]] += 1
    if reasons:
        print("\nMotivos de nao-conformidade:")
        for reason, count in reasons.most_common():
            print(f"  {reason:30s}: {count}")

    output_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(output_dir, "structural_conformity.csv")
    save_csv(records, filepath)
    print(f"\nDataset salvo em: {filepath}")


if __name__ == "__main__":
    main()
