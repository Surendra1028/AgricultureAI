# Farmer-friendly mode: how it works

## Why two modes?
Many farmers do not have NPK, pH, temperature and humidity readings available. Requiring those values would make the app difficult to use. The updated crop page therefore offers two separate flows.

## Basic Farmer Mode
Inputs:
- Village, town or district name
- Land size in acres
- Season (Kharif, Rabi or Summer)
- Irrigation source (rain-fed, borewell, canal or other)
- Soil type (optional; `Don't know` is valid)
- Previous crop (optional)

Endpoint: `POST /api/v1/recommend/basic`

This version uses transparent starter rules to shortlist broad crop options by season and irrigation category. It is **not** a trained machine-learning model, does not infer soil nutrients, and does not provide a guaranteed crop recommendation. Before field use, replace/extend these starter rules with verified district-, soil-, season- and irrigation-specific recommendations from agricultural university/KVK/state agriculture department sources. Keep the source, season/year and geographical coverage with each rule.

Example request:

```json
{
  "location": "Nellore, Andhra Pradesh",
  "land_acres": 2,
  "season": "Kharif",
  "irrigation": "Canal",
  "soil_type": "Don't know",
  "previous_crop": ""
}
```

## Advanced Soil Report Mode
Requires measured N, P, K, pH and climate readings. The existing Random Forest model expects those exact features. Do not substitute guessed or generic values. If a farmer has no soil report, direct them to a soil testing facility / Soil Health Card service rather than manufacturing values.

## Weather lookup
`GET /api/v1/location/lookup?name=<village-or-district>` uses Open-Meteo Geocoding to resolve a place to coordinates. The frontend then calls `GET /api/v1/weather` with the coordinates. If the location result is ambiguous, the user should choose/confirm the correct town or district; the current starter UI uses the first returned match.

## Safety and agronomy notes
- Do not provide fertilizer dosage without suitable soil test and crop-specific recommendations.
- Disease image output is screening only; refer uncertain/severe cases to an agricultural officer/KVK.
- Yield estimates should only be displayed after training and validating on representative local historical data.
- Keep Basic Farmer Mode and Advanced Soil Report Mode visibly distinct so users do not confuse rule-based suggestions with ML outputs.
