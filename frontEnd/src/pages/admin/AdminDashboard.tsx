import { Link } from "react-router-dom";

const NAV_CARDS = [
  {
    to: "/admin/requests",
    icon: "📋",
    title: "Access Requests",
    desc: "Review pending requests and create user accounts for new staff.",
  },
  {
    to: "/admin/users",
    icon: "👥",
    title: "Users",
    desc: "Edit staff details, reset passwords, or remove access when employees leave.",
  },
];

function AdminDashboard() {
  const name = localStorage.getItem("userId") ?? "Admin";

  return (
    <div className="admin-page">
      <p className="admin-page-sub" style={{ marginBottom: "0.25rem", fontFamily: "var(--font-mono)", fontSize: "0.8rem" }}>
        Signed in as <span style={{ color: "var(--primary)" }}>{name}</span>
      </p>
      <h1 className="admin-page-title">Admin Dashboard</h1>
      <p className="admin-page-sub">Manage staff access and system settings.</p>

      <div className="admin-nav-grid">
        {NAV_CARDS.map((card) => (
          <Link key={card.to} to={card.to} className="admin-nav-card">
            <span className="admin-nav-icon">{card.icon}</span>
            <div>
              <p className="admin-nav-title">{card.title}</p>
              <p className="admin-nav-desc">{card.desc}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}

export default AdminDashboard;
