import { useEffect, useState } from "react";
import { getSearchHistory } from "../api/endpoints";

export default function History() {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    getSearchHistory()
      .then((r) => setHistory(r.data))
      .catch((err) => setError(err.response?.data?.detail || "Erreur"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>Historique</h1>
          <p className="page-sub">Vos recherches passées</p>
        </div>
      </div>
      <div className="card table-card">
        {loading ? <p>Chargement...</p> : error ? (
          <p className="error-banner">{error}</p>
        ) : history.length === 0 ? (
          <p className="empty-msg">Aucune recherche enregistrée.</p>
        ) : (
          <table className="data-table">
            <thead><tr><th>#</th><th>Requête</th><th>Date</th></tr></thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={h.id}>
                  <td>{i + 1}</td>
                  <td><strong>{h.query}</strong></td>
                  <td>{new Date(h.created_at).toLocaleString("fr-FR")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}