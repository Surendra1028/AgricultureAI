# Smart Agriculture AI Platform

Full-stack educational project using React + Tailwind, FastAPI, Scikit-learn, TensorFlow/Keras, MySQL, Open-Meteo and Recharts.

## Important
This ZIP contains runnable application code, API endpoints, database models, frontend screens, and model-training scripts. It does not contain trained disease/crop/yield models or licensed real-world datasets. Download datasets listed in `docs/DATASETS.md` and train models before presenting predictions as model results. The fertilizer module provides transparent basic nutrient observations, not fertilizer dosage. All outputs require local agricultural validation.


## Farmer accounts and privacy
- Register: `POST /api/v1/auth/register` with `full_name`, `email`, and `password` (minimum 8 characters).
- Login: `POST /api/v1/auth/login` with `email` and `password`.
- Current account: `GET /api/v1/auth/me` using `Authorization: Bearer <access_token>`.
- Prediction endpoints and history require login. History is filtered by the authenticated user's ID.
- Passwords are stored as salted scrypt hashes, never as plain text. Access tokens expire after the configured number of minutes.
- Set a long, random `SECRET_KEY` in `backend/.env` before deployment. The example key is for local development only. Use HTTPS in production.

## Setup

### Backend
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```
Create MySQL database:
```sql
CREATE DATABASE smart_agriculture CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
Set `DATABASE_URL` in `backend/.env`, then:
```bash
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

For local testing without MySQL, set `DATABASE_URL=sqlite:///./smart_agriculture.db` in `.env`.

### Frontend
In another terminal:
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open http://localhost:5173

### Train crop model
Download crop dataset and save as `backend/data/crop_recommendation.csv`, with columns:
`N,P,K,temperature,humidity,ph,rainfall,label`
Then from `backend`:
```bash
python -m app.ml.train_crop
```

### Train disease model
Download/extract PlantVillage into class folders under `datasets/plantvillage`, install TensorFlow, then from `backend`:
```bash
python -m app.ml.train_disease --data-dir ../datasets/plantvillage
```

### Train yield model (optional)
Prepare `backend/data/crop_yield.csv` with columns:
`crop,area_hectares,rainfall_mm,average_temperature_c,fertilizer_kg_per_hectare,year,yield_tonnes_per_hectare`
Then run from `backend`:
```bash
python -m app.ml.train_yield
```
The script saves the regression model and MAE/RMSE/R² metrics. Use documented real historical data and validate on later years/unseen regions.

TensorFlow is an optional, relatively large dependency for disease detection. Install it separately when ready to train/run the CNN:
```bash
pip install -r requirements-ml.txt
```

See `docs/BUILD_GUIDE.md` and `docs/MODEL_VALIDATION.md`.

## Farmer-friendly input modes (updated)

The crop recommendation screen now has two modes:

- **Basic Farmer Mode:** asks for village/town/district, land size, season, irrigation source, and optional soil type/previous crop. It does not require NPK, pH, temperature, or humidity values. The backend returns broad, transparent rule-based crop options. This is a starter decision-support flow, **not a trained ML prediction** and not a district-specific agronomy guarantee.
- **Advanced Soil Report Mode:** accepts the NPK, pH and climate readings required by the trained crop classifier. Use actual soil-lab/weather readings; do not invent values.

The Weather page now accepts a village/town/district name. The backend resolves it using Open-Meteo Geocoding and fetches the forecast using the returned coordinates. A location lookup can return multiple matches; this starter UI uses the first match, so verify the displayed place/result before relying on it.

New endpoints:
- `POST /api/v1/recommend/basic`
- `GET /api/v1/location/lookup?name=Nellore`

Basic mode deliberately avoids showing a confidence score. Its crop options must be checked against current local agriculture department/KVK advisories, water availability, seed suitability, soil test and market conditions before sowing.

## Farmer language support (English / Telugu / Hindi)

The frontend includes a language selector in the top header. Farmers can switch the interface and supported advisory text between English, Telugu, and Hindi without sending farm data to a translation service. Basic crop recommendation notes, next steps, limitations, fertilizer safety guidance, disease-screening disclaimers, and weather-based advisories have offline translations. Weather advice is generated from forecast thresholds and is intended as general decision support, not a crop-specific prescription. Unknown model class names or provider-generated text may remain in English until a translation is added to `frontend/src/i18n.js`.

To add or edit translations, update `frontend/src/i18n.js`. The language selection applies immediately to the current result/advisory display.

## Frontend build and dependency compatibility

The frontend uses a Vite 6-compatible React plugin version pinned in `frontend/package.json`.
From the `frontend` directory run:

```bash
npm install
npm run build
npm run preview
```

If `npm install` reports `EAI_AGAIN` or a DNS/network error for `registry.npmjs.org`, the machine cannot currently reach the npm registry. Restore internet/DNS access and rerun `npm install`; this is not an application source-code error. The build output is generated in `frontend/dist/`.


## Farmer accounts (registration and login)

The application now includes email/password registration and login. Passwords are stored as salted scrypt hashes (never plaintext). Successful registration/login returns a signed bearer access token. The React app stores the token for the current browser session and automatically attaches it to protected API requests. The `/api/v1/auth/me` endpoint validates the current session. Prediction endpoints and prediction history require login, and history is filtered by the authenticated farmer's user ID.

Authentication endpoints:

- `POST /api/v1/auth/register` — JSON: `{ "full_name": "Farmer Name", "email": "farmer@example.com", "password": "minimum8chars" }`
- `POST /api/v1/auth/login` — JSON: `{ "email": "farmer@example.com", "password": "minimum8chars" }`
- `GET /api/v1/auth/me` — requires `Authorization: Bearer <access_token>`

For local development, set `SECRET_KEY` in `backend/.env`. Before deployment, replace the example value with a unique, randomly generated secret, use HTTPS, configure exact frontend origins, and consider moving browser token storage to secure HttpOnly cookies. Add email verification, password reset, rate limiting, and account lockout before production use. Existing prediction rows created before accounts were added may have a null `user_id` and will not appear in any farmer's private history.
