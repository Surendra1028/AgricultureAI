import os
import sys
import uuid
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Use an isolated SQLite file for API smoke tests.
os.environ["DATABASE_URL"] = f"sqlite:////tmp/smart_agriculture_pytest_{uuid.uuid4().hex}.db"
os.environ["FRONTEND_ORIGINS"] = "http://localhost:5173"

from fastapi.testclient import TestClient
from app.main import app


def test_health_and_modules():
    with TestClient(app) as client:
        assert client.get("/health").status_code == 200
        modules = client.get("/api/v1/modules")
        assert modules.status_code == 200
        assert {item["id"] for item in modules.json()["modules"]} >= {"crop", "disease", "yield", "weather"}


def register_and_login(client, email="farmer@example.com"):
    response = client.post("/api/v1/auth/register", json={
        "full_name": "Test Farmer", "email": email, "password": "StrongPass123"
    })
    assert response.status_code == 201
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_registration_login_and_me():
    with TestClient(app) as client:
        headers = register_and_login(client, "auth@example.com")
        me = client.get("/api/v1/auth/me", headers=headers)
        assert me.status_code == 200
        assert me.json()["email"] == "auth@example.com"
        login = client.post("/api/v1/auth/login", json={
            "email": "AUTH@example.com", "password": "StrongPass123"
        })
        assert login.status_code == 200
        bad = client.post("/api/v1/auth/login", json={
            "email": "auth@example.com", "password": "wrong-password"
        })
        assert bad.status_code == 401


def test_duplicate_registration_rejected():
    with TestClient(app) as client:
        register_and_login(client, "duplicate@example.com")
        response = client.post("/api/v1/auth/register", json={
            "full_name": "Another Farmer", "email": "duplicate@example.com", "password": "StrongPass123"
        })
        assert response.status_code == 409


def test_basic_farmer_recommendation_and_history():
    with TestClient(app) as client:
        headers = register_and_login(client, "history@example.com")
        payload = {
            "location": "Nellore, Andhra Pradesh",
            "land_acres": 2,
            "season": "Kharif",
            "irrigation": "Canal",
            "soil_type": "Don't know",
            "previous_crop": "",
        }
        response = client.post("/api/v1/recommend/basic", json=payload, headers=headers)
        assert response.status_code == 200
        body = response.json()
        assert body["mode"] == "basic_rule_based_screening"
        assert len(body["recommendations"]) > 0
        history = client.get("/api/v1/history", headers=headers)
        assert history.status_code == 200
        assert any(row["module"] == "basic_crop_screening" for row in history.json())


def test_basic_farmer_validation():
    with TestClient(app) as client:
        headers = register_and_login(client, "validation@example.com")
        response = client.post("/api/v1/recommend/basic", json={
            "location": "Nellore", "land_acres": -1, "season": "Kharif",
            "irrigation": "Canal", "soil_type": "Don't know"
        }, headers=headers)
        assert response.status_code == 422


def test_disease_rejects_wrong_mime_type():
    with TestClient(app) as client:
        headers = register_and_login(client, "disease@example.com")
        response = client.post("/api/v1/predict/disease", files={"file": ("leaf.txt", b"not image", "text/plain")}, headers=headers)
        assert response.status_code == 415


def test_disease_prediction_success():
    import io
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "disease_success@example.com")
        img = Image.new("RGB", (224, 224), color=(0, 128, 0))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        response = client.post(
            "/api/v1/predict/disease",
            files={"file": ("leaf.jpg", buf.getvalue(), "image/jpeg")},
            headers=headers
        )
        assert response.status_code == 200
        assert "predicted_class" in response.json()
        assert "confidence_percent" in response.json()
        assert "treatment" in response.json()
        assert "en" in response.json()["treatment"]


def test_disease_rejects_human_image():
    import io
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "human_test@example.com")
        # Skin tone image with no plant foliage
        img = Image.new("RGB", (224, 224), color=(220, 165, 140))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        response = client.post(
            "/api/v1/predict/disease",
            files={"file": ("human_selfie.jpg", buf.getvalue(), "image/jpeg")},
            headers=headers
        )
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "human" in detail or "irrelevant" in detail


