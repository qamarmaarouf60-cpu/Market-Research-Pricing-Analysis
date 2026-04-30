import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


def prepare_features(df):
    """
    Build feature matrix from product data for PCA.
    Features: price_mad, price_log, price_normalized + one-hot source
    """
    features = []

    # Numeric price features
    numeric_cols = ["price_mad", "price_log", "price_normalized"]
    available = [c for c in numeric_cols if c in df.columns]

    if not available:
        print("[PCA] No numeric price columns found. Run normalization first.")
        return None, []

    feature_df = df[available].copy()

    # One-hot encode source
    if "source" in df.columns:
        source_dummies = pd.get_dummies(df["source"], prefix="source")
        feature_df = pd.concat([feature_df, source_dummies], axis=1)

    feature_df = feature_df.fillna(0)
    return feature_df, list(feature_df.columns)


def run_pca(df, n_components=2):
    """
    Apply PCA to reduce product feature space.
    Useful for visualization and understanding price variance.
    Returns df with pca_1, pca_2 columns added.
    """
    print(f"[PCA] Starting dimensionality reduction to {n_components} components...")

    feature_df, feature_names = prepare_features(df)
    if feature_df is None or feature_df.empty:
        return df, None, []

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(feature_df)

    n_components = min(n_components, X_scaled.shape[1], X_scaled.shape[0])
    pca = PCA(n_components=n_components, random_state=42)
    components = pca.fit_transform(X_scaled)

    df = df.copy()
    for i in range(n_components):
        df[f"pca_{i+1}"] = components[:, i]

    explained = pca.explained_variance_ratio_
    print(f"[PCA] Explained variance: {[round(float(v)*100, 2) for v in explained]}%")
    print(f"[PCA] Total variance explained: {round(float(sum(explained))*100, 2)}%")

    return df, pca, explained


def get_pca_summary(pca, feature_names):
    """Return which features contribute most to each component."""
    summary = []
    for i, component in enumerate(pca.components_):
        top_features = sorted(
            zip(feature_names, component),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:3]
        summary.append({
            "component": f"PCA_{i+1}",
            "explained_variance_pct": round(float(pca.explained_variance_ratio_[i]) * 100, 2),
            "top_features": [{"feature": f, "weight": round(float(w), 4)} for f, w in top_features]
        })
    return summary