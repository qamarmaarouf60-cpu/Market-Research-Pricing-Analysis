import pandas as pd
import numpy as np
from sklearn.neighbors import LocalOutlierFactor


def run_lof(df, column="price_log", n_neighbors=20, contamination=0.05):
    """
    Detect anomalies using Local Outlier Factor (LOF).
    """

    print(f"[LOF] Starting anomaly detection...")

    # 🔥 FIX: align dataframe with valid rows
    X = df[[column]].dropna()
    df = df.loc[X.index].copy()

    # Safety checks
    if X.empty:
        print("[LOF] No valid data")
        return df, None

    if len(df) < 3:
        print("[LOF] Not enough samples")
        return df, None

    if len(df) < n_neighbors:
        n_neighbors = max(2, len(df) // 2)
        print(f"[LOF] Adjusted n_neighbors to {n_neighbors}")

    model = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination
    )

    predictions = model.fit_predict(X)

    df["lof_score"] = predictions  # -1 anomaly, 1 normal
    df["lof_anomaly"] = df["lof_score"] == -1

    # 🔥 higher = more anomalous
    df["lof_factor"] = -model.negative_outlier_factor_

    df["lof_factor"] = -model.negative_outlier_factor_

    # Normalize score between 0 and 1
    lof_vals = df["lof_factor"].values

    df["lof_confidence"] = (
        (lof_vals - lof_vals.min()) /
        (lof_vals.max() - lof_vals.min() + 1e-9)
    )

    n_anomalies = df["lof_anomaly"].sum()
    print(f"[LOF] Detected {n_anomalies} anomalies out of {len(df)} products")

    return df, model


def get_lof_outliers(df):
    """Return LOF anomalies sorted by severity."""
    if "lof_anomaly" not in df.columns:
        return []

    outliers = df[df["lof_anomaly"]].sort_values("lof_factor", ascending=False)

    return [
        {
            "name": row.get("name", ""),
            "price_mad": round(float(row.get("price_mad", 0)), 2),
            "source": row.get("source", ""),
            "lof_factor": round(float(row.get("lof_factor", 0)), 4),
             # Normalized confidence score
            "lof_confidence": round(
                float(row.get("lof_confidence", 0)),
                4
            ),
        }
        for _, row in outliers.iterrows()
    ]