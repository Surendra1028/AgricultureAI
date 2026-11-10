"""Generate realistic agronomic baseline datasets and train crop & yield models."""
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error, r2_score
import joblib
import json

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
ARTIFACTS_DIR = ROOT / "artifacts"

DATA_DIR.mkdir(parents=True, exist_ok=True)
ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)


def build_crop_yield_model():
    print("--- Building Crop Yield Dataset & Model ---")
    np.random.seed(42)

    crops_profiles = {
        "Rice": {"base_yield": 3.6, "temp_opt": 25, "rain_opt": 1100, "fert_opt": 120, "yield_var": 0.4},
        "Wheat": {"base_yield": 3.4, "temp_opt": 20, "rain_opt": 600, "fert_opt": 110, "yield_var": 0.35},
        "Maize": {"base_yield": 3.8, "temp_opt": 24, "rain_opt": 750, "fert_opt": 100, "yield_var": 0.4},
        "Cotton": {"base_yield": 1.9, "temp_opt": 28, "rain_opt": 700, "fert_opt": 90, "yield_var": 0.25},
        "Sugarcane": {"base_yield": 72.0, "temp_opt": 30, "rain_opt": 1500, "fert_opt": 220, "yield_var": 6.0},
        "Groundnut": {"base_yield": 1.8, "temp_opt": 26, "rain_opt": 600, "fert_opt": 60, "yield_var": 0.2},
        "Chickpea": {"base_yield": 1.2, "temp_opt": 19, "rain_opt": 400, "fert_opt": 40, "yield_var": 0.15},
        "Pigeonpea": {"base_yield": 1.0, "temp_opt": 28, "rain_opt": 800, "fert_opt": 45, "yield_var": 0.15},
        "Mustard": {"base_yield": 1.4, "temp_opt": 18, "rain_opt": 350, "fert_opt": 55, "yield_var": 0.2},
        "Soybean": {"base_yield": 1.7, "temp_opt": 27, "rain_opt": 850, "fert_opt": 70, "yield_var": 0.2},
        "Millets": {"base_yield": 1.3, "temp_opt": 29, "rain_opt": 450, "fert_opt": 40, "yield_var": 0.15},
    }

    rows = []
    years = list(range(2010, 2026))

    for crop, prof in crops_profiles.items():
        for year in years:
            for rep in range(10):  # 16 years * 10 = 160 rows per crop
                area = round(float(np.random.uniform(0.5, 10.0)), 2)
                # Introduce realistic variation
                temp = round(float(np.random.normal(prof["temp_opt"], 3.0)), 1)
                rainfall = round(float(np.random.normal(prof["rain_opt"], prof["rain_opt"] * 0.2)), 1)
                rainfall = max(rainfall, 100.0)
                fert = round(float(np.random.normal(prof["fert_opt"], prof["fert_opt"] * 0.25)), 1)
                fert = max(fert, 10.0)

                # Productivity factors
                temp_factor = 1.0 - 0.015 * abs(temp - prof["temp_opt"])
                rain_factor = 1.0 - 0.0003 * abs(rainfall - prof["rain_opt"])
                fert_factor = 1.0 + 0.001 * min(fert - prof["fert_opt"], 40.0)
                tech_trend = 1.0 + 0.008 * (year - 2010)

                yield_val = prof["base_yield"] * temp_factor * rain_factor * fert_factor * tech_trend
                yield_val += np.random.normal(0, prof["yield_var"])
                yield_val = round(max(yield_val, 0.2), 3)

                rows.append({
                    "crop": crop,
                    "area_hectares": area,
                    "rainfall_mm": rainfall,
                    "average_temperature_c": temp,
                    "fertilizer_kg_per_hectare": fert,
                    "year": year,
                    "yield_tonnes_per_hectare": yield_val
                })

    df_yield = pd.DataFrame(rows)
    yield_csv_path = DATA_DIR / "crop_yield.csv"
    df_yield.to_csv(yield_csv_path, index=False)
    print(f"Saved {len(df_yield)} rows to {yield_csv_path}")

    # Train model
    NUMERIC = ["area_hectares", "rainfall_mm", "average_temperature_c", "fertilizer_kg_per_hectare", "year"]
    CATEGORICAL = ["crop"]
    TARGET = "yield_tonnes_per_hectare"

    X = df_yield[NUMERIC + CATEGORICAL]
    y = df_yield[TARGET].astype(float)
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
        ("regressor", RandomForestRegressor(n_estimators=150, random_state=42, min_samples_leaf=2, n_jobs=-1)),
    ])
    model.fit(X_train, y_train)

    pred = model.predict(X_test)
    mae = mean_absolute_error(y_test, pred)
    r2 = r2_score(y_test, pred)

    yield_model_path = ARTIFACTS_DIR / "yield_prediction.joblib"
    joblib.dump(model, yield_model_path)
    metrics = {"mae_tonnes_per_hectare": round(float(mae), 3), "r2": round(float(r2), 3), "rows": len(df_yield)}
    (ARTIFACTS_DIR / "yield_metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"Trained Yield Model! MAE: {mae:.3f}, R2: {r2:.3f}. Saved to {yield_model_path}")


def build_crop_recommendation_model():
    print("\n--- Building Crop Recommendation Dataset & Model ---")
    np.random.seed(42)

    crop_specs = {
        "rice": {"N": (80, 10), "P": (45, 8), "K": (40, 5), "temp": (24, 2), "humidity": (82, 3), "ph": (6.4, 0.4), "rain": (230, 25)},
        "maize": {"N": (80, 10), "P": (48, 7), "K": (20, 4), "temp": (22, 3), "humidity": (65, 5), "ph": (6.3, 0.4), "rain": (85, 12)},
        "chickpea": {"N": (40, 8), "P": (68, 7), "K": (80, 5), "temp": (19, 2), "humidity": (17, 3), "ph": (7.3, 0.5), "rain": (80, 10)},
        "kidneybeans": {"N": (20, 5), "P": (67, 6), "K": (20, 3), "temp": (20, 3), "humidity": (22, 4), "ph": (5.7, 0.3), "rain": (105, 20)},
        "pigeonpeas": {"N": (20, 5), "P": (68, 6), "K": (20, 3), "temp": (28, 4), "humidity": (48, 8), "ph": (5.8, 0.8), "rain": (145, 30)},
        "mothbeans": {"N": (22, 5), "P": (48, 6), "K": (20, 3), "temp": (28, 3), "humidity": (53, 7), "ph": (6.8, 1.0), "rain": (51, 10)},
        "mungbean": {"N": (21, 5), "P": (48, 6), "K": (20, 3), "temp": (28, 2), "humidity": (85, 4), "ph": (6.7, 0.3), "rain": (48, 8)},
        "blackgram": {"N": (40, 6), "P": (67, 6), "K": (19, 3), "temp": (30, 3), "humidity": (65, 4), "ph": (7.1, 0.3), "rain": (68, 6)},
        "lentil": {"N": (19, 5), "P": (68, 6), "K": (19, 3), "temp": (25, 3), "humidity": (65, 4), "ph": (6.9, 0.4), "rain": (46, 6)},
        "pomegranate": {"N": (19, 5), "P": (19, 4), "K": (40, 4), "temp": (22, 2), "humidity": (90, 3), "ph": (6.4, 0.4), "rain": (108, 6)},
        "banana": {"N": (100, 10), "P": (82, 7), "K": (50, 4), "temp": (27, 2), "humidity": (80, 3), "ph": (6.0, 0.3), "rain": (105, 10)},
        "mango": {"N": (20, 5), "P": (27, 5), "K": (30, 4), "temp": (31, 3), "humidity": (50, 4), "ph": (5.8, 0.6), "rain": (95, 8)},
        "grapes": {"N": (23, 5), "P": (132, 8), "K": (200, 5), "temp": (24, 8), "humidity": (82, 3), "ph": (6.0, 0.3), "rain": (70, 5)},
        "watermelon": {"N": (99, 10), "P": (17, 4), "K": (50, 4), "temp": (26, 2), "humidity": (85, 3), "ph": (6.5, 0.3), "rain": (51, 6)},
        "muskmelon": {"N": (100, 10), "P": (18, 4), "K": (50, 4), "temp": (29, 2), "humidity": (92, 2), "ph": (6.4, 0.2), "rain": (25, 3)},
        "apple": {"N": (21, 5), "P": (134, 8), "K": (200, 5), "temp": (23, 2), "humidity": (92, 2), "ph": (5.9, 0.3), "rain": (113, 8)},
        "orange": {"N": (20, 5), "P": (17, 4), "K": (10, 3), "temp": (23, 8), "humidity": (92, 2), "ph": (7.0, 0.5), "rain": (110, 8)},
        "papaya": {"N": (50, 8), "P": (59, 6), "K": (50, 4), "temp": (34, 3), "humidity": (92, 2), "ph": (6.7, 0.2), "rain": (143, 25)},
        "coconut": {"N": (22, 5), "P": (17, 4), "K": (30, 4), "temp": (27, 2), "humidity": (95, 2), "ph": (6.0, 0.3), "rain": (176, 25)},
        "cotton": {"N": (118, 12), "P": (46, 6), "K": (20, 3), "temp": (24, 2), "humidity": (80, 3), "ph": (6.9, 0.5), "rain": (80, 12)},
        "jute": {"N": (78, 10), "P": (47, 6), "K": (40, 4), "temp": (25, 2), "humidity": (80, 4), "ph": (6.7, 0.3), "rain": (175, 20)},
        "coffee": {"N": (101, 10), "P": (29, 5), "K": (30, 4), "temp": (26, 2), "humidity": (59, 6), "ph": (6.8, 0.4), "rain": (158, 20)},
    }

    FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
    rows = []

    for crop, prof in crop_specs.items():
        for _ in range(100):  # 22 crops * 100 = 2,200 rows (exact Kaggle dataset size)
            N = round(float(np.clip(np.random.normal(prof["N"][0], prof["N"][1]), 0, 140)), 1)
            P = round(float(np.clip(np.random.normal(prof["P"][0], prof["P"][1]), 5, 145)), 1)
            K = round(float(np.clip(np.random.normal(prof["K"][0], prof["K"][1]), 5, 205)), 1)
            temp = round(float(np.clip(np.random.normal(prof["temp"][0], prof["temp"][1]), 8, 45)), 2)
            hum = round(float(np.clip(np.random.normal(prof["humidity"][0], prof["humidity"][1]), 14, 99)), 2)
            ph = round(float(np.clip(np.random.normal(prof["ph"][0], prof["ph"][1]), 3.5, 9.5)), 2)
            rain = round(float(np.clip(np.random.normal(prof["rain"][0], prof["rain"][1]), 20, 300)), 2)

            rows.append({
                "N": N, "P": P, "K": K,
                "temperature": temp, "humidity": hum,
                "ph": ph, "rainfall": rain,
                "label": crop
            })

    df_crop = pd.DataFrame(rows)
    crop_csv_path = DATA_DIR / "crop_recommendation.csv"
    df_crop.to_csv(crop_csv_path, index=False)
    print(f"Saved {len(df_crop)} rows to {crop_csv_path}")

    # Train Random Forest Classifier
    X, y = df_crop[FEATURES], df_crop["label"].astype(str)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("classifier", RandomForestClassifier(n_estimators=150, random_state=42, class_weight="balanced", n_jobs=-1))
    ])
    clf.fit(Xtr, ytr)
    pred = clf.predict(Xte)
    acc = accuracy_score(yte, pred)

    crop_model_path = ARTIFACTS_DIR / "crop_recommendation.joblib"
    joblib.dump(clf, crop_model_path)
    (ARTIFACTS_DIR / "crop_metrics.json").write_text(json.dumps({"accuracy": round(float(acc), 4)}, indent=2))
    print(f"Trained Crop Recommendation Model! Accuracy: {acc*100:.2f}%. Saved to {crop_model_path}")


if __name__ == "__main__":
    build_crop_yield_model()
    build_crop_recommendation_model()
