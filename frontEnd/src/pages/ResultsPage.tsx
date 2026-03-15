import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import type { AnalyzeResponse } from "../api/analyze";
import { fetchNiftiAsFile } from "../api/History";
import NiiVueViewer from "../components/NiiVueViewer";

function pct(n: number): string {
  return `${(n * 100).toFixed(1)}%`;
}

function fmtBytes(b: number): string {
  if (!b || b === 0) return "—";
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / (1024 * 1024)).toFixed(1)} MB`;
}

type LocationState = { result?: AnalyzeResponse; file?: File } | null;

function ResultsPage() {
  const navigate = useNavigate();
  const { state } = useLocation() as { state: LocationState };

  // niftiFile: comes from navigate state (fresh analysis) or fetched from API (history)
  const [niftiFile,     setNiftiFile]     = useState<File | null>(state?.file ?? null);
  const [niftiLoading,  setNiftiLoading]  = useState(false);
  const [niftiError,    setNiftiError]    = useState<string | null>(null);

  // 2-D heatmap overlay toggle
  const [showHeatmap, setShowHeatmap] = useState(true);

  const r = state?.result;

  // When coming from history (no file in state but server has it), auto-fetch
  useEffect(() => {
    if (niftiFile || !r?.analysis_id || !r?.has_nifti) return;

    let cancelled = false;
    setNiftiLoading(true);
    setNiftiError(null);

    fetchNiftiAsFile(r.analysis_id, r.filename)
      .then((f) => { if (!cancelled) setNiftiFile(f); })
      .catch((err) => { if (!cancelled) setNiftiError(err.message); })
      .finally(() => { if (!cancelled) setNiftiLoading(false); });

    return () => { cancelled = true; };
  }, [r?.analysis_id, r?.has_nifti]);   // eslint-disable-line react-hooks/exhaustive-deps

  if (!r) {
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

  const isMalignancy  = r.prediction.toLowerCase().includes("malig");
  const confidencePct = parseFloat((r.confidence * 100).toFixed(1));
  const badgeClass    = isMalignancy ? "badge-malignancy" : "badge-benign";
  const barClass      = isMalignancy
    ? confidencePct > 80 ? "bar-danger" : "bar-warning"
    : "bar-success";

  return (
    <div className="results-container">

      {/* ── Header ──────────────────────────────────────────────── */}
      <div className="results-header results-header--compact">
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

      {/* ── Main layout ─────────────────────────────────────────── */}
      <div className="results-main">

        {/* Left: 3-D viewer or 2-D fallback */}
        {niftiFile ? (
          <div className="results-viewer-box">
            <div className="image-box-header">
              <span>◈</span> CT Volume — Interactive 3-D Viewer
            </div>
            <NiiVueViewer
              niftiFile={niftiFile}
              gradcamNiftiB64={r.gradcam_nifti_b64 ?? null}
            />
          </div>
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {/* 2-D slice + heatmap overlay */}
            <div className="results-images">

              {/* CT slice with optional heatmap overlay */}
              <div className="image-box">
                <div className="image-box-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span><span>◈</span> CT — Middle Axial Slice</span>
                  {r.heatmap_base64 && (
                    <button
                      className={`heatmap-toggle-btn${showHeatmap ? " active" : ""}`}
                      onClick={() => setShowHeatmap((v) => !v)}
                      title={showHeatmap ? "Hide Grad-CAM overlay" : "Show Grad-CAM overlay"}
                    >
                      {showHeatmap ? "Hide Heatmap" : "Show Heatmap"}
                    </button>
                  )}
                </div>

                {r.slice_base64 ? (
                  <div className="slice-overlay-wrap">
                    <img
                      src={`data:image/png;base64,${r.slice_base64}`}
                      alt="CT axial slice"
                      className="slice-base"
                    />
                    {r.heatmap_base64 && (
                      <img
                        src={`data:image/png;base64,${r.heatmap_base64}`}
                        alt="Grad-CAM overlay"
                        className="slice-heatmap"
                        style={{ opacity: showHeatmap ? 0.6 : 0 }}
                      />
                    )}
                  </div>
                ) : (
                  <div className="image-placeholder">Slice image unavailable</div>
                )}
              </div>

              {/* Grad-CAM standalone (always visible for comparison) */}
              <div className="image-box">
                <div className="image-box-header"><span>◈</span> Grad-CAM Attention Map</div>
                {r.heatmap_base64
                  ? <img src={`data:image/png;base64,${r.heatmap_base64}`} alt="Grad-CAM heatmap" />
                  : <div className="image-placeholder">Heatmap unavailable</div>}
              </div>
            </div>

            {/* NIfTI loading state when fetching from history */}
            {niftiLoading && (
              <div className="load-nifti-prompt">
                <p className="load-nifti-hint">Loading 3-D volume from server…</p>
                <span className="nifti-spinner" />
              </div>
            )}
            {niftiError && (
              <div className="load-nifti-prompt">
                <p className="load-nifti-hint" style={{ color: "var(--danger)" }}>
                  Could not load 3-D viewer: {niftiError}
                </p>
              </div>
            )}
          </div>
        )}

        {/* Right: AI metrics + thumbnails + meta */}
        <div className="results-side">

          <div className="confidence-card">
            <p className="confidence-label">Model Confidence</p>
            <p className="confidence-value">{confidencePct}<span>%</span></p>
            <div className="confidence-bar-wrap">
              <div className={`confidence-bar ${barClass}`} style={{ width: `${confidencePct}%` }} />
            </div>
          </div>

          <div className="prob-card">
            <p className="confidence-label">Class Probabilities</p>
            <div className="prob-row">
              <div className="prob-header">
                <span className="prob-name" style={{ color: "var(--success)" }}>Benign</span>
                <span className="prob-pct">{pct(r.prob_benign)}</span>
              </div>
              <div className="confidence-bar-wrap">
                <div className="confidence-bar bar-success"
                  style={{ width: `${(r.prob_benign * 100).toFixed(1)}%` }} />
              </div>
            </div>
            <div className="prob-row">
              <div className="prob-header">
                <span className="prob-name" style={{ color: "var(--danger)" }}>Malignancy</span>
                <span className="prob-pct">{pct(r.prob_malignancy)}</span>
              </div>
              <div className="confidence-bar-wrap">
                <div className="confidence-bar bar-danger"
                  style={{ width: `${(r.prob_malignancy * 100).toFixed(1)}%` }} />
              </div>
            </div>
          </div>

          {/* 2-D thumbnails in side panel when 3-D viewer is active */}
          {niftiFile && (r.slice_base64 || r.heatmap_base64) && (
            <div className="side-snapshots">
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.5rem" }}>
                <p className="confidence-label" style={{ margin: 0 }}>2-D Reference</p>
                {r.heatmap_base64 && (
                  <button
                    className={`heatmap-toggle-btn${showHeatmap ? " active" : ""}`}
                    onClick={() => setShowHeatmap((v) => !v)}
                  >
                    {showHeatmap ? "Hide Heatmap" : "Show Heatmap"}
                  </button>
                )}
              </div>

              {r.slice_base64 && (
                <div className="snapshot-row">
                  <span className="snapshot-label">Axial slice</span>
                  <div className="slice-overlay-wrap">
                    <img src={`data:image/png;base64,${r.slice_base64}`} alt="axial slice"
                      className="slice-base snapshot-img" />
                    {r.heatmap_base64 && (
                      <img src={`data:image/png;base64,${r.heatmap_base64}`} alt="overlay"
                        className="slice-heatmap"
                        style={{ opacity: showHeatmap ? 0.6 : 0 }} />
                    )}
                  </div>
                </div>
              )}
              {r.heatmap_base64 && (
                <div className="snapshot-row">
                  <span className="snapshot-label">Grad-CAM only</span>
                  <img src={`data:image/png;base64,${r.heatmap_base64}`} alt="Grad-CAM"
                    className="snapshot-img" />
                </div>
              )}
            </div>
          )}

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
        </div>
      </div>

      {/* ── Footer ──────────────────────────────────────────────── */}
      <div className="disclaimer-box">
        ⚠ This AI model is decision-support only and must not replace clinical judgement or formal diagnosis.
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
