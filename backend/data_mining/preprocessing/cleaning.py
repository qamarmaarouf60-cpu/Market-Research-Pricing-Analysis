import pandas as pd
import re
 
 
def load_products_from_db():
    """Load all products from Django DB into a DataFrame."""
    from apps.products.models import Product
    qs = Product.objects.all().values(
        "id", "name", "price_text", "price_value", "source", "query", "url", "image_url"
    )
    df = pd.DataFrame(list(qs))
    return df
 
 
def clean_price(price_str):
    """Extract numeric value from price string."""
    if not price_str:
        return 0.0
    price_str = str(price_str).replace("\xa0", "").replace(" ", "")
    price_str = price_str.replace(",", ".")
    numbers = re.findall(r"[\d.]+", price_str)
    if numbers:
        try:
            return float(numbers[0])
        except ValueError:
            return 0.0
    return 0.0
 
 
def remove_duplicates(df):
    """Remove duplicate products based on URL."""
    before = len(df)
    df = df.drop_duplicates(subset=["url"], keep="first")
    after = len(df)
    print(f"[Cleaning] Removed {before - after} duplicates → {after} products remaining")
    return df
 
 
def remove_invalid_prices(df, min_price=1.0, max_price=500000.0):
    """Remove products with invalid or extreme prices."""
    before = len(df)
    df = df[df["price_value"] >= min_price]
    df = df[df["price_value"] <= max_price]
    after = len(df)
    print(f"[Cleaning] Removed {before - after} invalid prices → {after} products remaining")
    return df
 
 
def clean_names(df):
    """Clean product names."""
    df["name"] = df["name"].astype(str).str.strip()
    df["name"] = df["name"].str.replace(r"\s+", " ", regex=True)
    df = df[df["name"].str.len() >= 3]
    return df
 
 
def run_cleaning(query=None):
    """Full cleaning pipeline. Filter by query if provided."""
    print("[Cleaning] Loading products from DB...")
    df = load_products_from_db()
 
    if df.empty:
        print("[Cleaning] No products found in DB.")
        return df
 
    if query:
        df = df[df["query"].str.contains(query, case=False, na=False)]
        print(f"[Cleaning] Filtered to query '{query}' → {len(df)} products")
 
    df = remove_duplicates(df)
    df = remove_invalid_prices(df)
    df = clean_names(df)
 
    # Recompute price_value from price_text to ensure accuracy
    df["price_value"] = df["price_text"].apply(clean_price)
    df = df[df["price_value"] > 0]
 
    print(f"[Cleaning] Done. {len(df)} clean products ready.")
    return df.reset_index(drop=True)