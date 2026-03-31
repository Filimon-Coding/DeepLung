import { Link } from "react-router-dom";
import { useEffect, useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { fetchAdminStats, type AdminStats } from "../../api/admin";

// ── SVG Icons ────────────────────────────────────────────────────────────────

function IconAccessRequests() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M9 12h6M9 16h4M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
      <polyline points="14 3 14 8 20 8" />
      <circle cx="16.5" cy="17.5" r="2.5" />
      <path d="M18.5 19.5 20 21" />
    </svg>
  );
}

function IconMonitor() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="3" width="20" height="14" rx="2" ry="2" />
      <line x1="8" y1="21" x2="16" y2="21" />
      <line x1="12" y1="17" x2="12" y2="21" />
      <polyline points="6 9 10 13 14 9 18 13" />
    </svg>
  );
}

function IconUsers() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="9" cy="7" r="3" />
      <path d="M3 21v-2a4 4 0 0 1 4-4h4a4 4 0 0 1 4 4v2" />
      <circle cx="18" cy="7" r="2.5" />
      <path d="M22 21v-1.5a3.5 3.5 0 0 0-2.5-3.36" />
    </svg>
  );
}

function IconCalendar() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2" />
      <line x1="16" y1="2" x2="16" y2="6" />
      <line x1="8" y1="2" x2="8" y2="6" />
      <line x1="3" y1="10" x2="21" y2="10" />
    </svg>
  );
}

// ── Nav cards config ─────────────────────────────────────────────────────────

const NAV_CARDS = [
  {
    to: "/admin/requests",
    Icon: IconAccessRequests,
    title: "Access Requests",
    desc: "Review pending requests and create user accounts for new staff.",
    accent: "var(--primary)",
    accentBg: "var(--primary-dim)",
  },
  {
    to: "/admin/users",
    Icon: IconUsers,
    title: "Users",
    desc: "Edit staff details, reset passwords, or remove access when employees leave.",
    accent: "#3b82f6",
    accentBg: "rgba(59,130,246,0.1)",
  },
  {
    to: "/admin/monitor",
    Icon: IconMonitor,
    title: "System Monitor",
    desc: "View service health status and a full log of analysis activity.",
    accent: "#8b5cf6",
    accentBg: "rgba(139,92,246,0.1)",
  },
];

// ── Helpers ──────────────────────────────────────────────────────────────────

function toInputDate(d: Date) {
  return d.toISOString().slice(0, 10);
}

// ── Component ────────────────────────────────────────────────────────────────

