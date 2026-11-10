# Farmer language support

AgriSmart AI provides an in-app language selector for:
- English (`en`)
- Telugu (`te`)
- Hindi (`hi`)

## What is translated

- Main farmer-facing navigation and form labels.
- Basic crop recommendation names, notes, soil note, next step and limitations.
- Fertilizer guidance and safety disclaimer.
- Disease screening disclaimer and selected common disease labels.
- Weather-based advisory messages (rain probability, strong wind, high temperature, high humidity).
- Weather advisory caution that the output is decision support and must be checked with local agricultural experts.

## How it works

Translations are bundled locally in `frontend/src/i18n.js`; no external translation API or internet connection is needed to switch languages. The `translate()` helper translates known UI/advisory phrases. `translateCropResult()` recursively translates known strings and field labels in API responses. When an unknown crop/disease class or new backend message is received, the original English text is shown rather than guessing a translation. Add its reviewed Telugu and Hindi equivalents to the dictionary.

## Important limitation

Weather advisories use simple thresholds and forecast fields. They are not a complete agronomy model. Do not apply pesticides, fertilizer dosages, or irrigation solely based on these messages. Confirm crop- and district-specific decisions with a local agriculture officer/KVK.
