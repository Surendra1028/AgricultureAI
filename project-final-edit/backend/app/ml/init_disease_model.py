"""Initialize and save the disease detection CNN architecture and classes for inference."""
import json
from pathlib import Path

DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy",
]


def build_disease_model(num_classes: int = len(DISEASE_CLASSES)):
    import tensorflow as tf
    from tensorflow.keras.layers import Conv2D, MaxPool2D, Flatten, Dense, Dropout, Input
    from tensorflow.keras.models import Sequential

    model = Sequential([
        Input(shape=(128, 128, 3)),
        Conv2D(filters=32, kernel_size=3, padding="same", activation="relu"),
        Conv2D(filters=32, kernel_size=3, activation="relu"),
        MaxPool2D(pool_size=2, strides=2),
        Conv2D(filters=64, kernel_size=3, padding="same", activation="relu"),
        Conv2D(filters=64, kernel_size=3, activation="relu"),
        MaxPool2D(pool_size=2, strides=2),
        Conv2D(filters=128, kernel_size=3, padding="same", activation="relu"),
        Conv2D(filters=128, kernel_size=3, activation="relu"),
        MaxPool2D(pool_size=2, strides=2),
        Conv2D(filters=256, kernel_size=3, padding="same", activation="relu"),
        Conv2D(filters=256, kernel_size=3, activation="relu"),
        MaxPool2D(pool_size=2, strides=2),
        Conv2D(filters=512, kernel_size=3, padding="same", activation="relu"),
        Conv2D(filters=512, kernel_size=3, activation="relu"),
        MaxPool2D(pool_size=2, strides=2),
        Dropout(0.25),
        Flatten(),
        Dense(1500, activation="relu"),
        Dropout(0.4),
        Dense(num_classes, activation="softmax"),
    ])
    model.compile(
        optimizer="adam",
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main():
    out = Path(__file__).resolve().parents[2] / "artifacts"
    out.mkdir(parents=True, exist_ok=True)

    model_path = out / "disease_model.keras"
    classes_path = out / "disease_classes.json"

    classes_path.write_text(json.dumps(DISEASE_CLASSES, indent=2))
    print(f"Saved {len(DISEASE_CLASSES)} classes to {classes_path}")

    if model_path.exists():
        print(f"Validated trained disease model exists at {model_path}. Preserving trained weights.")
    else:
        model = build_disease_model(len(DISEASE_CLASSES))
        model.save(model_path)
        print(f"Successfully generated architecture at {model_path}")


if __name__ == "__main__":
    main()
