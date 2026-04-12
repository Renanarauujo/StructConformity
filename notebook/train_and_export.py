"""
Script de treino autonomo (espelha a pipeline do notebook).

Treina os 4 algoritmos com GridSearchCV, seleciona o melhor por acuracia
no teste e exporta como backend/model/best_model.pkl.
"""
from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


BASE = Path(__file__).resolve().parent.parent
DATASET = BASE / "dataset" / "structural_conformity.csv"
MODEL_OUT = BASE / "backend" / "model" / "best_model.pkl"

FEATURES = [
    "element_type_encoded", "dim_a", "dim_b", "dim_c", "fck", "cover",
    "main_rebar_diam", "main_rebar_quantity", "stirrup_diam", "stirrup_spacing",
]


def load_data():
    df = pd.read_csv(DATASET)
    le = LabelEncoder()
    df["element_type_encoded"] = le.fit_transform(df["element_type"])
    X = df[FEATURES]
    y = df["conformity"].map({"conforme": 1, "nao_conforme": 0})
    return train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)


def build_pipelines():
    return {
        "KNN": Pipeline([("scaler", StandardScaler()), ("classifier", KNeighborsClassifier())]),
        "Decision Tree": Pipeline([("scaler", StandardScaler()), ("classifier", DecisionTreeClassifier(random_state=42))]),
        "Naive Bayes": Pipeline([("scaler", StandardScaler()), ("classifier", GaussianNB())]),
        "SVM": Pipeline([("scaler", StandardScaler()), ("classifier", SVC(random_state=42))]),
    }


def build_param_grids():
    return {
        "KNN": {
            "classifier__n_neighbors": [3, 5, 7, 9, 11],
            "classifier__metric": ["euclidean", "manhattan"],
        },
        "Decision Tree": {
            "classifier__max_depth": [None, 5, 10, 15],
            "classifier__min_samples_split": [2, 5, 10],
        },
        "Naive Bayes": {
            "classifier__var_smoothing": [1e-9, 1e-8, 1e-7],
        },
        "SVM": {
            "classifier__C": [0.1, 1, 10],
            "classifier__kernel": ["rbf", "linear"],
        },
    }


def main():
    X_train, X_test, y_train, y_test = load_data()
    pipelines = build_pipelines()
    grids = build_param_grids()

    best = {}
    for name, pipe in pipelines.items():
        print(f"Otimizando {name}...")
        gs = GridSearchCV(pipe, grids[name], cv=5, scoring="accuracy", n_jobs=-1)
        gs.fit(X_train, y_train)
        best[name] = gs.best_estimator_
        print(f"  best CV score: {gs.best_score_:.4f}")

    print("\nResultados no teste:")
    scores = {}
    for name, model in best.items():
        pred = model.predict(X_test)
        acc = accuracy_score(y_test, pred)
        prec = precision_score(y_test, pred)
        rec = recall_score(y_test, pred, pos_label=0)
        f1 = f1_score(y_test, pred, average="weighted")
        scores[name] = acc
        print(f"  {name:14s} acc={acc:.4f}  prec_C={prec:.4f}  rec_NC={rec:.4f}  f1w={f1:.4f}")

    winner = max(scores, key=scores.get)
    print(f"\nMelhor modelo: {winner} (acc={scores[winner]:.4f})")
    MODEL_OUT.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best[winner], MODEL_OUT)
    print(f"Modelo salvo em: {MODEL_OUT}")


if __name__ == "__main__":
    main()
