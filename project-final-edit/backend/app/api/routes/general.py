from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db.database import get_db
from app.db.models import Prediction
from app.services.weather_service import get_weather
from app.core.security import get_current_user
from app.db.models import User
router = APIRouter(tags=["Platform"])
@router.get("/api/v1/history")
def history(limit: int = 50, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.query(Prediction).filter(Prediction.user_id == user.id).order_by(desc(Prediction.created_at)).limit(min(max(limit,1),200)).all()
    return [{"id": r.id, "module": r.module, "input": r.input_json, "result": r.result_json,
             "created_at": r.created_at.isoformat() if r.created_at else None} for r in rows]
@router.get("/api/v1/weather")
async def weather(latitude: float, longitude: float):
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise HTTPException(422, "Invalid latitude or longitude.")
    try:
        return await get_weather(latitude, longitude)
    except Exception:
        raise HTTPException(502, "Weather provider is temporarily unavailable.")


@router.get("/api/v1/location/lookup")
async def location_lookup(name: str):
    """Resolve a village/town/district name to coordinates for weather lookup."""
    import httpx
    if len(name.strip()) < 2:
        raise HTTPException(422, "Enter at least two characters for the location.")
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.get("https://geocoding-api.open-meteo.com/v1/search",
                                       params={"name": name.strip(), "count": 5, "language": "en", "format": "json"})
            response.raise_for_status()
            results = response.json().get("results", [])
        return {"results": [{"name": r.get("name"), "admin1": r.get("admin1"),
                              "country": r.get("country"), "latitude": r.get("latitude"),
                              "longitude": r.get("longitude")} for r in results]}
    except Exception:
        raise HTTPException(502, "Could not find that location right now. Try entering a nearby town or district.")
