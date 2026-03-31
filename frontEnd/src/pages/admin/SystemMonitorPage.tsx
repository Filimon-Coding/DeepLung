import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import {
  fetchSystemLogs,
  fetchSystemHealth,
  type LogEntry,
  type SystemHealth,
} from "../../api/admin";

function fmtDate(iso: string) {
  return new Date(iso).toLocaleString("no-NO", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function fmtSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function StatusDot({ status }: { status: string }) {
  const color =
    status === "online" ? "var(--primary)" :
    status === "offline" ? "#e11d48" : "#f59e0b";
  return (
    <span
      style={{
        display: "inline-block",
        width: 9,
        height: 9,
        borderRadius: "50%",
        background: color,
        marginRight: 7,
        flexShrink: 0,
      }}
    />
  );
}

export default function SystemMonitorPage() {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState("");

  function load() {
    setLoading(true);
    setError(null);
    Promise.all([fetchSystemHealth(), fetchSystemLogs(200)])
      .then(([h, l]) => {
        setHealth(h);
        setLogs(l);
      })
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }

  useEffect(() => { load(); }, []);

  const filtered = logs.filter((l) => {
    const q = search.toLowerCase();
    return (
      l.userEmail.toLowerCase().includes(q) ||
      l.filename.toLowerCase().includes(q) ||
      l.prediction.toLowerCase().includes(q)
    );
  });

  return (
    <div className="admin-page">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="dash-header">
        <div>
          <p className="dash-eyebrow">
            <Link to="/admin" className="dash-breadcrumb-link">Admin Dashboard</Link>
            {" / "}
            <span>System Monitor</span>
          </p>
          <h1 className="dash-title">System Monitor</h1>
          <p className="dash-subtitle">Service health and analysis activity log.</p>
        </div>
        <button className="btn-secondary" onClick={load} disabled={loading}>
          {loading ? "Refreshing…" : "Refresh"}
        </button>
      </div>

      {error && <p className="auth-error">{error}</p>}

      {/* ── Service health ─────────────────────────────────────── */}
      <div className="sysmon-health-grid">
        <div className="sysmon-health-card">
          <p className="sysmon-health-label">API Service</p>
          <p className="sysmon-health-status">
            <StatusDot status={health?.apiStatus ?? "unknown"} />
            {health ? health.apiStatus : "—"}
          </p>
        </div>
        <div className="sysmon-health-card">
          <p className="sysmon-health-label">Python / AI Service</p>
          <p className="sysmon-health-status">
            <StatusDot status={health?.pythonServiceStatus ?? "unknown"} />
            {health ? health.pythonServiceStatus : "—"}
          </p>
        </div>
        <div className="sysmon-health-card">
          <p className="sysmon-health-label">Total Users</p>
          <p className="sysmon-health-number">{health?.totalUsers ?? "—"}</p>
        </div>
        <div className="sysmon-health-card">
          <p className="sysmon-health-label">Total Analyses</p>
          <p className="sysmon-health-number">{health?.totalAnalyses ?? "—"}</p>
        </div>
        <div className="sysmon-health-card">
          <p className="sysmon-health-label">Pending Requests</p>
          <p className="sysmon-health-number">{health?.pendingRequests ?? "—"}</p>
        </div>
        {health && (
          <div className="sysmon-health-card sysmon-health-card--muted">
            <p className="sysmon-health-label">Last checked</p>
            <p className="sysmon-health-ts">{fmtDate(health.checkedAt)}</p>
          </div>
        )}
      </div>

      {/* ── Activity log ───────────────────────────────────────── */}
      <div className="dash-chart-card" style={{ marginTop: 24 }}>
        <div className="dash-chart-top">
          <div>
            <h2 className="dash-chart-title">Analysis Log</h2>
            <p className="dash-chart-subtitle">Most recent {logs.length} scan submissions</p>
          </div>
          <input
            className="sysmon-search"
            type="search"
            placeholder="Search user, file, result…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="dash-divider" />

        {loading && <p className="dash-chart-placeholder">Loading…</p>}

        {!loading && filtered.length === 0 && (
          <p className="dash-chart-placeholder">No entries found.</p>
        )}

        {!loading && filtered.length > 0 && (
          <div className="sysmon-table-wrap">
            <table className="sysmon-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Date / Time</th>
                  <th>User ID</th>
                  <th>User</th>
                  <th>File</th>
                  <th>Size</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((log) => (
                  <tr key={log.id}>
                    <td className="sysmon-td-id">{log.id}</td>
                    <td className="sysmon-td-date">{fmtDate(log.createdAt)}</td>
                    <td className="sysmon-td-userid">{log.userId}</td>
                    <td className="sysmon-td-user">{log.userEmail}</td>
                    <td className="sysmon-td-file" title={log.filename}>
                      {log.filename.length > 30 ? log.filename.slice(0, 28) + "…" : log.filename}
                    </td>
                    <td className="sysmon-td-size">{fmtSize(log.sizeBytes)}</td>
                    <td>
                      <span
                        className={`sysmon-badge ${
                          log.prediction === "Benign"
                            ? "sysmon-badge--benign"
                            : "sysmon-badge--malignant"
                        }`}
                      >
                        {log.prediction}
                      </span>
                    </td>
                    <td className="sysmon-td-conf">
                      {(log.confidence * 100).toFixed(1)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
