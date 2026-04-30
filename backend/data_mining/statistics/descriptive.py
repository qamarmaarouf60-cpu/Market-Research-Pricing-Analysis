import pandas as pd
import numpy as np
from scipy import stats


def describe_prices(df, column="price_mad"):
    """Full descriptive statistics on price distribution."""
    if column not in df.columns or df.empty:
        return {}

    prices = df[column].dropna()

    q1 = float(prices.quantile(0.25))
    q3 = float(prices.quantile(0.75))
    iqr = q3 - q1

    skewness = float(prices.skew())
    kurt = float(prices.kurtosis())

    # Normality test (Shapiro-Wilk, max 5000 samples)
    sample = prices.sample(min(5000, len(prices)), random_state=42)
    _, p_value = stats.shapiro(sample) if len(sample) >= 3 else (None, None)

    return {
        "count": int(len(prices)),
        "mean": round(float(prices.mean()), 2),
        "median": round(float(prices.median()), 2),
        "std": round(float(prices.std()), 2),
        "min": round(float(prices.min()), 2),
        "max": round(float(prices.max()), 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "skewness": round(skewness, 4),
        "kurtosis": round(kurt, 4),
        "is_normal_distribution": bool(p_value and p_value > 0.05),
        "shapiro_p_value": round(float(p_value), 6) if p_value else None,
    }


def describe_by_source(df, column="price_mad"):
    """Descriptive statistics grouped by source."""
    if "source" not in df.columns or df.empty:
        return []

    result = []
    for source, group in df.groupby("source"):
        prices = group[column].dropna()
        if prices.empty:
            continue
        result.append({
            "source": source,
            "count": int(len(prices)),
            "mean": round(float(prices.mean()), 2),
            "median": round(float(prices.median()), 2),
            "std": round(float(prices.std()), 2),
            "min": round(float(prices.min()), 2),
            "max": round(float(prices.max()), 2),
        })
    return sorted(result, key=lambda x: x["count"], reverse=True)


def price_distribution_buckets(df, column="price_mad", n_buckets=10):
    """Return price distribution as histogram buckets."""
    if column not in df.columns or df.empty:
        return []

    prices = df[column].dropna()
    counts, bin_edges = np.histogram(prices, bins=n_buckets)

    buckets = []
    for i in range(len(counts)):
        buckets.append({
            "range_min": round(float(bin_edges[i]), 2),
            "range_max": round(float(bin_edges[i + 1]), 2),
            "count": int(counts[i]),
        })
    return buckets


def compare_sources(df, column="price_mad"):
    """
    Run statistical test (Mann-Whitney U) to compare price distributions
    between sources. Returns pairs with p-value.
    """
    if "source" not in df.columns:
        return []

    sources = df["source"].unique()
    results = []

    for i in range(len(sources)):
        for j in range(i + 1, len(sources)):
            s1, s2 = sources[i], sources[j]
            g1 = df[df["source"] == s1][column].dropna()
            g2 = df[df["source"] == s2][column].dropna()

            if len(g1) < 3 or len(g2) < 3:
                continue

            stat, p_value = stats.mannwhitneyu(g1, g2, alternative="two-sided")
            results.append({
                "source_1": s1,
                "source_2": s2,
                "median_1": round(float(g1.median()), 2),
                "median_2": round(float(g2.median()), 2),
                "p_value": round(float(p_value), 6),
                "significant_difference": bool(p_value < 0.05),
            })

    return results


def run_descriptive(df):
    """Run full descriptive statistics pipeline."""
    print("[Statistics] Running descriptive analysis...")

    overall = describe_prices(df)
    by_source = describe_by_source(df)
    distribution = price_distribution_buckets(df)
    source_comparison = compare_sources(df)

    print(f"[Statistics] Overall: mean={overall.get('mean')} MAD, median={overall.get('median')} MAD")
    print(f"[Statistics] Sources analyzed: {len(by_source)}")

    return {
        "overall": overall,
        "by_source": by_source,
        "distribution": distribution,
        "source_comparison": source_comparison,
    }