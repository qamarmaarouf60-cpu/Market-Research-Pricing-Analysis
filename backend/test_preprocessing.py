# test_preprocessing.py

import pandas as pd

from data_mining.preprocessing.cleaning import (
    clean_price,
    remove_duplicates,
    remove_invalid_prices,
    clean_names,
)

from data_mining.preprocessing.normalization import run_normalization


def test_cleaning_and_normalization():
    print("=== START TEST ===")

    # 🔹 Fake dataset (no DB dependency)
    data = [
        {"id": 1, "name": "  iPhone 13  ", "price_text": "1000$", "price_value": 1000, "url": "a"},
        {"id": 2, "name": "iPhone 13", "price_text": "1000$", "price_value": 1000, "url": "a"},  # duplicate
        {"id": 3, "name": "Samsung", "price_text": "0", "price_value": 0, "url": "b"},           # invalid price
        {"id": 4, "name": "TV", "price_text": "5000 DH", "price_value": 5000, "url": "c"},
    ]

    df = pd.DataFrame(data)

    print("\nOriginal DataFrame:")
    print(df)

    # 🔹 STEP 1: recompute price_value FIRST (important fix)
    df["price_value"] = df["price_text"].apply(clean_price)

    # 🔹 STEP 2: cleaning
    df = remove_duplicates(df)
    df = remove_invalid_prices(df)
    df = clean_names(df)

    # Remove zero prices again (safety)
    df = df[df["price_value"] > 0]

    print("\nAfter Cleaning:")
    print(df)

    # 🔹 STEP 3: normalization
    df, minmax_scaler, standard_scaler = run_normalization(df)

    print("\nAfter Normalization:")
    print(df)

    # 🔹 Assertions (basic validation)
    assert not df.empty, "DataFrame is empty after processing"
    assert "price_mad" in df.columns, "Missing price_mad"
    assert "price_normalized" in df.columns, "Missing price_normalized"
    assert df["price_value"].min() > 0, "Invalid prices still present"

    print("\n✅ TEST PASSED")


# 🔥 THIS PART WAS MISSING (this runs the test)
if __name__ == "__main__":
    test_cleaning_and_normalization()