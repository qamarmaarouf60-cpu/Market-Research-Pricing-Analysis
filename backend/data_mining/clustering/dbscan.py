import pandas as pd
import numpy as np
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import StandardScaler


def run_dbscan(df, column="price_log", eps=0.5, min_samples=3):
    """
    Run DBSCAN clustering on product prices.
    DBSCAN is useful for finding clusters of arbitrary shape and detecting noise.
    Points labeled -1 are noise (potential outliers).
    """
    print(f"[DBSCAN] Starting with eps={eps}, min_samples={min_samples}...")

    X = df[[column]].dropna().values
    if len(X) < min_samples:
        print(f"[DBSCAN] Not enough data ({len(X)} products).")
        return df

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    db = DBSCAN(eps=eps, min_samples=min_samples)
    df = df.copy()
    df["dbscan_cluster"] = db.fit_predict(X_scaled)

    n_clusters = len(set(df["dbscan_cluster"])) - (1 if -1 in df["dbscan_cluster"].values else 0)
    n_noise = (df["dbscan_cluster"] == -1).sum()

    print(f"[DBSCAN] Found {n_clusters} clusters, {n_noise} noise points (outliers)")

    # Label noise points
    df["dbscan_label"] = df["dbscan_cluster"].apply(
        lambda x: "Outlier" if x == -1 else f"Cluster {x}"
    )

    summary = df.groupby("dbscan_label")["price_mad"].agg(["count", "min", "mean", "max"])
    print(f"[DBSCAN] Summary:\n{summary}\n")

    return df, db


def get_dbscan_outliers(df):
    """Return products flagged as noise/outliers by DBSCAN."""
    if "dbscan_cluster" not in df.columns:
        return pd.DataFrame()
    return df[df["dbscan_cluster"] == -1][["name", "price_mad", "source", "url"]].reset_index(drop=True)