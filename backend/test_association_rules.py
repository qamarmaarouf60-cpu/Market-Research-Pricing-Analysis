import pandas as pd

from data_mining.association_rules.apriori import run_apriori, get_top_rules
from data_mining.association_rules.fpgrowth import run_fpgrowth


def test_association_rules():
    print("=== START ASSOCIATION RULES TEST ===")

    # 🔹 Fake dataset
    data = [
        {"name": "Phone A", "price_mad": 100, "source": "amazon", "query": "phone cheap"},
        {"name": "Phone B", "price_mad": 150, "source": "amazon", "query": "phone cheap"},
        {"name": "Phone C", "price_mad": 1200, "source": "jumia", "query": "phone premium"},
        {"name": "Laptop A", "price_mad": 5000, "source": "amazon", "query": "laptop gaming"},
        {"name": "Laptop B", "price_mad": 7000, "source": "jumia", "query": "laptop gaming"},
        {"name": "Watch", "price_mad": 200, "source": "amazon", "query": "watch cheap"},
        {"name": "TV", "price_mad": 12000, "source": "jumia", "query": "tv premium"},
    ]

    df = pd.DataFrame(data)

    print("\nOriginal Data:")
    print(df)

    # =========================
    # 🔥 APRIORI TEST
    # =========================
    itemsets, rules = run_apriori(df, min_support=0.2, min_confidence=0.5)

    print("\nApriori Itemsets:")
    print(itemsets)

    print("\nApriori Rules:")
    print(rules)

    top_rules = get_top_rules(rules, n=5)
    print("\nTop Apriori Rules:")
    print(top_rules)

    # =========================
    # 🔥 FP-GROWTH TEST
    # =========================
    itemsets_fp, rules_fp = run_fpgrowth(df, min_support=0.2, min_confidence=0.5)

    print("\nFP-Growth Itemsets:")
    print(itemsets_fp)

    print("\nFP-Growth Rules:")
    print(rules_fp)

    # =========================
    # ASSERTIONS
    # =========================
    assert isinstance(itemsets, pd.DataFrame)
    assert isinstance(rules, pd.DataFrame)

    print("\n✅ ASSOCIATION RULES TEST PASSED")


# 🔥 RUN TEST
if __name__ == "__main__":
    test_association_rules()