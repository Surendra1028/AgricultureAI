"""Comprehensive agronomic fertilizer advisory engine.
Calculates crop-specific NPK requirements, deficit analysis, recommended commercial fertilizer quantities,
split-dose application schedules, and organic nutrient management in English, Telugu, and Hindi.
"""

CROP_NPK_BENCHMARKS = {
    "Rice": {"N": 100, "P": 50, "K": 50, "name": "Rice (Paddy)"},
    "Paddy": {"N": 100, "P": 50, "K": 50, "name": "Rice (Paddy)"},
    "Wheat": {"N": 120, "P": 60, "K": 40, "name": "Wheat"},
    "Maize": {"N": 120, "P": 60, "K": 50, "name": "Maize (Corn)"},
    "Cotton": {"N": 100, "P": 50, "K": 50, "name": "Cotton"},
    "Sugarcane": {"N": 250, "P": 100, "K": 120, "name": "Sugarcane"},
    "Groundnut": {"N": 25, "P": 50, "K": 75, "name": "Groundnut (Peanut)"},
    "Chickpea": {"N": 20, "P": 50, "K": 20, "name": "Bengal gram (Chickpea)"},
    "Pigeonpea": {"N": 25, "P": 50, "K": 25, "name": "Red gram (Pigeon pea)"},
    "Tomato": {"N": 120, "P": 80, "K": 100, "name": "Tomato"},
    "Potato": {"N": 150, "P": 100, "K": 120, "name": "Potato"},
    "Vegetables": {"N": 100, "P": 60, "K": 60, "name": "Vegetables"},
    "Millets": {"N": 50, "P": 30, "K": 20, "name": "Millets"},
}


def get_crop_benchmark(crop_name: str) -> dict:
    crop_clean = crop_name.strip().title()
    for key, val in CROP_NPK_BENCHMARKS.items():
        if key.lower() in crop_clean.lower() or crop_clean.lower() in key.lower():
            return val
    # Default benchmark for general field crops
    return {"N": 80, "P": 40, "K": 40, "name": crop_name}


