import pandas as pd
from mlxtend.frequent_patterns import apriori, association_rules
from mlxtend.preprocessing import TransactionEncoder


def prepare_transactions(df, min_price_segments=True):
    """
    Build transaction dataset from products.
    Each transaction = [source, price_segment, query_keyword]
    """
    transactions = []

    for _, row in df.iterrows():
        transaction = []

        # Add source
        if row.get("source"):
            transaction.append(f"source_{row['source']}")

        # Add price segment
        if row.get("price_segment"):
            transaction.append(f"segment_{row['price_segment'].replace(' ', '_')}")

        # Add query keywords (first word only to avoid sparsity)
        if row.get("query"):
            keyword = str(row["query"]).split()[0].lower()
            transaction.append(f"query_{keyword}")

        # Add price range bucket
        price = row.get("price_mad", 0)
        if price < 500:
            transaction.append("price_range_low")
        elif price < 2000:
            transaction.append("price_range_mid")
        elif price < 10000:
            transaction.append("price_range_high")
        else:
            transaction.append("price_range_premium")

        if len(transaction) >= 2:
            transactions.append(transaction)

    return transactions


def run_apriori(df, min_support=0.05, min_confidence=0.5, min_lift=1.0):
    """
    Run Apriori algorithm to find association rules between
    product source, price segment, and query keywords.
    """
    print(f"[Apriori] Building transactions...")
    transactions = prepare_transactions(df)

    if len(transactions) < 5:
        print(f"[Apriori] Not enough transactions ({len(transactions)}).")
        return pd.DataFrame(), pd.DataFrame()

    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    te_df = pd.DataFrame(te_array, columns=te.columns_)

    print(f"[Apriori] Running with min_support={min_support}...")
    frequent_itemsets = apriori(te_df, min_support=min_support, use_colnames=True)

    if frequent_itemsets.empty:
        print("[Apriori] No frequent itemsets found. Try lowering min_support.")
        return frequent_itemsets, pd.DataFrame()

    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=min_confidence
    )
    rules = rules[rules["lift"] >= min_lift]
    rules = rules.sort_values("lift", ascending=False)

    print(f"[Apriori] Found {len(frequent_itemsets)} itemsets, {len(rules)} rules")
    return frequent_itemsets, rules


def get_top_rules(rules, n=10):
    """Return top N rules as a clean list of dicts."""
    if rules.empty:
        return []

    result = []
    for _, row in rules.head(n).iterrows():
        result.append({
            "antecedents": list(row["antecedents"]),
            "consequents": list(row["consequents"]),
            "support": round(float(row["support"]), 4),
            "confidence": round(float(row["confidence"]), 4),
            "lift": round(float(row["lift"]), 4),
        })
    return result