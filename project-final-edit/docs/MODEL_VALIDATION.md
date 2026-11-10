# Model validation

- Split training, validation and test data; do not evaluate on training data.
- For crop classification report accuracy, macro precision/recall/F1 and confusion matrix.
- For yield regression report MAE, RMSE and R².
- Check class imbalance, missing values, outliers and data leakage.
- For images, split carefully to avoid near-duplicate leakage; test on images from different farms/cameras.
- Confidence is not certainty. Consider an uncertainty threshold.
- Validate all recommendations with local agricultural experts and soil tests.
- Never treat disease screening as a confirmed diagnosis or nutrient guidance as a fertilizer dosage prescription.
