import { useLocation, useNavigate } from "react-router-dom";
import type { AnalyzeResponse } from "../api/analyze";

function pct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function fmtBytes(b: number): string {
  if (!b || b === 0) return "—";
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / (1024 * 1024)).toFixed(1)} MB`;
}

type LocationState = { result?: AnalyzeResponse } | null;

function ResultsPage() {
  const navigate = useNavigate();
  const { state } = useLocation() as { state: LocationState };

  if (!state?.result) {
    return (
      <div className="results-container" style={{ textAlign: "center" }}>
        <h1 className="results-title">No results found</h1>
        <p style={{ color: "var(--text-secondary)", margin: "1rem 0 1.5rem" }}>
          Please analyse a scan first.
        </p>
        <button className="btn-primary" onClick={() => navigate("/analyze")}>
          Go to Analyze
        </button>
      </div>
    );
  }

  const r = state.result;
  const isMalignancy = r.prediction.toLowerCase().includes("malig");
  const confidencePct = parseFloat((r.confidence * 100).toFixed(1));

  const badgeClass = isMalignancy ? "badge-malignancy" : "badge-benign";
  const barClass = isMalignancy
    ? confidencePct > 80
      ? "bar-danger"
      : "bar-warning"
    : "bar-success";

  return (
    <div className="results-container">
      <div className="results-header">
        <h1 className="results-title">Analysis Results</h1>

        <div className={`prediction-badge ${badgeClass}`}>
          <span className="badge-dot" />
          {r.prediction.toUpperCase()}
        </div>

        <p className="results-meta">
          {r.filename && <span>{r.filename} · </span>}
          Confidence {pct(r.confidence)}
        </p>
      </div>

      <div className="results-images">
        <div className="image-box">
          <div className="image-box-header">
            <span>◈</span> CT — Middle Axial Slice
          </div>
          {r.slice_base64 ? (
            <img
              src={`data:image/png;base64,${r.slice_base64}`}
              alt="CT middle axial slice"
            />
          ) : (
            <div className="image-placeholder">Slice image unavailable</div>
          )}
        </div>

        <div className="image-box">
          <div className="image-box-header">
            <span>◈</span> Grad-CAM Attention Map
          </div>
          {r.heatmap_base64 ? (
            <img
              src={`data:image/png;base64,${r.heatmap_base64}`}
              alt="Grad-CAM heatmap"
            />
          ) : (
            <div className="image-placeholder">Heatmap unavailable</div>
          )}
        </div>
      </div>

      <div className="results-stats">
        <div className="confidence-card">
          <p className="confidence-label">Model Confidence</p>
          <p className="confidence-value">
            {confidencePct}
            <span>%</span>
          </p>
          <div className="confidence-bar-wrap">
            <div
              className={`confidence-bar ${barClass}`}
              style={{ width: `${confidencePct}%` }}
            />
          </div>
        </div>

        <div className="prob-card">
          <p className="confidence-label">Class Probabilities</p>

          <div className="prob-row">
            <div className="prob-header">
              <span className="prob-name" style={{ color: "var(--success)" }}>
                Benign
              </span>
              <span className="prob-pct">{pct(r.prob_benign)}</span>
            </div>
            <div className="confidence-bar-wrap">
              <div
                className="confidence-bar bar-success"
                style={{ width: `${(r.prob_benign * 100).toFixed(1)}%` }}
              />
            </div>
          </div>

          <div className="prob-row">
            <div className="prob-header">
              <span className="prob-name" style={{ color: "var(--danger)" }}>
                Malignancy
              </span>
              <span className="prob-pct">{pct(r.prob_malignancy)}</span>
            </div>
            <div className="confidence-bar-wrap">
              <div
                className="confidence-bar bar-danger"
                style={{ width: `${(r.prob_malignancy * 100).toFixed(1)}%` }}
              />
            </div>
          </div>
        </div>
      </div>

      {r.filename && (
        <div className="meta-card">
          <div className="meta-item">
            <p className="meta-label">Filename</p>
            <p className="meta-value">{r.filename}</p>
          </div>

          {r.size_bytes > 0 && (
            <div className="meta-item">
              <p className="meta-label">File size</p>
              <p className="meta-value">{fmtBytes(r.size_bytes)}</p>
            </div>
          )}

          <div className="meta-item">
            <p className="meta-label">Format</p>
            <p className="meta-value">{r.content_type || "application/gzip"}</p>
          </div>
        </div>
      )}

      <div className="disclaimer-box">
        ⚠ This AI model is decision-support only and must not replace clinical
        judgement or formal diagnosis.
      </div>

      <div className="results-actions" style={{ marginTop: "1.5rem" }}>
        <button className="btn-primary" onClick={() => navigate("/analyze")}>
          Analyse another scan
        </button>
        <button className="btn-secondary" onClick={() => navigate("/history")}>
          View history
        </button>
      </div>
    </div>
  );
}

export default ResultsPage;