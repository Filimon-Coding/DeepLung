import { useNavigate } from "react-router-dom";
import "./ResultsPage.css";

function ResultsPage() {
  const navigate = useNavigate();

  // Midlertidige dummy-verdier (erstattes senere med ekte API-svar)
  const prediction = "Tumor detected";
  const confidence = 87.4;

  return (
    <div className="results-container">
      <h1>Image Analysis Results</h1>

      <div className="results-grid">
        <div className="image-box">
          <h3>Original Image</h3>
          <img src="/samples/sample1.jpg" alt="Analyzed X-ray" />
        </div>

        <div className="image-box">
          <h3>Model Attention (Heatmap)</h3>
          <img src="/samples/sample1.jpg" alt="Heatmap placeholder" />
        </div>
      </div>

      <div className="prediction-box">
        <h2>Prediction: {prediction}</h2>
        <p>Confidence: {confidence}%</p>
      </div>

      <div className="interpretation-box">
        <p>
          This AI model provides decision support only and should not replace
          clinical judgement.
        </p>
      </div>

      <button onClick={() => navigate("/analyze")}>
        Analyze another image
      </button>
    </div>
  );
}

export default ResultsPage;