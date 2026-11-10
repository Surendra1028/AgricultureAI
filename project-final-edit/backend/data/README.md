Put the downloaded crop dataset here as `crop_recommendation.csv`. Expected columns: N,P,K,temperature,humidity,ph,rainfall,label. Keep datasets with their license/source information.
## Crop yield dataset

For the optional yield-regression model, place a **real, documented, locally relevant** CSV at `backend/data/crop_yield.csv` with columns:

`crop,area_hectares,rainfall_mm,average_temperature_c,fertilizer_kg_per_hectare,year,yield_tonnes_per_hectare`

Train from the `backend` directory with `python -m app.ml.train_yield`. The script saves `artifacts/yield_prediction.joblib` and `artifacts/yield_metrics.json`. Do not use invented/synthetic figures as evidence of field performance. Prefer official district/state crop statistics and keep units consistent. Test on later years and regions not used during training before presenting this as a reliable estimate.
