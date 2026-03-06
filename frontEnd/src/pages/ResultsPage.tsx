import { useLocation, useNavigate } from "react-router-dom";
import type { AnalyzeResponse } from "../api/analyze";


/**
 * ResultsPage
 * - Displays analysis response returned from the backend
 * - Falls back gracefully if the page is opened directly
 */
function ResultsPage() {
  const navigate = useNavigate();
  const location = useLocation();

  // AnalyzePage navigates here with: navigate("/results", { state: { result } })
  const state = location.state as { result?: AnalyzeResponse; previewUrl?: string } | null;

  // If user refreshes /results or opens it directly, state will be missing
  if (!state?.result) {
    return (
      <div className="results-container">
        <h1>Image Analysis Results</h1>
        <p>No results found. Please analyze an image first.</p>

        <button onClick={() => navigate("/analyze")}>Go to Analyze</button>
      </div>
    );
  }

  const { result, previewUrl } = state;

  // Convert confidence to percent if backend sends 0-1
  const confidencePercent =
    result.confidence <= 1 ? (result.confidence * 100).toFixed(1) : result.confidence.toFixed(1);

  return (
    <div className="results-container">
      <h1>Image Analysis Results</h1>

      <div className="results-grid">
        <div className="image-box">
          <h3>Original Image</h3>

          {/* If we have a preview URL from AnalyzePage, show it. Otherwise fallback. */}
          <img
            src={previewUrl ?? "/samples/sample1.jpg"}
            alt="Analyzed image"
          />
        </div>

        <div className="image-box">
          <h3>Model Attention (Heatmap)</h3>

          {/* Placeholder for now */}
          <img src="/samples/sample1.jpg" alt="Heatmap placeholder" />
        </div>
      </div>

      <div className="prediction-box">
        <h2>Prediction: {result.prediction}</h2>
        <p>Confidence: {confidencePercent}%</p>
      </div>

      <div className="interpretation-box">
        <p>
          This AI model provides decision support only and should not replace clinical judgement.
        </p>
      </div>

      <button onClick={() => navigate("/analyze")}>Analyze another image</button>
    </div>
  );
}

export default ResultsPage;