import { useEffect, useState } from "react";
import { getProductStats, getAnalyticsStats, getSources } from "../api/endpoints";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [analyticsStats, setAnalyticsStats] = useState(null);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    Promise.all([getProductStats(), getAnalyticsStats(), getSources()])
      .then(([ps, as_, sr]) => {
        setStats(ps.data);
        setAnalyticsStats(as_.data);
        setSources(sr.data);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  const maxCount = sources.reduce((m, s) => Math.max(m, s.count), 0);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Dashboard</h1>
          <p className="page-sub">Vue d'ensemble du marché</p>
        </div>
        <button className="btn-primary" onClick={() => navigate("/search")}>
          + Nouvelle analyse
        </button>
      </div>

      {loading ? (
        <p>Chargement...</p>
      ) : (
        <>
          <div className="stats-grid">
            {[
              { label: "Produits scrapés", value: stats?.total?.toLocaleString() },
              { label: "Prix moyen", value: `${stats?.avg_price?.toFixed(2)} MAD` },
              { label: "Prix min", value: `${stats?.min_price?.toFixed(2)} MAD` },
              { label: "Prix max", value: `${stats?.max_price?.toFixed(2)} MAD` },
            ].map(({ label, value }) => (
              <div key={label} className="stat-card">
                <span className="stat-label">{label}</span>
                <span className="stat-value">{value ?? "—"}</span>
              </div>
            ))}
          </div>

          <div className="dashboard-grid">
            <div className="card">
              <h3>Répartition par source</h3>
              {sources.length === 0 ? (
                <p className="empty-msg">Aucune donnée. Lancez une recherche.</p>
              ) : (
                sources.map((s) => (
                  <div key={s.source} className="source-row">
                    <span className="source-name">{s.source}</span>
                    <div className="source-bar-wrap">
                      <div
                        className="source-bar"
                        style={{ width: `${maxCount ? (s.count / maxCount) * 100 : 0}%` }}
                      />
                    </div>
                    <span className="source-count">{s.count}</span>
                  </div>
                ))
              )}
            </div>

            <div className="card">
              <h3>Gammes de prix</h3>
              {stats?.by_category ? (
                Object.entries(stats.by_category).map(([cat, count]) => (
                  <div key={cat} className="source-row">
                    <span className="source-name">{cat}</span>
                    <div className="source-bar-wrap">
                      <div
                        className="source-bar"
                        style={{ width: `${stats.total ? (count / stats.total) * 100 : 0}%` }}
                      />
                    </div>
                    <span className="source-count">{count}</span>
                  </div>
                ))
              ) : (
                <p className="empty-msg">Aucune donnée.</p>
              )}
            </div>
          </div>

          {analyticsStats?.by_source?.length > 0 && (
            <div className="card">
              <h3>Comparaison des marketplaces</h3>
              <table className="data-table">
                <thead>
                  <tr>
                    <th>Source</th><th>Produits</th><th>Prix moyen</th><th>Min</th><th>Max</th>
                  </tr>
                </thead>
                <tbody>
                  {analyticsStats.by_source.map((s) => (
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
        </>
      )}
    </div>
  );
}