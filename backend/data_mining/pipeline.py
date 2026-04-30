import os
import sys
import json
import pandas as pd

# ── Django setup ─────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

# ── Core modules ─────────────────────────────────────────────
from data_mining.preprocessing.cleaning import run_cleaning
from data_mining.preprocessing.normalization import run_normalization

from data_mining.statistics.descriptive import run_descriptive

from data_mining.clustering.kmeans import run_kmeans, get_cluster_summary
from data_mining.clustering.dbscan import run_dbscan, get_dbscan_outliers

from data_mining.anomaly_detection.isolation_forest import (
    run_isolation_forest,
    get_anomaly_report
)

from data_mining.anomaly_detection.lof import (
    run_lof,
    get_lof_outliers
)

from data_mining.dimensionality_reduction.pca import run_pca, get_pca_summary


# ── Optional modules ─────────────────────────────────────────
try:
    from data_mining.association_rules.apriori import run_apriori, get_top_rules
    from data_mining.association_rules.fpgrowth import run_fpgrowth
    ASSOCIATION_AVAILABLE = True
except ImportError:
    ASSOCIATION_AVAILABLE = False
    print("[Pipeline] mlxtend not installed → skipping association rules")


# ── SAFE SERIALIZER ──────────────────────────────────────────
def safe(obj):
    """Convert anything into JSON-safe format."""
    if obj is None:
        return None
    if isinstance(obj, pd.DataFrame):
        return obj.to_dict("records")
    if isinstance(obj, (list, dict, str, int, float, bool)):
        return obj
    if hasattr(obj, "tolist"):  # numpy
        return obj.tolist()
    return str(obj)


# ─────────────────────────────────────────────────────────────
def run_pipeline(query=None, n_clusters=3, contamination=0.05, save_report=True):

    print("=" * 60)
    print(" MARKET RESEARCH — DATA MINING PIPELINE")
    print("=" * 60)

    if query:
        print(f" Query filter: {query}")
    print()

    # =========================
    # 1. CLEANING
    # =========================
    print("── Step 1: Cleaning ──")
    df = run_cleaning(query=query)

    if df is None or df.empty:
        print("[Pipeline] No data found.")
        return None

    print()

    # =========================
    # 2. NORMALIZATION
    # =========================
    print("── Step 2: Normalization ──")
    df, _, _ = run_normalization(df)
    print()

    # =========================
    # 3. STATISTICS
    # =========================
    print("── Step 3: Statistics ──")
    stats_report = run_descriptive(df)
    print()

    # =========================
    # 4. CLUSTERING
    # =========================
    print("── Step 4: KMeans ──")
    df, _ = run_kmeans(df, n_clusters=n_clusters, column="price_log")
    cluster_summary = get_cluster_summary(df)
    print()

    print("── Step 4b: DBSCAN ──")
    df, _ = run_dbscan(df, column="price_log")
    dbscan_outliers = get_dbscan_outliers(df)
    print()

    # =========================
    # 5. ANOMALY DETECTION
    # =========================
    print("── Step 5: Isolation Forest ──")
    df, _ = run_isolation_forest(df, column="price_log", contamination=contamination)
    anomaly_report = get_anomaly_report(df)
    print()

    print("── Step 5b: LOF ──")
    df, _ = run_lof(df, column="price_log")
    lof_outliers = get_lof_outliers(df)
    print()

    # =========================
    # 6. ASSOCIATION RULES
    # =========================
    association_report = {"apriori": [], "fpgrowth": []}

    if ASSOCIATION_AVAILABLE and "price_segment" in df.columns:
        print("── Step 6: Association Rules ──")

        _, rules_a = run_apriori(df)
        if not rules_a.empty:
            association_report["apriori"] = get_top_rules(rules_a)

        _, rules_f = run_fpgrowth(df)
        if not rules_f.empty:
            association_report["fpgrowth"] = get_top_rules(rules_f)

        print()

    # =========================
    # 7. PCA
    # =========================
    print("── Step 7: PCA ──")
    df, pca_model, explained = run_pca(df, n_components=2)
    pca_summary = get_pca_summary(pca_model, df.columns)
    print()

    # =========================
    # FINAL REPORT (SAFE)
    # =========================
    report = {
        "query": query,
        "total_products": int(len(df)),

        "statistics": safe(stats_report),
        "clusters": safe(cluster_summary),

        "anomalies": safe(anomaly_report),
        "lof_outliers": safe(lof_outliers),
        "dbscan_outliers": safe(dbscan_outliers),

        "association_rules": safe(association_report),
        "pca": safe(pca_summary),
    }

    print("=" * 60)
    print(f" PIPELINE COMPLETE — {len(df)} products")
    print(f" Anomalies: {len(anomaly_report)}")
    print(f" Clusters: {len(cluster_summary)}")
    print("=" * 60)

    # =========================
    # SAVE JSON
    # =========================
    if save_report:
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        filename = os.path.join(BASE_DIR, "data_mining_report.json")
        if query:
            filename = f"data_mining_report_{query.replace(' ', '_')}.json"

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"\n Report saved → {filename}")

    return report


# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    query = input("Filter by query (optional): ").strip() or None
    run_pipeline(query=query)