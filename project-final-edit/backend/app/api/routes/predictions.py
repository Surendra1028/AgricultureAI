from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session
from pathlib import Path
import json
from app.db.database import get_db
from app.db.models import Prediction
from app.schemas import CropInput, YieldInput, FarmerCropInput, FertilizerInput
from app.services.prediction_service import predict_crop, predict_yield, fertilizer_guidance, basic_farmer_recommendations
from app.core.config import DISEASE_MODEL_PATH, DISEASE_CLASSES_PATH
from app.services.crop_disease_service import predict_produce_disease
from app.core.security import get_current_user
from app.db.models import User
router = APIRouter(prefix="/api/v1", tags=["Predictions"])
def save(db, module, inputs, result, user_id):
    row = Prediction(user_id=user_id, module=module, input_json=inputs, result_json=result)
    db.add(row); db.commit(); db.refresh(row)
    return row.id

@router.post("/recommend/basic")
def basic_recommend(payload: FarmerCropInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump()
    result = basic_farmer_recommendations(data)
    result["history_id"] = save(db, "basic_crop_screening", data, result, user.id)
    return result

@router.post("/predict/crop")
def crop(payload: CropInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump()
    result = predict_crop(data); result["history_id"] = save(db, "crop_recommendation", data, result, user.id)
    return result
@router.post("/predict/yield")
def yield_estimate(payload: YieldInput, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    data = payload.model_dump()
    result = predict_yield(data); result["history_id"] = save(db, "yield_prediction", data, result, user.id)
    return result
@router.post("/predict/fertilizer")
def fertilizer(
    payload: FertilizerInput | None = None,
    crop: str | None = None,
    nitrogen: float | None = None,
    phosphorus: float | None = None,
    potassium: float | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    if payload is not None:
        c, n, p, k = payload.crop, payload.nitrogen, payload.phosphorus, payload.potassium
    elif crop is not None and nitrogen is not None and phosphorus is not None and potassium is not None:
        c, n, p, k = crop, nitrogen, phosphorus, potassium
    else:
        raise HTTPException(
            status_code=422,
            detail="Missing required fertilizer parameters (crop, nitrogen, phosphorus, potassium)."
        )
    data = {"crop": c, "nitrogen": n, "phosphorus": p, "potassium": k}
    result = fertilizer_guidance(c, n, p, k)
    result["history_id"] = save(db, "fertilizer_guidance", data, result, user.id)
    return result
@router.post("/predict/disease")
async def disease(file: UploadFile = File(...), db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(415, "Upload a JPEG, PNG or WebP image.")
    content = await file.read(8 * 1024 * 1024 + 1)
    if len(content) > 8 * 1024 * 1024:
        raise HTTPException(413, "Image must be 8 MB or smaller.")
    mp, cp = Path(DISEASE_MODEL_PATH), Path(DISEASE_CLASSES_PATH)
    if not mp.exists() or not cp.exists():
        raise HTTPException(503, "Disease model not trained. Follow docs/DATASETS.md and app/ml/train_disease.py.")
    try:
        import io
        from PIL import Image, UnidentifiedImageError

        try:
            with Image.open(io.BytesIO(content)) as check_image:
                check_image.verify()
            image = Image.open(io.BytesIO(content)).convert("RGB")
        except (UnidentifiedImageError, OSError, ValueError):
            raise HTTPException(400, "The uploaded file is not a valid supported image.")

        try:
            result = predict_produce_disease(image)
        except ValueError as e:
            raise HTTPException(400, str(e))

        result["history_id"] = save(db, "crop_disease", {"filename": file.filename}, result, user.id)
        return result
    except HTTPException:
        raise
    except ImportError:
        raise HTTPException(503, "TensorFlow is not installed in this environment. Install the optional disease-model dependencies.")
    except Exception as exc:
        raise HTTPException(500, f"Image processing failed: {exc}")
