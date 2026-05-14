import { useEffect, useState } from "react";
import { getProducts, getSources } from "../api/endpoints";

export default function Products() {
  const [data, setData] = useState(null);
  const [sources, setSources] = useState([]);
  const [filters, setFilters] = useState({
    source: "", search: "", min_price: "", max_price: "",
    ordering: "-created_at", page: 1, page_size: 20,
  });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSources().then((r) => setSources(r.data)).catch(console.error);
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== ""));
    getProducts(params).then((r) => setData(r.data)).catch(console.error).finally(() => setLoading(false));
  }, [filters]);

  const set = (key, val) => setFilters((f) => ({ ...f, [key]: val, page: 1 }));

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Produits</h1>
          <p className="page-sub">{data ? `${data.total?.toLocaleString()} produits` : "Chargement..."}</p>
        </div>
      </div>

      <div className="card filters-bar">
        <input type="text" placeholder="Rechercher..." value={filters.search}
          onChange={(e) => set("search", e.target.value)} className="filter-input" />
        <select value={filters.source} onChange={(e) => set("source", e.target.value)} className="filter-select">
          <option value="">Toutes les sources</option>
          {sources.map((s) => <option key={s.source} value={s.source}>{s.source} ({s.count})</option>)}
        </select>
        <input type="number" placeholder="Prix min" value={filters.min_price}
          onChange={(e) => set("min_price", e.target.value)} className="filter-input filter-price" />
        <input type="number" placeholder="Prix max" value={filters.max_price}
          onChange={(e) => set("max_price", e.target.value)} className="filter-input filter-price" />
        <select value={filters.ordering} onChange={(e) => set("ordering", e.target.value)} className="filter-select">
          <option value="-created_at">Plus récents</option>
          <option value="price_value">Prix ↑</option>
          <option value="-price_value">Prix ↓</option>
          <option value="name">Nom A–Z</option>
        </select>
        <button className="btn-ghost" onClick={() => setFilters({ source: "", search: "", min_price: "",
          max_price: "", ordering: "-created_at", page: 1, page_size: 20 })}>Reset</button>
      </div>

      <div className="card table-card">
        {loading ? <p>Chargement...</p> : data?.results?.length === 0 ? (
          <p className="empty-msg">Aucun produit trouvé.</p>
        ) : (
          <table className="data-table">
            <thead>
              <tr><th>Image</th><th>Nom</th><th>Source</th><th>Prix</th><th>Catégorie</th><th>Lien</th></tr>
            </thead>
            <tbody>
              {data?.results?.map((p) => (
                <tr key={p.id}>
                  <td className="td-img">
                    {p.image_url
                      ? <img src={p.image_url} alt="" onError={(e) => (e.target.style.display = "none")} />
                      : <span>▦</span>}
                  </td>
                  <td className="td-name">{p.name}</td>
                  <td><span className="source-tag">{p.source}</span></td>
                  <td>{p.price_value ? parseFloat(p.price_value).toFixed(2) : "—"} MAD</td>
                  <td><span className="cat-badge">{p.price_category}</span></td>
                  <td>{p.url && <a href={p.url} target="_blank" rel="noopener noreferrer">Voir →</a>}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {data?.pages > 1 && (
          <div className="pagination">
            <button onClick={() => setFilters((f) => ({ ...f, page: f.page - 1 }))}
              disabled={filters.page <= 1}>‹</button>
            <span>Page {filters.page} / {data.pages}</span>
            <button onClick={() => setFilters((f) => ({ ...f, page: f.page + 1 }))}
              disabled={filters.page >= data.pages}>›</button>
          </div>
        )}
      </div>
    </div>
  );
}