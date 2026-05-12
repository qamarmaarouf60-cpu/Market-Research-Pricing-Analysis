import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def run_isolation_forest(df, column="price_log", contamination=0.05):
    print(f"[IsolationForest] Starting anomaly detection...")
    X = df[[column]].dropna()
    df = df.loc[X.index].copy()

    if len(df) < 10:
        df["is_anomaly"] = False
        df["anomaly_score"] = 1.0
        df["anomaly_confidence"] = 0.0
        return df, None

    model = IsolationForest(
        contamination=contamination,
        random_state=42,
        n_estimators=100
    )
    preds = model.fit_predict(X)           # -1 = anomalie, 1 = normal
    scores = model.decision_function(X)    # plus bas = plus suspect

    df["is_anomaly"]         = preds == -1
    df["anomaly_score"]      = scores
    # Normalise en [0,1] : 1 = très suspect
    df["anomaly_confidence"] = 1 - (
        (scores - scores.min()) / (scores.max() - scores.min() + 1e-9)
    )

    n = df["is_anomaly"].sum()
    print(f"[IsolationForest] Detected {n} anomalies out of {len(df)} products")
    return df, model

def get_anomaly_report(df):
    """Return structured anomaly report."""
    if "is_anomaly" not in df.columns:
        return []

    anomalies = df[df["is_anomaly"]].copy()
    anomalies = anomalies.sort_values("anomaly_confidence", ascending=False)

    report = []

    for _, row in anomalies.iterrows():
        report.append({
            "name": row.get("name", ""),
            "price_mad": round(float(row.get("price_mad", 0)), 2),
            "price_text": row.get("price_text", ""),
            "source": row.get("source", ""),
            "url": row.get("url", ""),
            "anomaly_confidence": round(float(row.get("anomaly_confidence", 0)), 4),
            "reason": _guess_reason(row),
        })

    return report


def _guess_reason(row):
    price = row.get("price_mad", 0)

    if price < 50:
        return "Prix trop bas (suspect)"
    if price > 200000:
        return "Prix extrêmement élevé"
    return "Anomalie statistique"