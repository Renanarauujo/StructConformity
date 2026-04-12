const API_URL = "http://localhost:5000/predict";

const form = document.getElementById("predict-form");
const btn = document.getElementById("btn-predict");
const resultDiv = document.getElementById("result");
const resultIcon = document.getElementById("result-icon");
const resultText = document.getElementById("result-text");

const fields = [
    "element_type", "dim_a", "dim_b", "dim_c", "fck", "cover",
    "main_rebar_diam", "main_rebar_quantity", "stirrup_diam", "stirrup_spacing",
];

const intFields = new Set(["element_type", "main_rebar_quantity"]);

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    btn.disabled = true;
    btn.textContent = "Analisando...";
    resultDiv.classList.add("hidden");

    const data = {};
    fields.forEach((field) => {
        const raw = document.getElementById(field).value;
        data[field] = intFields.has(field) ? parseInt(raw, 10) : parseFloat(raw);
    });

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        const isConforme = result.prediction === "conforme";

        resultDiv.className = "result " + (isConforme ? "conforme" : "nao_conforme");
        resultIcon.textContent = isConforme ? "OK" : "X";
        resultText.textContent = isConforme
            ? "  Elemento CONFORME com a NBR 6118"
            : "  Elemento NÃO CONFORME com a NBR 6118";

    } catch (error) {
        resultDiv.className = "result nao_conforme";
        resultIcon.textContent = "!";
        resultText.textContent = "  Erro ao conectar com a API. Verifique se o servidor está rodando.";
    }

    btn.disabled = false;
    btn.textContent = "Verificar Conformidade";
});
