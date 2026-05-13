import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const navItems = [
  { to: "/", icon: "⬡", label: "Dashboard" },
  { to: "/search", icon: "◎", label: "Recherche" },
  { to: "/products", icon: "▦", label: "Produits" },
  { to: "/analytics", icon: "◈", label: "Analytics" },
  { to: "/history", icon: "◷", label: "Historique" },
];

export default function Sidebar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <span>⬡</span>
        <span>PriceScope</span>
      </div>
      <nav className="sidebar-nav">
        {navItems.map(({ to, icon, label }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) => `nav-item ${isActive ? "active" : ""}`}
          >
            <span className="nav-icon">{icon}</span>
            <span className="nav-label">{label}</span>
          </NavLink>
        ))}
      </nav>
      <div className="sidebar-footer">
        <div className="user-info">
          <div className="user-avatar">{user?.username?.[0]?.toUpperCase() || "U"}</div>
          <div>
            <p className="user-name">{user?.username || "Utilisateur"}</p>
            <p className="user-role">Analyste</p>
          </div>
        </div>
        <button onClick={handleLogout} className="logout-btn">⏻</button>
      </div>
    </aside>
  );
}