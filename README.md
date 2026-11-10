# 🌱 AgricultureAI – Smart Agriculture AI Platform

An AI-powered Smart Agriculture Platform designed to help farmers make informed agricultural decisions using Machine Learning, Deep Learning, and real-time weather information.

AgricultureAI provides intelligent solutions for crop recommendation, plant disease screening, fertilizer guidance, crop yield estimation, and weather-based agricultural insights through a user-friendly multilingual web application.

## 🚀 Key Features

### 🌾 1. Crop Recommendation
- Recommends suitable crops based on soil and environmental conditions.
- Uses Nitrogen (N), Phosphorus (P), Potassium (K), temperature, humidity, pH, and rainfall.
- Implements a Random Forest classification pipeline.

### 🦠 2. Plant Disease Detection
- Image-based disease screening for agricultural plants.
- Designed to support leaves, fruits, and vegetables.
- Uses TensorFlow/Keras and CNN-based image classification approaches.
- Includes a MobileNetV2 transfer-learning training pipeline.
- Provides disease-related information and advisory guidance.

**Note:** Leaf, fruit, and vegetable detection pipelines have different implementation and model-readiness levels. Refer to the project documentation before treating predictions as validated diagnoses.

### 🧪 3. Fertilizer Recommendation
- Provides fertilizer guidance based on crop requirements and soil nutrient values.
- Evaluates NPK nutrient differences.
- Provides estimated fertilizer recommendations.
- Supports multilingual agricultural guidance.

### 📊 4. Crop Yield Prediction
- Estimates agricultural yield based on crop and environmental parameters.
- Uses a Random Forest Regressor training pipeline.
- Considers rainfall, temperature, crop type, cultivated area, and fertilizer usage.
- Displays estimated production in different agricultural units.

### 🌦️ 5. Weather Information
- Integrates the Open-Meteo API.
- Retrieves current weather and forecast information.
- Provides temperature, humidity, rainfall, and wind-speed information.
- Supports location-based weather lookup.

### 🌐 6. Multilingual Support
The application supports three languages:
- English
- Telugu (తెలుగు)
- Hindi (हिन्दी)

### 👨‍🌾 7. Farmer Dashboard
- Farmer registration and authentication.
- Personalized application experience.
- Prediction history.
- Agricultural information and recommendations.

## 🛠️ Technology Stack

| Category | Technologies |
|---|---|
| Frontend | React.js, JavaScript |
| Styling | Tailwind CSS |
| Build Tool | Vite |
| Backend | Python, FastAPI |
| Machine Learning | Scikit-learn |
| Deep Learning | TensorFlow, Keras |
| Computer Vision | CNN, MobileNetV2 |
| Database | MySQL / SQLite |
| ORM | SQLAlchemy |
| Data Processing | NumPy, Pandas |
| Visualization | Recharts |
| Authentication | JWT, Password Hashing |
| Weather API | Open-Meteo |
| Model Storage | Joblib, TensorFlow Lite |

## 🏗️ Project Architecture

```text
AgricultureAI/
│
├── project-final-edit/
│   │
│   ├── frontend/
│   │   ├── src/
│   │   │   ├── App.jsx
│   │   │   ├── api.js
│   │   │   ├── i18n.js
│   │   │   ├── main.jsx
│   │   │   └── index.css
│   │   └── package.json
│   │
│   ├── backend/
│   │   ├── app/
│   │   │   ├── api/
│   │   │   │   └── routes/
│   │   │   ├── core/
│   │   │   ├── db/
│   │   │   ├── ml/
│   │   │   ├── services/
│   │   │   ├── schemas.py
│   │   │   └── main.py
│   │   │
│   │   └── requirements.txt
│   │
│   ├── database/
│   │   └── schema.sql
│   │
│   ├── docs/
│   │
│   └── README.md
```

## 🧠 Machine Learning Models

