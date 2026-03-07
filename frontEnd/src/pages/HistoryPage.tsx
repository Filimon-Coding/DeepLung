import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  fetchHistory,
  fetchHistoryDetail,
  deleteHistoryItem,
  type HistoryItem,
} from "../api/History";

function fmtPct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function fmtDate(iso: string): string {
  return new Date(iso).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function HistoryPage() {
  const navigate = useNavigate();

  const [items,    setItems]    = useState<HistoryItem[]>([]);
  const [total,    setTotal]    = useState(0);
  const [page,     setPage]     = useState(1);
  const [loading,  setLoading]  = useState(true);
  const [error,    setError]    = useState<string | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [viewing,  setViewing]  = useState<number | null>(null);

  const PAGE_SIZE  = 20;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  const load = async (p: number) => {
    try {
      setLoading(true);
      setError(null);
      const data = await fetchHistory(p, PAGE_SIZE);
      setItems(data.items);
      setTotal(data.total);
      setPage(p);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load history.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { load(1); }, []);

  const handleView = async (id: number) => {
    try {
      setViewing(id);
      const result = await fetchHistoryDetail(id);
      navigate("/results", { state: { result } });
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to load result.");
    } finally {
      setViewing(null);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("Delete this result permanently?")) return;
    try {
      setDeleting(id);
      await deleteHistoryItem(id);
      load(page);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Delete failed.");
    } finally {
      setDeleting(null);
    }
  };

  return (
    <div className="history-page">
      <h1>Analysis History</h1>

      {loading && (
        <p style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)" }}>
          Loading…
        </p>
      )}

      {error && <p className="error-text">{error}</p>}

      {!loading && !error && items.length === 0 && (
        <div className="history-empty">
          <p>No analyses yet.</p>
          <button
            className="btn-primary"
            style={{ marginTop: "1rem" }}
            onClick={() => navigate("/analyze")}
          >
            Analyse a scan
          </button>
        </div>
      )}

      {!loading && items.length > 0 && (
        <>
          <div
            style={{
              background:   "var(--surface)",
              border:       "1px solid var(--border)",
              borderRadius: 14,
              overflow:     "hidden",
            }}
          >
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>File</th>
                  <th>Prediction</th>
                  <th>Confidence</th>
                  <th>Benign</th>
                  <th>Malignancy</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {items.map((item) => {
                  const isMalig = item.prediction.toLowerCase().includes("malig");
                  return (
                    <tr key={item.id}>
                      <td className="history-date">{fmtDate(item.createdAtUtc)}</td>

                      <td
                        style={{
                          fontFamily:    "var(--font-mono)",
                          fontSize:      "0.82rem",
                          maxWidth:      200,
                          overflow:      "hidden",
                          textOverflow:  "ellipsis",
                          whiteSpace:    "nowrap",
                        }}
                        title={item.filename}
                      >
                        {item.filename}
                      </td>

                      <td>
                        <span className={`history-badge ${isMalig ? "malignancy" : "benign"}`}>
                          {item.prediction}
                        </span>
                      </td>

                      <td className="history-pct">{fmtPct(item.confidence)}</td>

                      <td className="history-pct" style={{ color: "var(--success)" }}>
                        {fmtPct(item.probBenign)}
                      </td>

                      <td className="history-pct" style={{ color: "var(--danger)" }}>
                        {fmtPct(item.probMalignancy)}
                      </td>

                      <td>
                        <div style={{ display: "flex", gap: "0.5rem" }}>
                          <button
                            className="btn-secondary"
                            style={{ padding: "0.3rem 0.65rem", fontSize: "0.8rem" }}
                            disabled={viewing === item.id}
                            onClick={() => handleView(item.id)}
                          >
                            {viewing === item.id ? "…" : "View"}
                          </button>

                          <button
                            style={{
                              background:   "transparent",
                              border:       "1px solid var(--danger)",
                              color:        "var(--danger)",
                              borderRadius: 8,
                              padding:      "0.3rem 0.6rem",
                              fontSize:     "0.8rem",
                              cursor:       "pointer",
                              opacity:      deleting === item.id ? 0.5 : 1,
                            }}
                            disabled={deleting === item.id}
                            onClick={() => handleDelete(item.id)}
                          >
                            {deleting === item.id ? "…" : "✕"}
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div
              style={{
                marginTop:   "1.25rem",
                display:     "flex",
                gap:         "0.75rem",
                justifyContent: "center",
                alignItems:  "center",
              }}
            >
              <button
                className="btn-secondary"
                disabled={page === 1}
                onClick={() => load(page - 1)}
                style={{ padding: "0.4rem 0.9rem" }}
              >
                ← Prev
              </button>

              <span style={{ color: "var(--text-muted)", fontFamily: "var(--font-mono)", fontSize: "0.85rem" }}>
                {page} / {totalPages}
              </span>

              <button
                className="btn-secondary"
                disabled={page === totalPages}
                onClick={() => load(page + 1)}
                style={{ padding: "0.4rem 0.9rem" }}
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}