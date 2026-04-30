import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest


def run_isolation_forest(df, column="price_log", contamination=0.05):
    print(f"[IsolationForest] Starting anomaly detection...")

    X = df[[column]].dropna()
    df = df.loc[X.index].copy()

    # 🔥 FIX: don't fail silently
    if len(df) < 10:
        print(f"[IsolationForest] Not enough data ({len(df)} rows). Skipping model.")

        # still create columns so pipeline doesn't break
        df["is_anomaly"] = False
        df["anomaly_score"] = 1
        df["anomaly_confidence"] = 0

        return df, None

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

    if price < 10:
        return "Prix trop bas (suspect)"
    if price > 100000:
        return "Prix extrêmement élevé"
    return "Anomalie statistique"