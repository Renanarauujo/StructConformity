"""
Testes automatizados para o modelo de classificação de conformidade estrutural.

Objetivo: garantir que o modelo atende aos thresholds mínimos de performance.
Se o modelo for substituído por um pior, os testes falham e impedem a implantação.
"""
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# ── Thresholds mínimos de performance ──────────────────────────────────────
ACCURACY_THRESHOLD = 0.85
RECALL_NC_THRESHOLD = 0.90
PRECISION_C_THRESHOLD = 0.85
F1_THRESHOLD = 0.85

# ── Fixtures: carregamento do modelo e dados ───────────────────────────────
BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR / "model" / "best_model.pkl"
DATASET_PATH = BASE_DIR.parent / "dataset" / "structural_conformity.csv"


def load_model_and_data():
    """Carrega o modelo e prepara os dados de teste."""
    model = joblib.load(MODEL_PATH)

    df = pd.read_csv(DATASET_PATH)

    le = LabelEncoder()
    df["element_type_encoded"] = le.fit_transform(df["element_type"])

    feature_cols = [
        "element_type_encoded", "dim_a", "dim_b", "dim_c", "fck", "cover",
        "main_rebar_diam", "main_rebar_quantity", "stirrup_diam", "stirrup_spacing",
    ]
    X = df[feature_cols]
    y = df["conformity"].map({"conforme": 1, "nao_conforme": 0})

    # Mesmo split do notebook: 70/30, stratify, seed 42
    from sklearn.model_selection import train_test_split
    _, X_test, _, y_test = train_test_split(X, y, test_size=0.3, stratify=y, random_state=42)

    y_pred = model.predict(X_test)
    return y_test, y_pred


y_test, y_pred = load_model_and_data()


def test_accuracy():
    """Verifica se a acurácia geral atende ao threshold mínimo."""
    accuracy = accuracy_score(y_test, y_pred)
    assert accuracy >= ACCURACY_THRESHOLD, (
        f"Acurácia {accuracy:.4f} abaixo do threshold {ACCURACY_THRESHOLD}"
    )


def test_recall_nao_conforme():
    """Verifica se o recall para 'Não Conforme' é aceitável.

    Recall NC alto = poucos elementos defeituosos escapam da detecção.
    Em engenharia estrutural, aprovar uma peça não conforme é o pior cenário.
    """
    recall = recall_score(y_test, y_pred, pos_label=0)
    assert recall >= RECALL_NC_THRESHOLD, (
        f"Recall Não Conforme {recall:.4f} abaixo do threshold {RECALL_NC_THRESHOLD}"
    )


def test_precision_conforme():
    """Verifica se a precisão para 'Conforme' é aceitável.

    Precisão C alta = quando o modelo diz conforme, ele está certo.
    Evita alarmes falsos que geram retrabalho desnecessário.
    """
    precision = precision_score(y_test, y_pred, pos_label=1)
    assert precision >= PRECISION_C_THRESHOLD, (
        f"Precisão Conforme {precision:.4f} abaixo do threshold {PRECISION_C_THRESHOLD}"
    )


def test_f1_score():
    """Verifica se o F1-Score geral atende ao threshold mínimo.

    F1 equilibra precisão e recall. Um modelo com F1 alto é
    confiável tanto para aprovar quanto para reprovar elementos.
    """
    f1 = f1_score(y_test, y_pred, average="weighted")
    assert f1 >= F1_THRESHOLD, (
        f"F1-Score {f1:.4f} abaixo do threshold {F1_THRESHOLD}"
    )
