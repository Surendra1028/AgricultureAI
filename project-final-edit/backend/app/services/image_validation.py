"""Validation and organ classification service for crop leaves, fruits, and vegetables.

Screens uploaded images to identify agricultural produce (leaves, fruits, vegetables)
and reliably reject irrelevant inputs like human photos (faces/portraits), vehicles,
and household objects.
"""
from typing import Tuple, Optional, Dict, Any
import numpy as np
from PIL import Image

_imagenet_model = None

# Keywords in ImageNet-1k labels that identify human clothing, personal attire, or human presence
HUMAN_KEYWORDS = {
    "jersey", "suit", "pajama", "kimono", "sweatshirt", "lab_coat", "wig",
    "sunglasses", "sunglass", "mask", "seat_belt", "neck_brace", "stethoscope",
    "jean", "cardigan", "trench_coat", "groom", "gown", "cloak", "vestment",
    "brassiere", "bikini", "apron", "swimming_trunks", "sock", "shoe", "mitten",
    "scuba_diver", "ski_mask", "sombrero", "cowboy_hat", "football_helmet",
    "poncho", "stole", "necktie", "bow_tie", "sarong", "military_uniform",
    "mortarboard", "academic_gown", "bulletproof_vest", "breastplate"
}

# Keywords in ImageNet-1k labels that identify common non-plant objects
NON_PLANT_KEYWORDS = {
    "car", "sports_car", "racer", "convertible", "minivan", "truck", "bus", "jeep",
    "pickup", "limousine", "trailer_truck", "fire_engine", "ambulance", "cab",
    "laptop", "computer", "keyboard", "mouse", "cellular_telephone", "dial_telephone",
    "desk", "dining_table", "chair", "couch", "bed", "wardrobe", "bookcase",
    "refrigerator", "microwave", "toaster", "washing_machine", "monitor", "screen",
    "television", "traffic_light", "street_sign", "parking_meter", "wall_clock"
}

# Specific ImageNet produce class labels (avoid generic substrings like 'apple' matching 'custard_apple')
FRUIT_EXACT_LABELS = {
    "banana", "orange", "lemon", "strawberry", "pineapple", "pomegranate",
    "fig", "grape", "mango", "guava", "peach"
}

VEGETABLE_EXACT_LABELS = {
    "bell_pepper", "cucumber", "zucchini", "spaghetti_squash", "acorn_squash",
    "butternut_squash", "head_cabbage", "broccoli", "cauliflower", "artichoke",
    "cardoon", "mushroom", "corn", "potato", "mashed_potato"
}


def _get_imagenet_model():
    global _imagenet_model
    if _imagenet_model is None:
        import tensorflow as tf
        _imagenet_model = tf.keras.applications.MobileNetV2(weights="imagenet")
    return _imagenet_model


