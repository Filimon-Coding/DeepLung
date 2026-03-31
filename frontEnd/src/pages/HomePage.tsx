import { Link } from "react-router-dom";
import { isAuthenticated } from "../api/client";
import LungVisual from "../components/LungVisual";

function HomePage() {
  const authed = isAuthenticated();

  return (
    <div className="home">

      {/* ── Hero ─────────────────────────────────── */}
      <section className="hero-split">
        <div className="hero-text">
          <span className="hero-eyebrow">Clinical AI · Radiology Support</span>
          <h1 className="hero-title">
            Lung CT Analysis<br />
            <span>Powered by AI</span>
          </h1>
          <p className="hero-subtitle">
            Upload a chest CT scan and receive an instant AI-assisted read —
            confidence scores, class probabilities, and Grad-CAM attention
            heatmaps that show exactly where the model is looking.
          </p>
          <div className="hero-actions">
            <Link to={authed ? "/analyze" : "/login"} className="cta">
              {authed ? "Analyze a Scan →" : "Sign in to start →"}
            </Link>
            {authed && (
              <Link to="/history" className="cta-secondary">
                View history
              </Link>
            )}
          </div>

          <div className="hero-stats">
            <div className="hero-stat">
              <span className="hero-stat-value">3D</span>
              <span className="hero-stat-label">ResNet model</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-value">NIfTI</span>
              <span className="hero-stat-label">volumetric input</span>
            </div>
            <div className="hero-stat-divider" />
            <div className="hero-stat">
              <span className="hero-stat-value">Grad-CAM</span>
              <span className="hero-stat-label">explainability</span>
            </div>
          </div>
        </div>

        <div className="hero-visual">
          <div className="lung-glow-ring" />
          <LungVisual />
        </div>
      </section>

      {/* ── How it works ─────────────────────────── */}
      <section className="section">
        <p className="section-eyebrow">Workflow</p>
        <h2 className="section-title">From scan to diagnosis in seconds</h2>

        <div className="cards">
          <div className="card">
            <div className="card-step">1</div>
            <h3 className="card-title">Upload CT Scan</h3>
            <p className="card-text">
              Drop a <code>.nii.gz</code> NIfTI file from your radiology
              workstation. The system accepts standard formats used across
              clinical imaging pipelines.
            </p>
          </div>

          <div className="card">
            <div className="card-step">2</div>
            <h3 className="card-title">3D AI Inference</h3>
            <p className="card-text">
              A 3D ResNet processes the full volumetric scan — not individual
              slices — capturing spatial patterns across all axes to classify
              lung pathology with calibrated confidence.
            </p>
          </div>

          <div className="card">
            <div className="card-step">3</div>
            <h3 className="card-title">Explainable Results</h3>
            <p className="card-text">
              Grad-CAM heatmaps are overlaid on the CT slice to highlight
              regions that drove the prediction. Results are saved to your
              personal history for review and comparison.
            </p>
          </div>
        </div>
      </section>

      {/* ── Disclaimer ───────────────────────────── */}
      <p className="disclaimer">
        For research and demonstration purposes only — not a certified medical device.
        Clinical decisions must be made by qualified healthcare professionals.
      </p>

    </div>
  );
}

export default HomePage;