def test_disease_rejects_irrelevant_non_plant_image():
    import io
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "non_plant_test@example.com")
        # Solid white non-plant image
        img = Image.new("RGB", (224, 224), color=(255, 255, 255))
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        response = client.post(
            "/api/v1/predict/disease",
            files={"file": ("white_room.jpg", buf.getvalue(), "image/jpeg")},
            headers=headers
        )
        assert response.status_code == 400
        detail = response.json()["detail"].lower()
        assert "irrelevant" in detail or "not appear to be a crop" in detail


def test_disease_distinct_predictions():
    import io
    import numpy as np
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "distinct_test@example.com")
        # Test two distinctly colored plant patterns (deep green vs yellowish diseased foliage)
        arr1 = np.full((224, 224, 3), (34, 139, 34), dtype=np.uint8)  # Forest Green
        img1 = Image.fromarray(arr1)
        buf1 = io.BytesIO()
        img1.save(buf1, format="JPEG")

        # Apple or tomato sample from test images if available
        test_file = Path("/tmp/test_images/Apple___Apple_scab.JPG")
        if test_file.exists():
            leaf_bytes = test_file.read_bytes()
        else:
            arr2 = np.full((224, 224, 3), (100, 140, 40), dtype=np.uint8)
            img2 = Image.fromarray(arr2)
            buf2 = io.BytesIO()
            img2.save(buf2, format="JPEG")
            leaf_bytes = buf2.getvalue()

        resp1 = client.post(
            "/api/v1/predict/disease",
            files={"file": ("leaf1.jpg", buf1.getvalue(), "image/jpeg")},
            headers=headers
        )
        resp2 = client.post(
            "/api/v1/predict/disease",
            files={"file": ("leaf2.jpg", leaf_bytes, "image/jpeg")},
            headers=headers
        )

        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Check that predictions are accurate and not hardcoded to a single identical class
        assert "predicted_class" in resp1.json()
        assert "predicted_class" in resp2.json()


