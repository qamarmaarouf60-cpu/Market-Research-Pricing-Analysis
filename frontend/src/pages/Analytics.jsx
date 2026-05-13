import { useState } from "react";
import { getDistribution, analyzeQuery, getAnalyticsStats } from "../api/endpoints";

export default function Analytics() {
  const [query, setQuery] = useState("");
  const [dist, setDist] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [statsData, setStatsData] = useState(null);
  const [loadingDist, setLoadingDist] = useState(false);
  const [loadingAnalyze, setLoadingAnalyze] = useState(false);
  const [error, setError] = useState("");

  const fetchDist = async () => {
    if (!query.trim()) return;
    setLoadingDist(true); setError("");
    try {
      const [d, s] = await Promise.all([getDistribution({ query }), getAnalyticsStats({ query })]);
      setDist(d.data); setStatsData(s.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Aucune donnée pour cette requête");
    } finally { setLoadingDist(false); }
  };

  const fetchAnalysis = async () => {
    if (!query.trim()) return;
    setLoadingAnalyze(true); setError("");
    try {
      const { data } = await analyzeQuery(query);
      setAnalysis(data);
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur pipeline");
    } finally { setLoadingAnalyze(false); }
  };

  const maxBucket = dist ? Math.max(...dist.buckets.map((b) => b.count)) : 0;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Analytics</h1>
          <p className="page-sub">Distribution des prix & pipeline data mining</p>
        </div>
      </div>

      <div className="card search-card">
        <input type="text" placeholder="Ex: iphone 13" value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchDist()}
          className="search-input" />
        <div className="analytics-actions">
          <button className="btn-primary" onClick={fetchDist} disabled={loadingDist}>
            {loadingDist ? "..." : "◈ Distribution"}
          </button>
          <button className="btn-secondary" onClick={fetchAnalysis} disabled={loadingAnalyze}>
            {loadingAnalyze ? "..." : "⬡ Pipeline complet"}
          </button>
        </div>
      </div>

      {error && <div className="error-banner">{error}</div>}

      {dist && (
        <div className="dashboard-grid">
          <div className="card">
            <h3>Statistiques descriptives</h3>
            {[
              ["Total", dist.total],
              ["Moyenne", `${dist.mean?.toFixed(2)} MAD`],
              ["Médiane", `${dist.median?.toFixed(2)} MAD`],
              ["Écart-type", `${dist.std?.toFixed(2)} MAD`],
              ["Min", `${dist.min?.toFixed(2)} MAD`],
              ["Max", `${dist.max?.toFixed(2)} MAD`],
            ].map(([l, v]) => (
              <div key={l} className="source-row">
                <span className="source-name">{l}</span>
                <span><strong>{v}</strong></span>
              </div>
            ))}
          </div>

          <div className="card">
            <h3>Distribution des prix</h3>
            <div className="histogram">
              {dist.buckets.map((b, i) => (
                <div key={i} className="histo-bar-wrap"
                  title={`${b.range_min}–${b.range_max} MAD : ${b.count}`}>
                  <div className="histo-bar"
                    style={{ height: `${maxBucket ? (b.count / maxBucket) * 100 : 0}%` }} />
                  <span className="histo-label">{Math.round(b.range_min / 1000)}k</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {statsData?.by_source?.length > 0 && (
        <div className="card">
          <h3>Par source — « {query} »</h3>
          <table className="data-table">
            <thead>
              <tr><th>Source</th><th>Produits</th><th>Moy.</th><th>Min</th><th>Max</th></tr>
            </thead>
            <tbody>
              {statsData.by_source.map((s) => (
                <tr key={s.source}>
                  <td><span className="source-tag">{s.source}</span></td>
                  <td>{s.total}</td>
                  <td>{s.avg_price?.toFixed(2)} MAD</td>
                  <td>{s.min_price?.toFixed(2)} MAD</td>
                  <td>{s.max_price?.toFixed(2)} MAD</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {analysis && (
        <>
          <div className="dashboard-grid">
            <div className="card">
              <h3>Clusters K-Means</h3>
              {analysis.clusters?.length > 0 ? analysis.clusters.map((c, i) => (
                <div key={i} className="cluster-item">
                  <strong>Cluster {c.cluster ?? i}</strong> — {c.size} produits
                  <p>Moy: {c.avg_price?.toFixed(2)} MAD | Min: {c.min_price?.toFixed(2)} | Max: {c.max_price?.toFixed(2)}</p>
                </div>
              )) : <p className="empty-msg">Pas assez de données.</p>}
            </div>

            <div className="card">
              <h3>Anomalies détectées</h3>
              {analysis.anomalies?.length > 0 ? analysis.anomalies.slice(0, 10).map((a, i) => (
                <div key={i} className="anomaly-item">
                  <span>⚠ </span>
                  <span>{a.name || "Produit"}</span>
                  <strong> — {p.price_value ? parseFloat(p.price_value).toFixed(2) : "—"} MAD</strong>
                </div>
              )) : <p className="empty-msg">Aucune anomalie.</p>}
            </div>
          </div>
        </>
      )}
    </div>
  );
}