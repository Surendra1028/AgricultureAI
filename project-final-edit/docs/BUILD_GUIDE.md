# Build and run guide

## 1. Backend (Ubuntu)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

For a quick local run, edit `backend/.env` and use:

```env
DATABASE_URL=sqlite:///./smart_agriculture.db
FRONTEND_ORIGINS=http://localhost:5173
```

Start the API from the `backend` directory:

```bash
uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs` for interactive API docs.

## 2. Frontend

In a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173`. For a production bundle, run `npm run build`; Vite writes output to `frontend/dist`. Preview it with `npm run preview`.

## 3. MySQL option

Create the database using `database/schema.sql`, then set `DATABASE_URL` in `backend/.env` to a valid MySQL/PyMySQL connection string. Never commit real credentials.

## 4. Optional model setup

- Crop classification: put the dataset at `backend/data/crop_recommendation.csv`, then run `python -m app.ml.train_crop` from `backend`.
- Yield regression: put the documented historical dataset at `backend/data/crop_yield.csv`, then run `python -m app.ml.train_yield` from `backend`.
- Disease CNN: install `pip install -r requirements-ml.txt`; put PlantVillage class folders under `datasets/plantvillage` at the project root; from `backend`, run `python -m app.ml.train_disease --data-dir ../datasets/plantvillage`.

The ZIP does not include licensed datasets or trained model artifacts. A model endpoint returns a setup-required response until its model has been trained. Do not present untrained modules as functioning AI predictions.

## 5. Smoke checks

With the backend running, check `/health` and `/docs`. The test suite can be run from `backend` with:

```bash
pytest -q
```

Weather and geocoding require internet access. Frontend package installation/build also requires npm registry access unless dependencies are already cached.


## Authentication setup

Copy `backend/.env.example` to `backend/.env` and set a unique `SECRET_KEY` before running the app. New farmers can register from the frontend. Login returns a bearer token; the frontend attaches it automatically to prediction and history requests. Each farmer sees only prediction records linked to their account.