| Module | Algorithm / Approach | Task |
|---|---|---|
| Crop Recommendation | Random Forest Classifier | Classification |
| Plant Disease Detection | CNN / MobileNetV2 | Image Classification |
| Crop Yield Prediction | Random Forest Regressor | Regression |
| Fertilizer Recommendation | Rule-Based Logic | Nutrient Guidance |
| Weather Advisory | Rule-Based Logic + Weather API | Weather Insights |

**Machine Learning Workflow:**

1. Dataset collection.
2. Data preprocessing.
3. Exploratory Data Analysis.
4. Feature engineering.
5. Model training.
6. Model evaluation.
7. Model serialization.
8. Backend integration.
9. Real-time prediction.

## ⚙️ Installation and Setup

### Prerequisites

Make sure you have installed:

- Python 3.10 or later (check compatibility with the selected ML dependencies).
- Node.js and npm.
- MySQL Server (optional if using SQLite).
- Git.

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/AgricultureAI.git

cd AgricultureAI/project-final-edit
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Create a Python virtual environment:

```bash
python3 -m venv venv
```

Activate the environment:

**Ubuntu / Linux:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your backend environment variables and database connection according to the project's configuration.

### 3. Database Setup

For MySQL:

```sql
CREATE DATABASE agriculture_ai;
```

Import the provided database schema:

```bash
mysql -u root -p agriculture_ai < database/schema.sql
```

Configure the database connection in the backend environment file.

SQLite is also supported by the application.

### 4. Train Machine Learning Models

Navigate to the ML directory and execute the relevant training scripts after downloading and preparing the required datasets.

Example:

```bash
python -m app.ml.train_crop
python -m app.ml.train_yield
python -m app.ml.train_disease
```

Ensure that the saved model artifacts and class-label files are available at the locations expected by the backend services.

**Important:** Disease model architectures and inference preprocessing must be consistent. Do not use untrained initialization models for predictions.

### 5. Start the Backend Server

From the backend directory:

```bash
uvicorn app.main:app --reload
```

Backend API:

```text
http://127.0.0.1:8000
```

Interactive API documentation:

```text
http://127.0.0.1:8000/docs
```

### 6. Frontend Setup

Open another terminal:

```bash
cd project-final-edit/frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Open the local URL displayed by Vite in your browser.

## 📡 API Modules

| API Module | Description |
|---|---|
| Authentication | Farmer registration and login |
| Crop Recommendation | Crop suitability prediction |
| Disease Detection | Image-based disease screening |
| Fertilizer | Nutrient and fertilizer guidance |
| Yield Prediction | Agricultural yield estimation |
| Weather | Current weather and forecasts |
| History | Previous prediction records |

## 🔮 Future Enhancements

- Improve disease detection using real-world leaf, fruit, and vegetable datasets.
- Implement dedicated and validated deep learning models for different plant categories.
- Improve crop recommendations using region-specific agricultural datasets.
- Integrate verified soil-test reports.
- Develop more accurate fertilizer recommendation algorithms.
- Add explainable AI (XAI) to explain model predictions.
- Improve model performance using hyperparameter optimization.
- Add IoT-based soil monitoring.
- Integrate satellite and remote-sensing data.
- Deploy the application for real-world accessibility.

## 🎯 Project Objective

The primary objective of AgricultureAI is to combine Artificial Intelligence, Machine Learning, Deep Learning, and modern web technologies to make agricultural information more accessible and useful to farmers.

By providing data-driven agricultural insights through a multilingual interface, the platform aims to support smarter farming decisions and promote technology-driven agriculture.

## ⚠️ Disclaimer

This project is developed for educational, research, and demonstration purposes. Model predictions and fertilizer suggestions are not guaranteed agricultural prescriptions. The included synthetic datasets and unvalidated model pipelines should not be considered evidence of real-world accuracy. Farmers should verify important agricultural decisions with qualified agricultural experts and local soil-testing recommendations.

## 👨‍💻 Author

**AgricultureAI – Smart Agriculture AI Platform**

Developed as an AI/ML and Full Stack Development project.

## 📄 License

This project is available for educational and research purposes. Add an appropriate open-source license before permitting reuse or redistribution.
