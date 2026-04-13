const API_URL = "http://localhost:5000/predict";

const form = document.getElementById("predict-form");
const btn = document.getElementById("btn-predict");
const resultDiv = document.getElementById("result");
const resultIcon = document.getElementById("result-icon");
const resultTitle = document.getElementById("result-title");
const resultSubtitle = document.getElementById("result-subtitle");
const rhoDisplay = document.getElementById("rho_value");
const rhoBox = document.querySelector(".rho-live");
const dimCLabel = document.getElementById("dim_c_label");
const dimAHint = document.getElementById("dim_a_hint");
const dimBHint = document.getElementById("dim_b_hint");

const NUM_FIELDS = [
    "dim_a", "dim_b", "dim_c", "fck", "cover",
    "main_rebar_diam", "main_rebar_quantity", "stirrup_diam", "stirrup_spacing",
];
const INT_FIELDS = new Set(["main_rebar_quantity"]);

const PRESETS = {
    "viga-tipica": {
        element_type: "0",
        dim_a: 20, dim_b: 50, dim_c: 500,
        fck: "30", cover: "3",
        main_rebar_diam: "16.0", main_rebar_quantity: 6,
        stirrup_diam: "6.3", stirrup_spacing: 20,
    },
    "pilar-tipico": {
        element_type: "1",
        dim_a: 25, dim_b: 25, dim_c: 300,
        fck: "30", cover: "3",
        main_rebar_diam: "16.0", main_rebar_quantity: 8,
        stirrup_diam: "6.3", stirrup_spacing: 15,
    },
    "limpar": {
        element_type: "0",
        dim_a: "", dim_b: "", dim_c: "",
        fck: "25", cover: "3",
        main_rebar_diam: "10.0", main_rebar_quantity: "",
        stirrup_diam: "5.0", stirrup_spacing: "",
    },
};

// ─────────────────────────────────────────────────────────────
// UX: rótulos dinâmicos conforme tipo de elemento
function updateLabels() {
    const isColumn = document.querySelector('input[name="element_type"]:checked').value === "1";
    if (isColumn) {
        dimCLabel.textContent = "Altura do pilar (Z)";
        dimAHint.textContent = "dim_a (lado)";
        dimBHint.textContent = "dim_b (lado)";
    } else {
        dimCLabel.textContent = "Comprimento da viga";
        dimAHint.textContent = "dim_a (largura)";
        dimBHint.textContent = "dim_b (altura)";
    }
}

// ─────────────────────────────────────────────────────────────
// ρ ao vivo
function updateRho() {
    const phi = parseFloat(document.getElementById("main_rebar_diam").value);
    const qty = parseInt(document.getElementById("main_rebar_quantity").value);
    const a = parseFloat(document.getElementById("dim_a").value);
    const b = parseFloat(document.getElementById("dim_b").value);
    if (!phi || !qty || !a || !b) {
        rhoDisplay.textContent = "—";
        rhoBox.className = "rho-live";
        return;
    }
    const as = qty * Math.PI * Math.pow(phi / 20, 2);
    const ac = a * b;
    const rho = (as / ac) * 100;
    rhoDisplay.textContent = `ρ = ${rho.toFixed(2)} %`;

    const isColumn = document.querySelector('input[name="element_type"]:checked').value === "1";
    const max = isColumn ? 8.0 : 4.0;
    const min = isColumn ? 0.4 : 0.15;
    rhoBox.classList.remove("ok", "warn", "bad");
    if (rho < min * 0.8 || rho > max) rhoBox.classList.add("bad");
    else if (rho < min || rho > max * 0.9) rhoBox.classList.add("warn");
    else rhoBox.classList.add("ok");
}

// ─────────────────────────────────────────────────────────────
// Aplicar preset
function applyPreset(name) {
    const p = PRESETS[name];
    if (!p) return;
    document.querySelector(`input[name="element_type"][value="${p.element_type}"]`).checked = true;
    for (const [key, val] of Object.entries(p)) {
        if (key === "element_type") continue;
        const el = document.getElementById(key);
        if (el) el.value = val;
    }
    updateLabels();
    updateRho();
}

document.querySelectorAll(".preset").forEach((btn) => {
    btn.addEventListener("click", () => applyPreset(btn.dataset.preset));
});

document.querySelectorAll('input[name="element_type"]').forEach((r) => {
    r.addEventListener("change", () => { updateLabels(); updateRho(); });
});

NUM_FIELDS.forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", updateRho);
});

updateLabels();
updateRho();

// ─────────────────────────────────────────────────────────────
// Submit
form.addEventListener("submit", async (e) => {
    e.preventDefault();

    btn.disabled = true;
    btn.textContent = "Analisando...";
    resultDiv.classList.add("hidden");

    const data = {
        element_type: parseInt(document.querySelector('input[name="element_type"]:checked').value, 10),
    };
    for (const id of NUM_FIELDS) {
        const raw = document.getElementById(id).value;
        data[id] = INT_FIELDS.has(id) ? parseInt(raw, 10) : parseFloat(raw);
    }

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const result = await response.json();
        const isConforme = result.prediction === "conforme";

        resultDiv.className = "result " + (isConforme ? "conforme" : "nao_conforme");
        resultIcon.textContent = isConforme ? "✓" : "✗";
        resultTitle.textContent = isConforme ? "Conforme" : "Não conforme";
        resultSubtitle.textContent = isConforme
            ? "Elemento atende aos critérios da NBR 6118."
            : "Elemento viola ao menos uma regra da NBR 6118.";
    } catch (error) {
        resultDiv.className = "result nao_conforme";
        resultIcon.textContent = "!";
        resultTitle.textContent = "Erro";
        resultSubtitle.textContent = "Não foi possível conectar à API. Verifique se o servidor está rodando.";
    }

    btn.disabled = false;
    btn.textContent = "Verificar conformidade";
});
