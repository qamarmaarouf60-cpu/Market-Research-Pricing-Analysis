import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { register } from "../api/endpoints";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ username: "", password: "", email: "" });
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);

  const switchMode = (newMode) => {
    setMode(newMode);
    setError("");
    setSuccess("");
    setForm({ username: "", password: "", email: "" });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);
    try {
      if (mode === "register") {
        await register({ username: form.username, password: form.password, email: form.email });
        setSuccess("Compte créé avec succès ! Connectez-vous.");
        setMode("login");
        setForm({ username: form.username, password: "", email: "" });
        return;
      }
      await login(form.username, form.password);
      navigate("/");
    } catch (err) {
      setError(err.response?.data?.detail || (mode === "register" ? "Erreur lors de l'inscription" : "Identifiants invalides"));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-logo">⬡ PriceScope</div>
        <h1>{mode === "login" ? "Connexion" : "Créer un compte"}</h1>
        <p className="auth-subtitle">
          {mode === "login" ? "Accédez à vos analyses de marché" : "Rejoignez la plateforme"}
        </p>
        {error && <div className="auth-error">{error}</div>}
        {success && <div className="auth-success">{success}</div>}
        <form onSubmit={handleSubmit} className="auth-form">
          <div className="field">
            <label>Nom d'utilisateur</label>
            <input
              type="text"
              value={form.username}
              onChange={(e) => setForm({ ...form, username: e.target.value })}
              placeholder="votre_nom"
              required
            />
          </div>
          {mode === "register" && (
            <div className="field">
              <label>Email</label>
              <input
                type="email"
                value={form.email}
                onChange={(e) => setForm({ ...form, email: e.target.value })}
                placeholder="vous@email.com"
              />
            </div>
          )}
          <div className="field">
            <label>Mot de passe</label>
            <input
              type="password"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              placeholder="••••••••"
              required
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Chargement..." : mode === "login" ? "Se connecter" : "S'inscrire"}
          </button>
        </form>
        <p className="auth-switch">
          {mode === "login" ? "Pas de compte ?" : "Déjà un compte ?"}{" "}
          <button onClick={() => switchMode(mode === "login" ? "register" : "login")}>
            {mode === "login" ? "S'inscrire" : "Se connecter"}
          </button>
        </p>
      </div>
    </div>
  );
}