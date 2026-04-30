import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score


PRICE_SEGMENT_LABELS = {
    0: "Bas de gamme",
    1: "Milieu de gamme",
    2: "Haut de gamme",
}


def find_optimal_k(df, column="price_log", k_range=range(2, 8)):
    """Find optimal number of clusters using silhouette score."""
    X = df[[column]].dropna()
    n_samples = len(X)

    best_k = 3
    best_score = -1

    for k in k_range:
        # 🚨 CRITICAL FIX
        if k >= n_samples:
            continue

        if len(X) < k:
            continue

        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = km.fit_predict(X)

        # 🚨 EXTRA SAFETY (very important)
        if len(set(labels)) < 2:
            continue

        score = silhouette_score(X, labels)
        print(f"[KMeans] k={k} → silhouette score: {score:.4f}")

        if score > best_score:
            best_score = score
            best_k = k

    print(f"[KMeans] Optimal k={best_k} (score={best_score:.4f})")
    return best_k


def run_kmeans(df, n_clusters=3, column="price_log", auto_k=False):
    """
    Run KMeans clustering on product prices.
    Returns df with 'cluster' and 'price_segment' columns.
    """
    print(f"[KMeans] Starting clustering with n_clusters={n_clusters}...")

    X = df[[column]].dropna()

    if len(X) < n_clusters:
        print(f"[KMeans] Not enough data ({len(X)} products) for {n_clusters} clusters.")
        return df

    if auto_k:
        n_clusters = find_optimal_k(df, column)

    km = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df = df.copy()
    df["cluster"] = km.fit_predict(X)

    # Sort clusters by mean price so label 0 = cheapest
    cluster_means = df.groupby("cluster")[column].mean().sort_values()
    rank_map = {old: new for new, old in enumerate(cluster_means.index)}
    df["cluster"] = df["cluster"].map(rank_map)

    # Assign human-readable labels
    df["price_segment"] = df["cluster"].map(
        {i: PRICE_SEGMENT_LABELS.get(i, f"Segment {i}") for i in range(n_clusters)}
    )

    # Summary
    summary = df.groupby("price_segment")["price_mad"].agg(["count", "min", "mean", "max"])
    print(f"[KMeans] Clustering done:\n{summary}\n")

    return df, km


def get_cluster_summary(df):
    """Return a clean summary dict per segment."""
    if "price_segment" not in df.columns:
        return {}

    summary = []
    for segment, group in df.groupby("price_segment"):
        summary.append({
            "segment": segment,
            "count": len(group),
            "min_price": round(float(group["price_mad"].min()), 2),
            "avg_price": round(float(group["price_mad"].mean()), 2),
            "max_price": round(float(group["price_mad"].max()), 2),
            "sources": group["source"].value_counts().to_dict(),
        })
    return summary