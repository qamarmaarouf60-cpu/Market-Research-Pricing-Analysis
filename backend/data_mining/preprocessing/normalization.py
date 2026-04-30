import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
 
 
# Approximate conversion rates to MAD (Moroccan Dirham)
CONVERSION_RATES = {
    "USD": 10.0,   # 1 USD ≈ 10 MAD
    "EUR": 11.0,   # 1 EUR ≈ 11 MAD
    "GBP": 13.0,   # 1 GBP ≈ 13 MAD
    "MAD": 1.0,
    "DH":  1.0,
    "DHS": 1.0,
}
 
 
def detect_currency(price_text):
    """Detect currency from price string."""
    if not price_text:
        return "MAD"
    price_upper = str(price_text).upper()
    if "$" in price_upper or "USD" in price_upper:
        return "USD"
    if "€" in price_upper or "EUR" in price_upper:
        return "EUR"
    if "£" in price_upper or "GBP" in price_upper:
        return "GBP"
    return "MAD"
 
 
def convert_to_mad(df):
    """Convert all prices to MAD."""
    def convert_row(row):
        currency = detect_currency(row.get("price_text", ""))
        rate = CONVERSION_RATES.get(currency, 1.0)
        return row["price_value"] * rate
 
    df["price_mad"] = df.apply(convert_row, axis=1)
    print(f"[Normalization] Converted all prices to MAD.")
    return df
 
 
def normalize_minmax(df, column="price_mad"):
    """Normalize prices to [0, 1] range using MinMax scaling."""
    scaler = MinMaxScaler()
    df["price_normalized"] = scaler.fit_transform(df[[column]])
    print(f"[Normalization] MinMax normalization applied on '{column}'.")
    return df, scaler
 
 
def normalize_standard(df, column="price_mad"):
    """Standardize prices (mean=0, std=1) using Standard scaling."""
    scaler = StandardScaler()
    df["price_standardized"] = scaler.fit_transform(df[[column]])
    print(f"[Normalization] Standard normalization applied on '{column}'.")
    return df, scaler
 
 
def log_transform(df, column="price_mad"):
    """Apply log transformation to handle skewed price distributions."""
    df["price_log"] = np.log1p(df[column])
    print(f"[Normalization] Log transformation applied on '{column}'.")
    return df
 
 
def run_normalization(df):
    """Full normalization pipeline."""
    print("[Normalization] Starting normalization...")
 
    df = convert_to_mad(df)
    df = log_transform(df)
    df, minmax_scaler = normalize_minmax(df)
    df, standard_scaler = normalize_standard(df)
 
    print(f"[Normalization] Done. Columns added: price_mad, price_log, price_normalized, price_standardized")
    return df, minmax_scaler, standard_scaler