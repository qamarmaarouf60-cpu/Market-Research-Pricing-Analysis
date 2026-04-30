import pandas as pd

from data_mining.preprocessing.cleaning import (
    clean_price,
    remove_duplicates,
    remove_invalid_prices,
    clean_names,
)

from data_mining.preprocessing.normalization import run_normalization

from data_mining.anomaly_detection.lof import run_lof, get_lof_outliers
from data_mining.anomaly_detection.isolation_forest import (
    run_isolation_forest,
    get_anomaly_report
)


def test_anomaly_detection():
    print("=== START ANOMALY TEST ===")

    # 🔹 Fake dataset with clear outliers
    data = [
        {"name": "Cheap 1", "price_text": "10 DH", "price_value": 10, "url": "a", "source": "s1"},
        {"name": "Cheap 2", "price_text": "15 DH", "price_value": 15, "url": "b", "source": "s1"},
        {"name": "Normal 1", "price_text": "500 DH", "price_value": 500, "url": "c", "source": "s2"},
        {"name": "Normal 2", "price_text": "600 DH", "price_value": 600, "url": "d", "source": "s2"},
        {"name": "Expensive", "price_text": "1000 DH", "price_value": 1000, "url": "e", "source": "s3"},
        {"name": "Luxury", "price_text": "2000 DH", "price_value": 2000, "url": "f", "source": "s3"},
        {"name": "FAKE SCAM", "price_text": "99999 DH", "price_value": 99999, "url": "g", "source": "scam"},
    ]

    df = pd.DataFrame(data)

    print("\nOriginal Data:")
    print(df)

    # =========================
    # 🔹 CLEANING
    # =========================
    df["price_value"] = df["price_text"].apply(clean_price)
    df = remove_duplicates(df)
    df = remove_invalid_prices(df)
    df = clean_names(df)

    # =========================
    # 🔹 NORMALIZATION
    # =========================
    df, _, _ = run_normalization(df)

    print("\nAfter normalization:")
    print(df[["name", "price_mad", "price_log"]])

    # =========================
    # 🔹 LOF (Local Outlier Factor)
    # =========================
    df_lof, lof_model = run_lof(df)

    print("\nLOF results:")
    print(df_lof[["name", "price_mad", "lof_anomaly", "lof_factor"]])

    lof_outliers = get_lof_outliers(df_lof)
    print("\nLOF Outliers:")
    print(lof_outliers)

    # =========================
    # 🔹 ISOLATION FOREST
    # =========================
    df_iso, iso_model = run_isolation_forest(df)

    print("\nIsolation Forest results:")

    # 🔥 SAFE CHECK (prevents crash if skipped)
    if df_iso is not None and "is_anomaly" in df_iso.columns:
        print(df_iso[["name", "price_mad", "is_anomaly", "anomaly_confidence"]])

        iso_report = get_anomaly_report(df_iso)
        print("\nIsolation Forest Report:")
        print(iso_report)

    else:
        print("[IsolationForest] Skipped (not enough data or model not run)")

    # =========================
    # 🔹 ASSERTIONS
    # =========================
    assert "lof_anomaly" in df_lof.columns, "LOF failed"
    assert "lof_factor" in df_lof.columns, "LOF missing factor"

    print("\n✅ ANOMALY TEST PASSED")


# 🔥 RUN TEST
if __name__ == "__main__":
    test_anomaly_detection()