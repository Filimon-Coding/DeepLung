import { Link } from "react-router-dom";
import { isAuthenticated } from "../api/client";

function HomePage() {
  const authed = isAuthenticated();

  return (
    <div className="home">
      <header className="hero">
        <h1 className="hero-title">
          AI Medical
          <br />
          <span>Imaging Demo</span>
        </h1>

        <p className="hero-subtitle">
          A full-stack demonstration of a 3D convolutional neural network
          pipeline for lung CT analysis — from NIfTI upload to Grad-CAM
          attention maps and saved result history.
        </p>

        <Link to={authed ? "/analyze" : "/login"} className="cta">
          {authed ? "Open Analyze →" : "Sign in to start →"}
        </Link>
      </header>

      <section className="section">
        <h2 className="section-title">How it works</h2>

        <div className="cards">
          <div className="card">
            <div className="card-step">1</div>
            <h3 className="card-title">Upload</h3>
            <p className="card-text">
              Drop a <code>.nii.gz</code> chest CT scan into the Analyze page.
            </p>
          </div>

          <div className="card">
            <div className="card-step">2</div>
            <h3 className="card-title">Inference</h3>
            <p className="card-text">
              The scan is sent through the backend pipeline and the model returns
              class probabilities.
            </p>
          </div>

          <div className="card">
            <div className="card-step">3</div>
            <h3 className="card-title">Results</h3>
            <p className="card-text">
              View prediction, confidence, probabilities, Grad-CAM attention maps,
              and saved history.
            </p>
          </div>
        </div>

        <p className="disclaimer">
          ⚠ Educational demo only — not a certified medical diagnosis tool.
        </p>
      </section>
    </div>
  );
}

export default HomePage;