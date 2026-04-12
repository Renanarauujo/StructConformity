"""
Desenho da secao transversal da viga 15x30 com 10 barras phi10 em 4 camadas.
Demonstra a Regra 12 (validate_rebar_spacing_beam) do StructConformity.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

# Parametros (cm / mm)
dim_a = 15.0     # largura
dim_b = 30.0     # altura
cover = 2.5
phi_stirrup = 0.5   # cm (5 mm)
phi_main = 1.0      # cm (10 mm)

# Disposicao: 4 camadas com 3,3,3,1 barras (total=10) — ajuste visual
layers = [3, 3, 3, 1]
n_layers = len(layers)

# Largura util
bw_util = dim_a - 2 * (cover + phi_stirrup)

# Posicoes Y das camadas (de baixo pra cima)
y_bottom = cover + phi_stirrup + phi_main / 2
vertical_spacing = 3.5  # cm entre centros de camadas
y_positions = [y_bottom + i * vertical_spacing for i in range(n_layers)]

fig, ax = plt.subplots(figsize=(4.5, 7))

# Secao de concreto
ax.add_patch(Rectangle((0, 0), dim_a, dim_b, facecolor="#d9d9d9",
                       edgecolor="#333", linewidth=1.5))

# Estribo (retangulo interno)
s_offset = cover
stirrup_width = dim_a - 2 * cover
stirrup_height = dim_b - 2 * cover
ax.add_patch(Rectangle((s_offset, s_offset), stirrup_width, stirrup_height,
                       fill=False, edgecolor="#cc0000", linewidth=2.0,
                       linestyle="--", label=f"Estribo phi5 a 15 cm"))

# Barras longitudinais (circulos)
for layer_idx, n_bars in enumerate(layers):
    y = y_positions[layer_idx]
    # x de 3.5 a 11.5 com n_bars equidistantes
    if n_bars == 1:
        xs = [dim_a / 2]
    else:
        x_start = cover + phi_stirrup + phi_main / 2
        x_end = dim_a - x_start
        xs = [x_start + k * (x_end - x_start) / (n_bars - 1) for k in range(n_bars)]
    for x in xs:
        ax.add_patch(Circle((x, y), phi_main / 2, facecolor="#1f4e79",
                            edgecolor="black", linewidth=0.5))

# Anotacoes de cota
ax.annotate("", xy=(0, -1), xytext=(dim_a, -1),
            arrowprops=dict(arrowstyle="<->", color="black"))
ax.text(dim_a / 2, -2.2, f"dim_a = {dim_a:.0f} cm", ha="center", fontsize=10)

ax.annotate("", xy=(-1, 0), xytext=(-1, dim_b),
            arrowprops=dict(arrowstyle="<->", color="black"))
ax.text(-2.5, dim_b / 2, f"dim_b = {dim_b:.0f} cm", ha="center",
        va="center", rotation=90, fontsize=10)

# Cobrimento
ax.annotate("cobrimento 2,5 cm", xy=(cover, dim_b - cover / 2),
            xytext=(dim_a + 2, dim_b - cover / 2),
            arrowprops=dict(arrowstyle="->", color="#555"), fontsize=9, color="#555")

# Legenda textual
info = (
    f"10 phi10 em 4 camadas\n"
    f"s_min = 2,28 cm (agregado 19 mm)\n"
    f"s_real = 3,00 cm (camada com 3 barras)\n"
    f"bw_util = {bw_util:.1f} cm\n"
    f"rho = 1,75 %"
)
ax.text(dim_a + 2, 2, info, fontsize=9, va="bottom",
        bbox=dict(boxstyle="round,pad=0.4", fc="#f7f7f7", ec="#999"))

ax.set_xlim(-4, dim_a + 12)
ax.set_ylim(-4, dim_b + 4)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Viga 15x30 — 10 phi10 — CONFORME", fontsize=12, fontweight="bold")

plt.tight_layout()
out = "viga_15x30_10phi10.png"
plt.savefig(out, dpi=150, bbox_inches="tight")
print(f"Imagem salva: {out}")
