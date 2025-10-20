# backend/anomaly_detector/isolation_forest_detector.py
from __future__ import annotations
import os
import json
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

def detect_anomalies(csv_path: str, output_path: str, contamination: float = 0.2) -> dict:
    df = pd.read_csv(csv_path)
    feats = df[["latency_ms", "loss", "perplexity", "accuracy"]]

    model = IsolationForest(contamination=contamination, random_state=42)
    df["anomaly"] = model.fit_predict(feats)          # -1 = anomalie, 1 = normal
    df["score"] = model.decision_function(feats)      # plus petit = plus anormal

    anomalies = df[df["anomaly"] == -1].copy()

    result = {
        "total_points": int(len(df)),
        "anomalies_detected": int(len(anomalies)),
        "rows": df.to_dict(orient="records"),
        "anomalous_rows": anomalies.to_dict(orient="records")
    }

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"✅ Anomalies sauvegardées dans : {output_path}")
    return result

if __name__ == "__main__":
    here = Path(__file__).resolve().parent
    detect_anomalies(
        csv_path=str(here / "metrics.csv"),
        output_path=str(here / "results" / "isolation_results.json"),
    )