function AdminDashboard() {
  const name = localStorage.getItem("userId") ?? "Admin";
  const today = toInputDate(new Date());

  const [fromDate, setFromDate] = useState(() =>
    toInputDate(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000))
  );
  const [toDate, setToDate] = useState(today);

  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    fetchAdminStats(fromDate, toDate)
      .then(setStats)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, [fromDate, toDate]);

  const pctBenign =
    stats && stats.total > 0
      ? Math.round((stats.benign / stats.total) * 100)
      : 0;
  const pctMalignant =
    stats && stats.total > 0
      ? Math.round((stats.malignant / stats.total) * 100)
      : 0;

  return (
    <div className="admin-page">

      {/* ── Page header ─────────────────────────────────────── */}
      <div className="dash-header">
        <div>
          <p className="dash-eyebrow">
            Signed in as <span className="dash-eyebrow-name">{name}</span>
          </p>
          <h1 className="dash-title">Admin Dashboard</h1>
          <p className="dash-subtitle">Manage staff access and monitor system activity.</p>
        </div>
      </div>

      {/* ── Quick-nav cards ──────────────────────────────────── */}
      <div className="dash-nav-grid">
        {NAV_CARDS.map((card) => (
          <Link
            key={card.to}
            to={card.to}
            className="dash-nav-card"
            style={{ "--card-accent": card.accent, "--card-accent-bg": card.accentBg } as React.CSSProperties}
          >
            <span className="dash-nav-icon-wrap">
              <card.Icon />
            </span>
            <div className="dash-nav-body">
              <p className="dash-nav-title">{card.title}</p>
              <p className="dash-nav-desc">{card.desc}</p>
            </div>
            <span className="dash-nav-arrow">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M5 12h14M12 5l7 7-7 7" />
              </svg>
            </span>
          </Link>
        ))}
      </div>

      {/* ── Analysis Activity ────────────────────────────────── */}
      <div className="dash-chart-card">

        <div className="dash-chart-top">
          <div>
            <h2 className="dash-chart-title">Analysis Activity</h2>
            <p className="dash-chart-subtitle">Benign vs. malignant predictions over time</p>
          </div>

          <div className="dash-date-range">
            <span className="dash-date-range-icon"><IconCalendar /></span>
            <input
              type="date"
              className="dash-date-input"
              value={fromDate}
              max={toDate}
              onChange={(e) => setFromDate(e.target.value)}
              aria-label="From date"
            />
            <span className="dash-date-sep">→</span>
            <input
              type="date"
              className="dash-date-input"
              value={toDate}
              min={fromDate}
              max={today}
              onChange={(e) => setToDate(e.target.value)}
              aria-label="To date"
            />
          </div>
        </div>

        {/* ── Summary badges ───────────────────────────────── */}
        <div className="dash-kpi-row">
          <div className="dash-kpi dash-kpi--total">
            <span className="dash-kpi-value">{loading ? "—" : (stats?.total ?? 0)}</span>
            <span className="dash-kpi-label">Total scans</span>
          </div>
          <div className="dash-kpi dash-kpi--benign">
            <span className="dash-kpi-value">{loading ? "—" : (stats?.benign ?? 0)}</span>
            <span className="dash-kpi-label">Benign</span>
            {!loading && stats && stats.total > 0 && (
              <span className="dash-kpi-pct">{pctBenign}%</span>
            )}
          </div>
          <div className="dash-kpi dash-kpi--malignant">
            <span className="dash-kpi-value">{loading ? "—" : (stats?.malignant ?? 0)}</span>
            <span className="dash-kpi-label">Malignant</span>
            {!loading && stats && stats.total > 0 && (
              <span className="dash-kpi-pct">{pctMalignant}%</span>
            )}
          </div>
        </div>

        {/* ── Divider ──────────────────────────────────────── */}
        <div className="dash-divider" />

        {/* ── Chart ────────────────────────────────────────── */}
        {loading && <p className="dash-chart-placeholder">Loading…</p>}
        {error && (
          <p className="dash-chart-placeholder dash-chart-placeholder--error">{error}</p>
        )}

        {!loading && !error && stats && (
          stats.daily.length === 0 ? (
            <p className="dash-chart-placeholder">No analyses in this period.</p>
          ) : (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart
                data={stats.daily}
                margin={{ top: 4, right: 8, left: -8, bottom: 4 }}
                barCategoryGap="35%"
                barGap={3}
              >
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" vertical={false} />
                <XAxis
                  dataKey="date"
                  tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                  tickFormatter={(v) => v.slice(5)}
                  axisLine={false}
                  tickLine={false}
                />
                <YAxis
                  allowDecimals={false}
                  tick={{ fontSize: 11, fill: "var(--text-muted)" }}
                  axisLine={false}
                  tickLine={false}
                />
                <Tooltip
                  cursor={{ fill: "var(--surface-2)" }}
                  contentStyle={{
                    background: "var(--surface)",
                    border: "1px solid var(--border-strong)",
                    borderRadius: 10,
                    fontSize: 12,
                    boxShadow: "var(--shadow)",
                  }}
                  labelStyle={{ color: "var(--text-secondary)", marginBottom: 4 }}
                  labelFormatter={(l) => `Date: ${l}`}
                />
                <Legend
                  iconType="circle"
                  iconSize={7}
                  wrapperStyle={{ fontSize: 12, paddingTop: 12, color: "var(--text-secondary)" }}
                />
                <Bar dataKey="benign" name="Benign" fill="#65A30D" radius={[4, 4, 0, 0]} />
                <Bar dataKey="malignant" name="Malignant" fill="#e11d48" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )
        )}
      </div>
    </div>
  );
}

export default AdminDashboard;