def validate_produce_image(image: Image.Image) -> Dict[str, Any]:
    """Validate whether an image is a crop leaf, fruit, or vegetable vs an irrelevant image.

    Returns dict with:
        is_valid: bool
        organ: 'leaf' | 'fruit' | 'vegetable' | 'unknown'
        category: 'plant' | 'human' | 'non_plant'
        detected_produce: Optional[str]
        error_message: Optional[str]
    """
    arr = np.array(image.convert("RGB"), dtype=np.float32)
    R, G, B = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

    # 1. Human skin chromaticity detection (standard daylight skin cluster)
    # 1. Agricultural & Botanical Chromaticity in HSV
    hsv = np.array(image.convert("HSV"))
    h, s, v = hsv[:, :, 0], hsv[:, :, 1], hsv[:, :, 2]

    # Daylight skin tone threshold with natural skin saturation bounds (skin is not neon orange/yellow)
    skin_mask = (
        (R > 95) & (G > 40) & (B > 20) &
        ((np.maximum(np.maximum(R, G), B) - np.minimum(np.minimum(R, G), B)) > 15) &
        (np.abs(R - G) > 15) & (R > G) & (R > B) &
        (s >= 25) & (s <= 125)
    )
    skin_pct = float(np.mean(skin_mask) * 100)

    # Leaf / Foliage: 50..120 (pure green to deep foliage)
    leaf_mask = (h >= 50) & (h <= 120) & (s >= 25) & (v >= 25)
    leaf_pct = float(np.mean(leaf_mask) * 100)

    # Fruit / Vegetable hues (vibrantly saturated agricultural produce):
    # Red produce (tomato, apple, strawberry, red pepper): H <= 11 or H >= 242, S >= 100
    red_mask = ((h <= 11) | (h >= 242)) & (s >= 100) & (v >= 30)
    # Orange produce (orange, carrot, orange pepper, ripe mango): 12 <= H <= 30, S >= 120
    orange_mask = (h >= 12) & (h <= 30) & (s >= 120) & (v >= 35)
    # Yellow produce (banana, lemon, yellow pepper, squash, corn): 31 <= H <= 49, S >= 100
    yellow_mask = (h >= 31) & (h <= 49) & (s >= 100) & (v >= 35)
    # Purple produce (grape, eggplant): 180 <= H <= 235, S >= 35
    purple_mask = (h >= 180) & (h <= 235) & (s >= 35) & (v >= 20)

    red_pct = float(np.mean(red_mask) * 100)
    orange_pct = float(np.mean(orange_mask) * 100)
    yellow_pct = float(np.mean(yellow_mask) * 100)
    produce_color_pct = float(np.mean(leaf_mask | red_mask | orange_mask | yellow_mask | purple_mask) * 100)

    # 3. Pretrained general vision model semantic check
    top_labels = []
    top1_label = ""
    top1_prob = 0.0
    is_produce_label = False
    is_human_label = False
    is_non_plant_label = False
    detected_produce = None

    try:
        import tensorflow as tf
        inet = _get_imagenet_model()
        resized = image.convert("RGB").resize((224, 224))
        inp = tf.keras.applications.mobilenet_v2.preprocess_input(
            np.expand_dims(np.array(resized, dtype=np.float32), 0)
        )
        preds = inet.predict(inp, verbose=0)
        decoded = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=5)[0]
        top1_label = decoded[0][1].lower()
        top1_prob = float(decoded[0][2])
        top_labels = [d[1].lower() for d in decoded if d[2] >= 0.08]
        if not top_labels:
            top_labels = [top1_label]

        for lbl in top_labels:
            words = set(lbl.split("_"))
            if any(k in words for k in FRUIT_EXACT_LABELS | VEGETABLE_EXACT_LABELS):
                is_produce_label = True
                break

        for lbl in top_labels:
            if any(h_kw in lbl for h_kw in HUMAN_KEYWORDS):
                is_human_label = True
                break

        for lbl in top_labels:
            if any(np_kw in lbl for np_kw in NON_PLANT_KEYWORDS):
                is_non_plant_label = True
                break
    except Exception:
        pass

    # Rejection 1: Obvious human photos (faces, portraits, clothing)
    if (skin_pct > 8.0 and produce_color_pct < 28.0) or (is_human_label and leaf_pct < 35.0 and not is_produce_label):
        return {
            "is_valid": False,
            "organ": "unknown",
            "category": "human",
            "detected_produce": None,
            "error_message": (
                "Irrelevant image detected: The uploaded image appears to be a human photo or portrait. "
                "Disease detection is designed exclusively for crop leaves, vegetables, and fruits. "
                "Please upload a clear photo of an affected plant leaf, vegetable, or fruit."
            ),
        }

    # Rejection 2: Non-agricultural scenes or inanimate objects
    if (produce_color_pct < 5.0 and not is_produce_label) or (is_non_plant_label and produce_color_pct < 25.0 and not is_produce_label):
        clean_name = top1_label.replace("_", " ") if top1_label else "object"
        return {
            "is_valid": False,
            "organ": "unknown",
            "category": "non_plant",
            "detected_produce": None,
            "error_message": (
                f"Irrelevant image detected: The uploaded image appears to be an object ({clean_name}). "
                "Disease detection is designed exclusively for crop leaves, vegetables, and fruits. "
                "Please upload a clear photo of an affected plant leaf, vegetable, or fruit."
            ),
        }

    # Organ and specific produce item classification
    organ = "leaf"
    detected_produce = None

    if any("banana" in l for l in top_labels) or (yellow_pct > 50.0 and leaf_pct < 15.0):
        organ = "fruit"
        detected_produce = "Banana"
    elif any(c in top_labels for c in ["orange", "lemon"]) or (orange_pct > 40.0 and leaf_pct < 15.0):
        organ = "fruit"
        detected_produce = "Orange"
    elif top1_label == "head_cabbage" and top1_prob > 0.80 and (red_pct + orange_pct < 5.0):
        # Potential cabbage produce head (disambiguated from Apple leaf in crop_disease_service)
        organ = "vegetable"
        detected_produce = "Cabbage"
    elif (red_pct + orange_pct >= 20.0 and leaf_pct < 20.0):
        if any(lbl in ["hip", "buckeye"] for lbl in top_labels):
            organ = "vegetable"
            detected_produce = "Tomato"
        elif any("pepper" in l for l in top_labels):
            organ = "vegetable"
            detected_produce = "Bell Pepper"
        elif any(lbl in ["grocery_store", "fig", "granny_smith", "apple"] for lbl in top_labels):
            organ = "fruit"
            detected_produce = "Apple"
        else:
            organ = "vegetable"
            detected_produce = "Tomato"
    elif any("cucumber" in l or "zucchini" in l for l in top_labels):
        organ = "vegetable"
        detected_produce = "Cucumber"
    elif any("squash" in l for l in top_labels) or (orange_pct >= 25.0 and leaf_pct >= 20.0):
        organ = "vegetable"
        detected_produce = "Squash"
    elif any("potato" in l for l in top_labels):
        organ = "vegetable"
        detected_produce = "Potato"
    elif any(f in top_labels for f in ["mango", "guava", "pomegranate"]):
        organ = "fruit"
        for f in ["mango", "guava", "pomegranate"]:
            if any(f in l for l in top_labels):
                detected_produce = f.title()
                break
    elif leaf_pct >= 20.0:
        organ = "leaf"
        detected_produce = None
    else:
        organ = "leaf"
        detected_produce = None

    return {
        "is_valid": True,
        "organ": organ,
        "category": "plant",
        "detected_produce": detected_produce,
        "error_message": None,
    }


def validate_plant_image(image: Image.Image) -> Tuple[bool, str, Optional[str]]:
    """Backward-compatible helper function."""
    res = validate_produce_image(image)
    return res["is_valid"], res["category"], res["error_message"]
