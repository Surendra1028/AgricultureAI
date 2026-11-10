from pathlib import Path
import joblib
import numpy as np
from app.core.config import CROP_MODEL_PATH, YIELD_MODEL_PATH
FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
def load_model(path):
    return joblib.load(path) if Path(path).exists() else None
def predict_crop(data):
    model = load_model(CROP_MODEL_PATH)
    if model is None:
        return {"prediction": None, "mode": "setup_required", "message": "Train the crop model using docs/DATASETS.md and app/ml/train_crop.py."}
    import pandas as pd
    row = pd.DataFrame([{k: data[k] for k in FEATURES}], columns=FEATURES)
    pred = str(model.predict(row)[0])
    confidence = round(float(np.max(model.predict_proba(row)[0])) * 100, 2) if hasattr(model, "predict_proba") else None
    return {"prediction": pred, "confidence_percent": confidence, "mode": "trained_model"}
CROP_YIELD_BENCHMARKS = {
    "Rice": 3.8,
    "Paddy": 3.8,
    "Wheat": 3.4,
    "Maize": 4.5,
    "Cotton": 2.0,
    "Sugarcane": 75.0,
    "Groundnut": 2.2,
    "Chickpea": 1.4,
    "Pigeonpea": 1.2,
    "Tomato": 28.0,
    "Potato": 24.0,
    "Millets": 1.8,
    "Vegetables": 18.0,
}

def predict_yield(data):
    model = load_model(YIELD_MODEL_PATH)
    if model is None:
        return {"prediction": None, "mode": "setup_required", "message": "A validated yield dataset/model has not been configured yet."}
    import pandas as pd
    row = pd.DataFrame([{
        "crop": data["crop"],
        "area_hectares": data["area_hectares"],
        "rainfall_mm": data["rainfall_mm"],
        "average_temperature_c": data["average_temperature_c"],
        "fertilizer_kg_per_hectare": data["fertilizer_kg_per_hectare"],
        "year": data["year"],
    }])
    per_ha = round(float(model.predict(row)[0]), 3)
    area = float(data["area_hectares"])
    total_tonnes = round(per_ha * area, 3)

    quintals_per_ha = round(per_ha * 10, 2)
    quintals_per_acre = round(quintals_per_ha / 2.471, 2)
    total_quintals = round(total_tonnes * 10, 2)
    total_bags_50kg = int(round((total_tonnes * 1000) / 50))
    acres = round(area * 2.471, 2)

    crop_name = str(data["crop"]).strip().title()
    benchmark_avg = 3.5
    for k, v in CROP_YIELD_BENCHMARKS.items():
        if k.lower() in crop_name.lower():
            benchmark_avg = v
            break

    ratio = per_ha / max(0.1, benchmark_avg)
    if ratio >= 1.1:
        perf_en = "High Potential (Above Regional Average)"
        perf_te = "అధిక దిగుబడి సామర్థ్యం (ప్రాంతీయ సగటు కంటే ఎక్కువ)"
        perf_hi = "उच्च उपज क्षमता (क्षेत्रीय औसत से अधिक)"
    elif ratio >= 0.85:
        perf_en = "Optimal / Expected Harvest"
        perf_te = "సాధారణ / ఆశించిన దిగుబడి"
        perf_hi = "सामान्य / अपेक्षित उपज"
    else:
        perf_en = "Moderate / Below Benchmark Potential"
        perf_te = "మితమైన దిగుబడి (సగటు కంటే తక్కువ)"
        perf_hi = "मध्यम / औसत से कम उत्पादन"

    return {
        "crop": data["crop"],
        "area_hectares": area,
        "area_acres": acres,
        "estimated_yield_tonnes_per_hectare": per_ha,
        "estimated_total_tonnes": total_tonnes,
        "quintals_per_hectare": quintals_per_ha,
        "quintals_per_acre": quintals_per_acre,
        "total_quintals": total_quintals,
        "total_bags_50kg": total_bags_50kg,
        "mode": "trained_model",
        "advisory": {
            "en": {
                "performance_rating": perf_en,
                "summary": f"Estimated harvest for {data['crop']} across {area} ha ({acres} acres) is {total_tonnes} tonnes (~{total_quintals} quintals or ~{total_bags_50kg} bags of 50 kg).",
                "production_factors": [
                    f"Rainfall: Seasonal rainfall of {data['rainfall_mm']} mm provides healthy soil moisture.",
                    f"Temperature: Average seasonal temperature of {data['average_temperature_c']}°C supports crop development.",
                    f"Fertilizer: Applied {data['fertilizer_kg_per_hectare']} kg/ha. Apply in split doses to prevent nutrient runoff."
                ],
                "harvest_advice": "Ensure adequate irrigation during grain/pod filling and harvest when grain moisture is around 14% to maximize market returns."
            },
            "te": {
                "performance_rating": perf_te,
                "summary": f"{data['crop']} పంటకు {area} హెక్టార్లు ({acres} ఎకరాలు) విస్తీర్ణంలో మొత్తం సుమారు {total_tonnes} టన్నులు ({total_quintals} క్వింటాళ్లు లేదా సుమారు {total_bags_50kg} బస్తాలు - 50 కేజీలు) దిగుబడి వచ్చే అవకాశం ఉంది.",
                "production_factors": [
                    f"వర్షపాతం: {data['rainfall_mm']} మి.మీ. వర్షపాతం పంట ఎదుగుదలకు అనుకూలమైన తేమను అందిస్తుంది.",
                    f"ఉష్ణోగ్రత: సగటు ఉష్ణోగ్రత {data['average_temperature_c']}°C పంట దశలకు సరిపోతుంది.",
                    f"ఎరువుల వినియోగం: హెక్టారుకు {data['fertilizer_kg_per_hectare']} కిలోల ఎరువులు ఉపయోగించారు. సమతుల్య NPK ఎరువులను దశలవారీగా వేయండి."
                ],
                "harvest_advice": "పూత మరియు గింజ పాలుపోసుకునే దశలలో పొలంలో తేమ ఆరిపోకుండా చూసుకోండి. కోత తర్వాత తేమ 14% ఉండేలా ఆరబెట్టి విక్రయించండి."
            },
            "hi": {
                "performance_rating": perf_hi,
                "summary": f"{data['crop']} की फसल में {area} हेक्टेयर ({acres} एकड़) क्षेत्र से कुल अनुमानित उत्पादन {total_tonnes} टन (~{total_quintals} क्विंटल अथवा लगभग {total_bags_50kg} बैग - 50 किग्रा) होने का अनुमान है।",
                "production_factors": [
                    f"वर्षा: {data['rainfall_mm']} मिमी वर्षा फसल की वृद्धि के लिए अनुकूल नमी प्रदान करती है।",
                    f"तापमान: औसत तापमान {data['average_temperature_c']}°C फसल के विकास के लिए उपयुक्त है।",
                    f"उर्वरक: प्रति हेक्टेयर {data['fertilizer_kg_per_hectare']} किग्रा उर्वरक प्रयुक्त हुआ। संतुलित खुराक देने से उपज स्थिर रहती है।"
                ],
                "harvest_advice": "फूल आने और दाना बनते समय खेत में पर्याप्त नमी बनाए रखें। कटाई के बाद अनाज को 14% नमी तक सुखाकर मंडी में बेचें।"
            }
        }
    }
