from flask_openapi3 import OpenAPI, Info
from flask import jsonify
from flask_cors import CORS
import joblib
import numpy as np
from pydantic import BaseModel, Field

info = Info(title="StructConformity API", version="2.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

model = joblib.load("model/best_model.pkl")


class PredictRequest(BaseModel):
    element_type: int = Field(..., description="Tipo do elemento (0=beam, 1=column)")
    dim_a: float = Field(..., description="Largura da secao (cm)")
    dim_b: float = Field(..., description="Altura da secao (cm)")
    dim_c: float = Field(..., description="Comprimento (viga) ou altura em Z (pilar), em cm")
    fck: float = Field(..., description="Resistencia do concreto (MPa)")
    cover: float = Field(..., description="Cobrimento (cm)")
    main_rebar_diam: float = Field(..., description="Bitola longitudinal (mm)")
    main_rebar_quantity: int = Field(..., description="Quantidade de barras longitudinais")
    stirrup_diam: float = Field(..., description="Bitola do estribo (mm)")
    stirrup_spacing: float = Field(..., description="Espacamento dos estribos (cm)")


@app.get("/")
def home():
    return "StructConformity API rodando"


@app.post("/predict")
def predict(body: PredictRequest):
    features = np.array([[
        body.element_type,
        body.dim_a,
        body.dim_b,
        body.dim_c,
        body.fck,
        body.cover,
        body.main_rebar_diam,
        body.main_rebar_quantity,
        body.stirrup_diam,
        body.stirrup_spacing,
    ]])
    prediction = model.predict(features)
    result = "conforme" if prediction[0] == 1 else "nao_conforme"
    return jsonify({"prediction": result})


if __name__ == "__main__":
    app.run(debug=True)
