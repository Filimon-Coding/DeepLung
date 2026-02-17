import { Link } from "react-router-dom";
import "./HomePage.css";

/**
 * HomePage: Forklarer hvordan AI-modellen fungerer (ingen opplasting her).
 */
function HomePage() {
  return (
    <div className="home">
      {/* Hero */}
      <header className="hero">
        <h1 className="hero-title">AI Medical Imaging Demo</h1>
        <p className="hero-subtitle">
          This application demonstrates a typical AI pipeline for medical imaging.
          A trained convolutional neural network (CNN) can support detection of patterns
          in chest CT images.
        </p>

        {/* CTA */}
        <Link to="/analyze" className="cta">
          Go to Analyze
        </Link>
      </header>

      {/* How it works */}
      <section className="section">
        <h2 className="section-title">How it works</h2>

        <div className="cards">
          <div className="card">
            <div className="card-step">1</div>
            <h3 className="card-title">Input</h3>
            <p className="card-text">
              Provide an image (upload on the Analyze page or choose a sample).
            </p>
          </div>

          <div className="card">
            <div className="card-step">2</div>
            <h3 className="card-title">Preprocessing</h3>
            <p className="card-text">
              The image is resized/normalized to match the model’s expected input.
            </p>
          </div>

          <div className="card">
            <div className="card-step">3</div>
            <h3 className="card-title">Inference & Output</h3>
            <p className="card-text">
              The model computes a prediction score, and the UI displays the result
              (and later, explanations like heatmaps).
            </p>
          </div>
        </div>

        <p className="disclaimer">
          Educational demo only — not a medical diagnosis tool.
        </p>
      </section>
    </div>
  );
}

export default HomePage;