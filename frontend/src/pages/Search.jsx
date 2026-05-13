import { useState, useEffect, useRef } from "react";
import { scrapeAndAnalyze, getJobStatus, globalSearch } from "../api/endpoints";

export default function Search() {
  const [query, setQuery] = useState("");
  const [mode, setMode] = useState("search");
  const [results, setResults] = useState(null);
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const pollRef = useRef(null);

  useEffect(() => () => clearInterval(pollRef.current), []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    setError(""); setResults(null); setJob(null); setLoading(true);
    try {
      if (mode === "scrape") {
        await scrapeAndAnalyze(query.trim());
        setJob({ status: "running", products_in_db: 0 });
        pollRef.current = setInterval(async () => {
          const { data } = await getJobStatus(query.trim());
          setJob(data);
          if (data.status === "idle") {
            clearInterval(pollRef.current);
            setLoading(false);
          }
        }, 2000);
      } else {
        const { data } = await globalSearch(query.trim());
        setResults(data);
        setLoading(false);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Erreur");
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Recherche</h1>
          <p className="page-sub">Recherchez ou scrapez un produit</p>
        </div>
      </div>

      <div className="card search-card">
        <div className="mode-toggle">
          <button className={mode === "search" ? "active" : ""} onClick={() => setMode("search")}>
            ◎ Recherche locale
          </button>
          <button className={mode === "scrape" ? "active" : ""} onClick={() => setMode("scrape")}>
            ⟳ Scraper + Analyser
          </button>
        </div>
        <form onSubmit={handleSubmit} className="search-form">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ex: iphone 13, laptop gaming..."
            className="search-input"
          />
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "..." : "→"}
          </button>
        </form>
        {mode === "scrape" && (
          <p className="scrape-info">
            Lance le scraping sur Amazon, eBay, Jumia, Avito puis le pipeline data mining.
          </p>
        )}
      </div>

      {error && <div className="error-banner">{error}</div>}

      {job && (
        <div className={`card job-status ${job.status}`}>
          <strong>{job.status === "running" ? "⟳ Scraping en cours..." : "✓ Terminé"}</strong>
          <p>Produits collectés : <strong>{job.products_in_db}</strong></p>
          {job.status === "idle" && job.products_in_db > 0 && (
            <p>✓ Allez sur <a href="/analytics">Analytics</a> pour analyser.</p>
          )}
        </div>
      )}

      {results && (
        <div className="results-section">
          <h3>{results.count} résultat(s) pour « {results.query} »</h3>
          {results.results.length === 0 ? (
            <p className="empty-msg">Aucun produit. Essayez le mode Scraper.</p>
          ) : (
            <div className="products-grid">
              {results.results.map((p) => (
                <div key={p.id} className="product-card">
                  {p.image_url && (
                    <img src={p.image_url} alt={p.name} onError={(e) => (e.target.style.display = "none")} />
                  )}
                  <span className="source-tag">{p.source}</span>
                  <p className="product-name">{p.name}</p>
                  <div className="product-footer">
                    <span className="product-price">{p.price_value?.toFixed(2)} MAD</span>
                    {p.url && <a href={p.url} target="_blank" rel="noopener noreferrer">Voir →</a>}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}