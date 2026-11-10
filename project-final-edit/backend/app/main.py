from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import FRONTEND_ORIGINS
from app.db.database import Base, engine
from app.db import models
from app.api.routes import predictions, general, auth
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title="Smart Agriculture AI Platform", version="1.0.0",
              description="Educational AI-powered agricultural decision-support platform",
              lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=FRONTEND_ORIGINS, allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])
@app.get("/")
def home():
    return {"project": "Smart Agriculture AI Platform", "status": "running", "docs": "/docs"}
@app.get("/health")
def health():
    return {"status": "healthy"}
@app.get("/api/v1/modules")
def modules():
    return {"modules": [
        {"id":"disease","name":"Crop Disease Detection","method":"CNN / TensorFlow"},
        {"id":"crop","name":"Crop Recommendation","method":"Random Forest / XGBoost"},
        {"id":"fertilizer","name":"Fertilizer Guidance","method":"NPK observations + agronomic validation"},
        {"id":"yield","name":"Crop Yield Prediction","method":"Regression"},
        {"id":"weather","name":"Weather Insights","method":"Open-Meteo API"}]}
app.include_router(auth.router)
app.include_router(predictions.router)
app.include_router(general.router)
