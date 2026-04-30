import pandas as pd
from mlxtend.frequent_patterns import fpgrowth, association_rules
from mlxtend.preprocessing import TransactionEncoder
from data_mining.association_rules.apriori import prepare_transactions


def run_fpgrowth(df, min_support=0.05, min_confidence=0.5, min_lift=1.0):
    """
    Run FP-Growth algorithm — faster alternative to Apriori for large datasets.
    Same output format as Apriori.
    """
    print(f"[FPGrowth] Building transactions...")
    transactions = prepare_transactions(df)

    if len(transactions) < 5:
        print(f"[FPGrowth] Not enough transactions ({len(transactions)}).")
        return pd.DataFrame(), pd.DataFrame()

    te = TransactionEncoder()
    te_array = te.fit_transform(transactions)
    te_df = pd.DataFrame(te_array, columns=te.columns_)

    print(f"[FPGrowth] Running with min_support={min_support}...")
    frequent_itemsets = fpgrowth(te_df, min_support=min_support, use_colnames=True)

    if frequent_itemsets.empty:
        print("[FPGrowth] No frequent itemsets found. Try lowering min_support.")
        return frequent_itemsets, pd.DataFrame()

    rules = association_rules(
        frequent_itemsets,
        metric="confidence",
        min_threshold=min_confidence
    )
    rules = rules[rules["lift"] >= min_lift]
    rules = rules.sort_values("lift", ascending=False)

    print(f"[FPGrowth] Found {len(frequent_itemsets)} itemsets, {len(rules)} rules")
    return frequent_itemsets, rules