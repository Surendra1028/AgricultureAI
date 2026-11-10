"""Train a crop-yield regression model from a validated historical dataset.

Expected CSV: backend/data/crop_yield.csv
Columns: crop, area_hectares, rainfall_mm, average_temperature_c,
         fertilizer_kg_per_hectare, year, yield_tonnes_per_hectare
"""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "crop_yield.csv"
OUT = ROOT / "artifacts"
NUMERIC = ["area_hectares", "rainfall_mm", "average_temperature_c", "fertilizer_kg_per_hectare", "year"]
CATEGORICAL = ["crop"]
TARGET = "yield_tonnes_per_hectare"


def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Place a validated historical dataset at {DATA}. See docs/DATASETS.md.")
    df = pd.read_csv(DATA)
    required = NUMERIC + CATEGORICAL + [TARGET]
    missing = [column for column in required if column not in df.columns]
    if missing:
        raise ValueError(f"Missing dataset columns: {missing}")
    df = df[required].dropna(subset=[TARGET]).copy()
    if len(df) < 30:
        raise ValueError("At least 30 valid rows are required for this starter training workflow; more diverse regional data is strongly preferred.")
    if (df[TARGET] < 0).any() or (df["area_hectares"] <= 0).any():
        raise ValueError("Yield must be non-negative and area_hectares must be positive.")

    X = df[NUMERIC + CATEGORICAL]
    y = df[TARGET].astype(float)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocess = ColumnTransformer([
        ("numeric", SimpleImputer(strategy="median"), NUMERIC),
        ("crop", Pipeline([
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("onehot", OneHotEncoder(handle_unknown="ignore")),
        ]), CATEGORICAL),
    ])
    model = Pipeline([
        ("preprocess", preprocess),
        ("regressor", RandomForestRegressor(n_estimators=300, random_state=42, min_samples_leaf=2, n_jobs=-1)),
    ])
    model.fit(X_train, y_train)
    predicted = model.predict(X_test)
    metrics = {
        "mae_tonnes_per_hectare": float(mean_absolute_error(y_test, predicted)),
        "rmse_tonnes_per_hectare": float(mean_squared_error(y_test, predicted) ** 0.5),
        "r2": float(r2_score(y_test, predicted)),
        "test_rows": int(len(y_test)),
        "warning": "Random split metrics can be optimistic for time- or region-dependent data. Validate on later years and unseen regions before real use.",
    }
    OUT.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, OUT / "yield_prediction.joblib")
    (OUT / "yield_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(json.dumps({"saved": str(OUT / "yield_prediction.joblib"), **metrics}, indent=2))


if __name__ == "__main__":
    main()
