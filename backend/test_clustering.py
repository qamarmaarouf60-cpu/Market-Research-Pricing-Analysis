import pandas as pd

from data_mining.preprocessing.cleaning import clean_price, remove_duplicates, remove_invalid_prices, clean_names
from data_mining.preprocessing.normalization import run_normalization

from data_mining.clustering.kmeans import run_kmeans, get_cluster_summary
from data_mining.clustering.dbscan import run_dbscan, get_dbscan_outliers


def test_clustering():
    print("=== START CLUSTERING TEST ===")

    # 🔹 Fake dataset (important: diverse prices)
    data = [
        {"name": "Cheap 1", "price_text": "100 DH", "price_value": 100, "url": "a", "source": "site1"},
        {"name": "Cheap 2", "price_text": "120 DH", "price_value": 120, "url": "b", "source": "site1"},
        {"name": "Mid 1", "price_text": "1000 DH", "price_value": 1000, "url": "c", "source": "site2"},
        {"name": "Mid 2", "price_text": "1200 DH", "price_value": 1200, "url": "d", "source": "site2"},
        {"name": "High 1", "price_text": "10000 DH", "price_value": 10000, "url": "e", "source": "site3"},
        {"name": "High 2", "price_text": "12000 DH", "price_value": 12000, "url": "f", "source": "site3"},
        {"name": "Outlier", "price_text": "99999 DH", "price_value": 99999, "url": "g", "source": "siteX"},
    ]

    df = pd.DataFrame(data)

    print("\nOriginal Data:")
    print(df)

    # 🔹 CLEANING
    df["price_value"] = df["price_text"].apply(clean_price)
    df = remove_duplicates(df)
    df = remove_invalid_prices(df)
    df = clean_names(df)

    # 🔹 NORMALIZATION (needed for clustering)
    df, _, _ = run_normalization(df)

    print("\nAfter Normalization:")
    print(df[["name", "price_mad", "price_log"]])

    # 🔹 KMEANS
    df_kmeans, km_model = run_kmeans(df, auto_k=True)

    print("\nKMeans Result:")
    print(df_kmeans[["name", "price_mad", "cluster", "price_segment"]])

    summary = get_cluster_summary(df_kmeans)
    print("\nKMeans Summary:")
    print(summary)

    # 🔹 DBSCAN
    df_dbscan, db_model = run_dbscan(df)

    print("\nDBSCAN Result:")
    print(df_dbscan[["name", "price_mad", "dbscan_cluster", "dbscan_label"]])

    outliers = get_dbscan_outliers(df_dbscan)
    print("\nDetected Outliers:")
    print(outliers)

    # ✅ Assertions
    assert "cluster" in df_kmeans.columns
    assert "price_segment" in df_kmeans.columns
    assert "dbscan_cluster" in df_dbscan.columns

    print("\n✅ CLUSTERING TEST PASSED")


# 🔥 Run test
if __name__ == "__main__":
    test_clustering()