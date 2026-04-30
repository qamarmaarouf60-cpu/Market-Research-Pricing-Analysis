import pandas as pd

from data_mining.statistics.descriptive import run_descriptive


def test_statistics():
    print("=== START STATISTICS TEST ===")

    # 🔹 fake dataset
    data = [
        {"name": "A", "price_mad": 10, "source": "amazon"},
        {"name": "B", "price_mad": 20, "source": "amazon"},
        {"name": "C", "price_mad": 500, "source": "jumia"},
        {"name": "D", "price_mad": 700, "source": "jumia"},
        {"name": "E", "price_mad": 5000, "source": "noon"},
        {"name": "F", "price_mad": 10000, "source": "noon"},
    ]

    df = pd.DataFrame(data)

    print("\nInput Data:")
    print(df)

    # =========================
    # RUN STATS PIPELINE
    # =========================
    result = run_descriptive(df)

    print("\n=== OVERALL STATS ===")
    print(result["overall"])

    print("\n=== BY SOURCE ===")
    print(result["by_source"])

    print("\n=== DISTRIBUTION ===")
    print(result["distribution"])

    print("\n=== SOURCE COMPARISON ===")
    print(result["source_comparison"])

    # =========================
    # BASIC ASSERTIONS
    # =========================
    assert "overall" in result
    assert "by_source" in result
    assert "distribution" in result
    assert "source_comparison" in result

    print("\n✅ STATISTICS TEST PASSED")


if __name__ == "__main__":
    test_statistics()