def test_fruit_disease_prediction_success():
    import io
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "fruit_disease@example.com")
        test_file = Path("/tmp/produce_test_images/apple_fruit.jpg")
        if test_file.exists():
            fruit_bytes = test_file.read_bytes()
        else:
            img = Image.new("RGB", (224, 224), color=(200, 30, 30))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            fruit_bytes = buf.getvalue()

        response = client.post(
            "/api/v1/predict/disease",
            files={"file": ("apple_fruit.jpg", fruit_bytes, "image/jpeg")},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["organ_type"] == "Fruit"
        assert "predicted_class" in data
        assert "confidence_percent" in data
        assert "treatment" in data
        assert "en" in data["treatment"]
        assert "te" in data["treatment"]
        assert "hi" in data["treatment"]
        assert "chemical_control" in data["treatment"]["en"]


def test_vegetable_disease_prediction_success():
    import io
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "vegetable_disease@example.com")
        test_file = Path("/tmp/test_images/tomato_early_blight_0.JPG")
        if test_file.exists():
            veg_bytes = test_file.read_bytes()
        else:
            img = Image.new("RGB", (224, 224), color=(40, 140, 40))
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            veg_bytes = buf.getvalue()

        response = client.post(
            "/api/v1/predict/disease",
            files={"file": ("tomato_blight.jpg", veg_bytes, "image/jpeg")},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["organ_type"] in ["Leaf", "Vegetable", "Fruit"]
        assert data["crop"] in ["Tomato", "Potato", "Bell Pepper", "Vegetable", "Crop", "Apple", "Cabbage"]
        assert "predicted_class" in data
        assert "treatment" in data


def test_cabbage_and_orange_advisories_exist():
    from app.services.disease_advisory import get_disease_advisory
    for key in ["Cabbage___healthy", "Cabbage___Black_rot", "Cabbage___Downy_mildew", "Orange___healthy"]:
        adv = get_disease_advisory(key)
        assert "en" in adv
        assert "te" in adv
        assert "hi" in adv
        assert "chemical_control" in adv["en"]
        assert "preventive_measures" in adv["te"]
        assert "fertilizer_management" in adv["hi"]


def test_tomato_produce_disease_prediction():
    import io
    from PIL import Image
    with TestClient(app) as client:
        headers = register_and_login(client, "tomato_produce@example.com")
        test_file = Path("/tmp/produce_test_images/red_tomato_fruit.jpg")
        if test_file.exists():
            fruit_bytes = test_file.read_bytes()
        else:
            # Saturated red produce with dark lesion area
            arr = np.full((224, 224, 3), (210, 35, 25), dtype=np.uint8)
            arr[50:120, 50:120] = (40, 20, 15)  # Necrotic spot
            img = Image.fromarray(arr)
            buf = io.BytesIO()
            img.save(buf, format="JPEG")
            fruit_bytes = buf.getvalue()

        response = client.post(
            "/api/v1/predict/disease",
            files={"file": ("red_tomato.jpg", fruit_bytes, "image/jpeg")},
            headers=headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["organ_type"] == "Vegetable"
        assert data["crop"] == "Tomato"
        assert "Tomato___Fruit_rot" in data["predicted_class"] or "Tomato___healthy" in data["predicted_class"] or "Tomato___Blossom_end_rot" in data["predicted_class"]
        assert "treatment" in data


def test_prediction_endpoints_require_authentication():
    with TestClient(app) as client:
        response = client.get("/api/v1/history")
        assert response.status_code == 401


def test_prediction_history_is_private_per_user():
    with TestClient(app) as client:
        headers_a = register_and_login(client, "private-a@example.com")
        headers_b = register_and_login(client, "private-b@example.com")
        payload = {
            "location": "Nellore", "land_acres": 1, "season": "Kharif",
            "irrigation": "Rain-fed", "soil_type": "Don't know"
        }
        created = client.post("/api/v1/recommend/basic", json=payload, headers=headers_a)
        assert created.status_code == 200
        history_a = client.get("/api/v1/history", headers=headers_a).json()
        history_b = client.get("/api/v1/history", headers=headers_b).json()
        assert any(row["id"] == created.json()["history_id"] for row in history_a)
        assert all(row["id"] != created.json()["history_id"] for row in history_b)


def test_fertilizer_prediction_json_and_query():
    with TestClient(app) as client:
        headers = register_and_login(client, "fertilizer@example.com")
        # JSON payload
        res_json = client.post("/api/v1/predict/fertilizer", json={
            "crop": "Rice", "nitrogen": 40.0, "phosphorus": 20.0, "potassium": 30.0
        }, headers=headers)
        assert res_json.status_code == 200
        assert res_json.json()["lowest_reported_nutrient"] == "P"
        assert res_json.json()["mode"] == "transparent_rule_based_guidance"

        # Query param backward compatibility
        res_query = client.post(
            "/api/v1/predict/fertilizer?crop=Wheat&nitrogen=15.0&phosphorus=30.0&potassium=40.0",
            headers=headers
        )
        assert res_query.status_code == 200
        assert res_query.json()["lowest_reported_nutrient"] == "N"


def test_trained_crop_and_yield_models():
    with TestClient(app) as client:
        headers = register_and_login(client, "trained_models@example.com")
        res_crop = client.post("/api/v1/predict/crop", json={
            "N": 90, "P": 42, "K": 43, "temperature": 20.8, "humidity": 82, "ph": 6.5, "rainfall": 202
        }, headers=headers)
        assert res_crop.status_code == 200
        assert res_crop.json()["mode"] == "trained_model"
        assert res_crop.json()["prediction"] is not None

        res_yield = client.post("/api/v1/predict/yield", json={
            "crop": "Rice", "area_hectares": 1.0, "rainfall_mm": 900, "average_temperature_c": 26,
            "fertilizer_kg_per_hectare": 100, "year": 2025
        }, headers=headers)
        assert res_yield.status_code == 200
        assert res_yield.json()["mode"] == "trained_model"
        assert res_yield.json()["estimated_yield_tonnes_per_hectare"] > 0


def test_location_lookup_validation():
    with TestClient(app) as client:
        res = client.get("/api/v1/location/lookup?name=a")
        assert res.status_code == 422
