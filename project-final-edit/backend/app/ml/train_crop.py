from pathlib import Path
import json, joblib, pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data" / "crop_recommendation.csv"
OUT = ROOT / "artifacts"
FEATURES = ["N","P","K","temperature","humidity","ph","rainfall"]
def main():
    if not DATA.exists():
        raise FileNotFoundError(f"Download a real dataset to {DATA}. See docs/DATASETS.md.")
    df = pd.read_csv(DATA)
    missing = [c for c in FEATURES + ["label"] if c not in df.columns]
    if missing: raise ValueError(f"Missing dataset columns: {missing}")
    X, y = df[FEATURES], df["label"].astype(str)
    if y.nunique() < 2 or y.value_counts().min() < 2:
        raise ValueError("Each crop label must have at least 2 rows and the dataset must contain at least 2 crop classes.")
    Xtr, Xte, ytr, yte = train_test_split(X,y,test_size=.2,random_state=42,stratify=y)
    model = Pipeline([("imputer",SimpleImputer(strategy="median")),
                      ("classifier",RandomForestClassifier(n_estimators=300,random_state=42,class_weight="balanced"))])
    model.fit(Xtr,ytr); pred = model.predict(Xte)
    OUT.mkdir(parents=True,exist_ok=True); joblib.dump(model,OUT/"crop_recommendation.joblib")
    metrics = {"accuracy":accuracy_score(yte,pred),"report":classification_report(yte,pred,output_dict=True)}
    (OUT/"crop_metrics.json").write_text(json.dumps(metrics,indent=2))
    print(json.dumps({"accuracy":metrics["accuracy"],"saved":str(OUT/"crop_recommendation.joblib")},indent=2))
if __name__ == "__main__": main()
