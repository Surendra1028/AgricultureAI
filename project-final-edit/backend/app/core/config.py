import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BACKEND_DIR = Path(__file__).resolve().parents[2]


def _resolve_path(p: str) -> str:
    path = Path(p)
    return str(path if path.is_absolute() else (BACKEND_DIR / path))


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./smart_agriculture.db")
FRONTEND_ORIGINS = [
    x.strip()
    for x in os.getenv("FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
    if x.strip()
]
DISEASE_MODEL_PATH = _resolve_path(os.getenv("DISEASE_MODEL_PATH", "artifacts/disease_model.keras"))
DISEASE_CLASSES_PATH = _resolve_path(os.getenv("DISEASE_CLASSES_PATH", "artifacts/disease_classes.json"))
FRUIT_DISEASE_MODEL_PATH = _resolve_path(os.getenv("FRUIT_DISEASE_MODEL_PATH", "artifacts/fruit_disease_model.tflite"))
FRUIT_DISEASE_CLASSES_PATH = _resolve_path(os.getenv("FRUIT_DISEASE_CLASSES_PATH", "artifacts/fruit_disease_classes.json"))
CROP_MODEL_PATH = _resolve_path(os.getenv("CROP_MODEL_PATH", "artifacts/crop_recommendation.joblib"))
YIELD_MODEL_PATH = _resolve_path(os.getenv("YIELD_MODEL_PATH", "artifacts/yield_prediction.joblib"))

# Use a unique, randomly generated SECRET_KEY before deployment.
SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret-before-deployment")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