def generate_fertilizer_guidance(crop: str, n_val: float, p_val: float, k_val: float) -> dict:
    target = get_crop_benchmark(crop)
    t_n, t_p, t_k = target["N"], target["P"], target["K"]

    def_n = max(0.0, round(t_n - n_val, 1))
    def_p = max(0.0, round(t_p - p_val, 1))
    def_k = max(0.0, round(t_k - k_val, 1))

    # Calculate commercial fertilizer equivalents:
    # Urea is 46% Nitrogen
    urea_kg = round(def_n / 0.46, 1) if def_n > 0 else 0.0
    # DAP is 46% P2O5 and 18% N
    dap_kg = round(def_p / 0.46, 1) if def_p > 0 else 0.0
    # Single Super Phosphate (SSP) is 16% P2O5
    ssp_kg = round(def_p / 0.16, 1) if def_p > 0 else 0.0
    # MOP (Muriate of Potash) is 60% K2O
    mop_kg = round(def_k / 0.60, 1) if def_k > 0 else 0.0

    urea_bags_45kg = round(urea_kg / 45, 1) if urea_kg > 0 else 0.0
    dap_bags_50kg = round(dap_kg / 50, 1) if dap_kg > 0 else 0.0
    mop_bags_50kg = round(mop_kg / 50, 1) if mop_kg > 0 else 0.0

    values = {"N": n_val, "P": p_val, "K": k_val}
    lowest_nut = min(values, key=values.get)

    return {
        "crop": target["name"],
        "entered_npk": {"N": n_val, "P": p_val, "K": k_val},
        "target_npk": {"N": t_n, "P": t_p, "K": t_k},
        "deficits": {"N": def_n, "P": def_p, "K": def_k},
        "lowest_reported_nutrient": lowest_nut,
        "mode": "transparent_rule_based_guidance",
        "advisory": {
            "en": {
                "title": f"Nutrient & Fertilizer Plan for {target['name']}",
                "status_summary": f"Your entered soil Phosphorus (P={p_val}) and Nitrogen (N={n_val}) show {lowest_nut} as the most deficient nutrient relative to the target requirements of {target['name']}.",
                "fertilizers_needed": [
                    {"name": "Urea (46% N)", "amount": f"{urea_kg} kg/ha ({urea_bags_45kg} bags of 45 kg)", "note": "Primary nitrogen source for vegetative growth."},
                    {"name": "DAP (18-46-0) OR SSP (16% P)", "amount": f"{dap_kg} kg/ha DAP ({dap_bags_50kg} bags) OR {ssp_kg} kg/ha SSP", "note": "Primary phosphorus source for strong root establishment."},
                    {"name": "MOP - Potash (60% K2O)", "amount": f"{mop_kg} kg/ha ({mop_bags_50kg} bags of 50 kg)", "note": "Primary potassium source for pest resistance and grain filling."}
                ],
                "application_schedule": [
                    {"stage": "Basal Dose (At Sowing/Transplanting)", "action": "Apply 100% of required Phosphorus (DAP or SSP), 50% of Potash (MOP), and 25% of Nitrogen (Urea) into the soil before final harrowing."},
                    {"stage": "First Top Dressing (20–25 Days / Tillering)", "action": "Broadcast 50% of the remaining Nitrogen (Urea) when soil is moist to accelerate vegetative tillering."},
                    {"stage": "Second Top Dressing (40–45 Days / Panicle Initiation)", "action": "Apply the remaining 25% of Nitrogen (Urea) together with the remaining 50% of Potash (MOP) to boost grain formation."}
                ],
                "organic_and_micronutrient_tips": "Incorporate 5–10 tonnes of well-rotted Farmyard Manure (FYM) or 2 tonnes of Vermicompost during land preparation. If growing rice, apply 25 kg/ha of Zinc Sulphate (21%) to prevent Khaira (zinc deficiency) disease.",
                "safety_disclaimer": "These calculations are benchmark scientific estimates per hectare. Check with your local Agriculture Officer or Soil Testing Laboratory to adjust for local soil texture and irrigation before purchasing."
            },
            "te": {
                "title": f"{target['name']} పంటకు పోషకాలు మరియు ఎరువుల సమగ్ర ప్రణాళిక",
                "status_summary": f"మీరు నమోదు చేసిన నేల NPK విలువల్లో ({target['name']} పంట సిఫార్సులతో పోల్చితే) {lowest_nut} పోషకం అత్యల్పంగా ఉంది. ఈ లోపాన్ని సరిదిద్దడం ద్వారా పంట దిగుబడి పెరుగుతుంది.",
                "fertilizers_needed": [
                    {"name": "యూరియా (46% నత్రజని)", "amount": f"హెక్టారుకు {urea_kg} కిలోలు (సుమారు {urea_bags_45kg} బస్తాలు - 45 కేజీలు)", "note": "పైరు శాఖీయ ఎదుగుదలకు, పచ్చదనానికి ముఖ్యమైనది."},
                    {"name": "DAP లేదా SSP (భాస్వరం)", "amount": f"DAP {dap_kg} కిలోలు ({dap_bags_50kg} బస్తాలు) లేదా SSP {ssp_kg} కిలోలు", "note": "వేరు వ్యవస్థ బలంగా విస్తరించడానికి తోడ్పడుతుంది."},
                    {"name": "MOP - పొటాష్ (60% K2O)", "amount": f"హెక్టారుకు {mop_kg} కిలోలు (సుమారు {mop_bags_50kg} బస్తాలు - 50 కేజీలు)", "note": "గింజ గట్టిపడటానికి, తెగుళ్లను తట్టుకోవడానికి అవసరం."}
                ],
                "application_schedule": [
                    {"stage": "మొదటి దఫా / ఆఖరి దుక్కిలో (బేసల్ డోస్)", "action": "సిఫార్సు చేసిన మొత్తం భాస్వరం (DAP/SSP), 50% పొటాష్ (MOP) మరియు 25% యూరియాను ఆఖరి దుక్కిలో వేసి మట్టిలో కలపండి."},
                    {"stage": "రెండవ దఫా (20–25 రోజులకు / దుబ్బు చేసే దశ)", "action": "మొక్కలు పిలకలు వేసే సమయంలో 50% యూరియాను పొలంలో తగినంత తేమ ఉన్నప్పుడు చల్లండి."},
                    {"stage": "మూడవ దఫా (40–45 రోజులకు / చిరుపొట్ట దశ)", "action": "మిగిలిన 25% యూరియాతో పాటు మిగిలిన 50% పొటాష్ (MOP) ను వేస్తే గింజ బరువు, నాణ్యత పెరుగుతుంది."}
                ],
                "organic_and_micronutrient_tips": "ఆఖరి దుక్కిలో ఎకరానికి 4-5 ట్రాక్టర్ల పశువుల ఎరువు లేదా 1 టన్ను వర్మీకంపోస్ట్ వేయండి. వరి సాగులో జింక్ లోపం రాకుండా ఎకరానికి 10 కిలోల జింక్ సల్ఫేట్ తప్పనిసరిగా వేయండి.",
                "safety_disclaimer": "ఇవి హెక్టారుకు ప్రామాణిక వ్యవసాయ లెక్కలు మాత్రమే. కొనుగోలు చేసే ముందు స్థానిక వ్యవసాయ అధికారి లేదా రైతు భరోసా కేంద్రం (RBK/KVK) లో నిర్ధారించుకోండి."
            },
            "hi": {
                "title": f"{target['name']} की फसल के लिए उर्वरक एवं पोषण प्रबंधन",
                "status_summary": f"आपके द्वारा दर्ज किए गए मिट्टी के NPK मानों में {target['name']} की आवश्यकता के अनुसार {lowest_nut} सबसे कम पाया गया है।",
                "fertilizers_needed": [
                    {"name": "यूरिया (46% नाइट्रोजन)", "amount": f"{urea_kg} किग्रा/हेक्टेयर ({urea_bags_45kg} बैग - 45 किग्रा)", "note": "फसल के वानस्पतिक विकास और हरियाली के लिए आवश्यक।"},
                    {"name": "DAP या SSP (फास्फोरस)", "amount": f"DAP {dap_kg} किग्रा ({dap_bags_50kg} बैग) या SSP {ssp_kg} किग्रा", "note": "जड़ों के मजबूत विकास के लिए प्रारंभिक अवस्था में जरूरी।"},
                    {"name": "MOP - पोटाश (60% K2O)", "amount": f"{mop_kg} किग्रा/हेक्टेयर ({mop_bags_50kg} बैग - 50 किग्रा)", "note": "दाने के भराव और रोग प्रतिरोधक क्षमता बढ़ाने हेतु।" }
                ],
                "application_schedule": [
                    {"stage": "बुवाई/रोपाई के समय (बेसल खुराक)", "action": "फास्फोरस की पूरी मात्रा (DAP/SSP), पोटाश का 50% और यूरिया का 25% हिस्सा अंतिम जुताई में मिट्टी में मिलाएँ।"},
                    {"stage": "पहला टॉप ड्रेसिंग (20-25 दिन / कल्ले फूटने पर)", "action": "खेत में पर्याप्त नमी होने पर बची हुई यूरिया का 50% हिस्सा छिड़कें ताकि कल्ले तेजी से फूटें।"},
                    {"stage": "दूसरा टॉप ड्रेसिंग (40-45 दिन / बाली बनते समय)", "action": "बचा हुआ 25% यूरिया और बचा हुआ 50% पोटाश एक साथ डालें ताकि दाने चमकदार और वजनदार बनें।"}
                ],
                "organic_and_micronutrient_tips": "खेत की तैयारी के समय 2-3 ट्रॉली सड़ी गोबर खाद या केंचुआ खाद डालें। धान की फसल में खैरा रोग से बचाव हेतु 25 किग्रा जिंक सल्फेट प्रति हेक्टेयर अवश्य दें।",
                "safety_disclaimer": "यह गणना प्रति हेक्टेयर मानक वैज्ञानिक सिफारिशों पर आधारित है। उर्वरक खरीदने से पहले स्थानीय कृषि अधिकारी (KVK) से परामर्श अवश्य करें।"
            }
        }
    }
