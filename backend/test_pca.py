import pandas as pd

from data_mining.preprocessing.cleaning import clean_price, remove_duplicates, remove_invalid_prices, clean_names
from data_mining.preprocessing.normalization import run_normalization

from data_mining.dimensionality_reduction.pca import run_pca, get_pca_summary, prepare_features 


def test_pca():
    print("=== START PCA TEST ===")

    # 🔹 dataset
    data = [
        {"name": "Cheap", "price_text": "10 DH", "price_value": 10, "url": "a", "source": "amazon"},
        {"name": "Cheap2", "price_text": "20 DH", "price_value": 20, "url": "b", "source": "amazon"},
        {"name": "Mid", "price_text": "500 DH", "price_value": 500, "url": "c", "source": "jumia"},
        {"name": "Mid2", "price_text": "700 DH", "price_value": 700, "url": "d", "source": "jumia"},
        {"name": "High", "price_text": "5000 DH", "price_value": 5000, "url": "e", "source": "amazon"},
        {"name": "Luxury", "price_text": "10000 DH", "price_value": 10000, "url": "f", "source": "noon"},
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
    # 🔹 PCA
    # =========================
    df, pca_model, explained = run_pca(df, n_components=2)

    print("\nPCA Results:")
    print(df[["name", "pca_1", "pca_2"]])

    print("\nExplained variance:")
    print(explained)

    # =========================
    # 🔹 PCA SUMMARY
    # =========================
    if pca_model is not None:
        feature_df, feature_names = prepare_features(df)
        summary = get_pca_summary(pca_model, feature_names)

        print("\nPCA Feature Contribution:")
        print(summary)

    # =========================
    # ASSERTIONS
    # =========================
    assert "pca_1" in df.columns
    assert "pca_2" in df.columns

    print("\n✅ PCA TEST PASSED")


# 🔥 RUN
if __name__ == "__main__":
    test_pca()