from app.services.fertilizer_service import generate_fertilizer_guidance

def fertilizer_guidance(crop, nitrogen, phosphorus, potassium):
    result = generate_fertilizer_guidance(crop, nitrogen, phosphorus, potassium)
    lowest = result["lowest_reported_nutrient"]
    result["observation"] = f"{lowest} is the lowest of the three entered NPK values relative to crop requirements."
    result["guidance"] = result["advisory"]["en"]["safety_disclaimer"]
    return result


def basic_farmer_recommendations(data):
    """Transparent starter rules for a low-friction farmer flow; not a trained ML model."""
    season = data["season"]
    irrigation = data["irrigation"]
    soil = data["soil_type"]

    # Broad candidate groups only. Final crop choice must be checked against local
    # agriculture department advisories, water availability, seed availability and soil.
    seasonal = {
        "Kharif": [
            {"crop": "Paddy (Rice)", "water": "High", "note": "Consider only where assured water and suitable local conditions are available."},
            {"crop": "Groundnut", "water": "Medium", "note": "A possible rain-fed or irrigated option in suitable regions."},
            {"crop": "Pigeon pea (Red gram)", "water": "Low to medium", "note": "A pulse option to discuss with the local agriculture officer."},
            {"crop": "Millets", "water": "Low", "note": "Often considered in lower-water farming systems; choose locally suitable variety."},
        ],
        "Rabi": [
            {"crop": "Bengal gram (Chickpea)", "water": "Low to medium", "note": "A possible post-monsoon pulse where local conditions suit."},
            {"crop": "Groundnut", "water": "Medium", "note": "Consider where soil, temperature and irrigation are suitable."},
            {"crop": "Maize", "water": "Medium", "note": "Needs suitable temperature and reliable water at key growth stages."},
            {"crop": "Safflower", "water": "Low", "note": "A possible dryland option in suitable regions."},
        ],
        "Summer": [
            {"crop": "Green gram (Moong)", "water": "Low to medium", "note": "Short-duration pulse option; check local sowing window."},
            {"crop": "Vegetables", "water": "Medium to high", "note": "Choose crop and variety based on market access and assured irrigation."},
            {"crop": "Fodder crops", "water": "Varies", "note": "Can be considered where livestock feed is a priority."},
        ],
    }
    candidates = seasonal[season]
    if irrigation == "Rain-fed":
        candidates = [c for c in candidates if c["water"] in ("Low", "Low to medium", "Medium")]
        candidates = sorted(candidates, key=lambda c: ("Low" not in c["water"], c["crop"]))
    elif irrigation in ("Borewell", "Canal", "Other"):
        # Retain choices but do not assume water is unlimited.
        candidates = candidates

    soil_note = "Soil type was not supplied; these are broad candidates, not a soil-matched recommendation."
    if soil != "Don't know":
        soil_note = f"Soil type entered: {soil}. A soil test is still needed for nutrient-specific advice."

    return {
        "mode": "basic_rule_based_screening",
        "recommendations": candidates[:3],
        "farmer_inputs": {"location": data["location"], "land_acres": data["land_acres"],
                          "season": season, "irrigation": irrigation, "soil_type": soil,
                          "previous_crop": data.get("previous_crop")},
        "soil_note": soil_note,
        "next_step": "Confirm crop, variety and sowing date with your local agriculture department/KVK using current district advisories before purchasing seed.",
        "limitations": "This basic mode does not use NPK/pH and is not a trained ML prediction. It provides broad options only; local climate, soil test, water quantity, pest pressure and market conditions can change suitability."
    }
