import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DragAndDrop from "../components/DragAndDrop/DragAndDrop";
import AnalyzeButton from "../components/AnalyzeButton/AnalyzeButton";
import { analyzeImage } from "../api/analyze";
import "./AnalyzePage.css";

/**
 * AnalyzePage
 * - Receives file from DragAndDrop
 * - Sends file to backend for analysis
 * - Navigates to Results page with response
 */
function AnalyzePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  

  const navigate = useNavigate();

  /**
   * Upload file to backend and navigate to /results with returned JSON.
   */
  const handleAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setIsLoading(true);
      setErrorMsg(null);

      // Call backend and get JSON result
      const result = await analyzeImage(selectedFile);

      // Create a local preview URL so ResultsPage can show the uploaded image
      const previewUrl = URL.createObjectURL(selectedFile);

      // Navigate to Results and pass data via router state
      navigate("/results", { state: { result, previewUrl } });
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="analyze-page">
      {/* Title + short description */}
      <header className="analyze-header">
        <h1>Analyze</h1>
        <p className="analyze-subtitle">
          Upload an image to run the model and view results.
        </p>
      </header>

      {/* Upload Card */}
      <section className="card">
        <h2 className="card-title">Upload image</h2>
        <p className="card-hint">
          Drag & drop a file into the area below.
        </p>

        <DragAndDrop onFileSelected={(file) => {
          setSelectedFile(file);
          setPreviewUrl(URL.createObjectURL(file));
          }}
        />

        {/* Show selected file */}
        {selectedFile && (
          <p className="file-selected">
            Selected file: <strong>{selectedFile.name}</strong>
          </p>
        )}

        {/* Show selected image */}
        {previewUrl && (
          <div className="image-preview"> 
          <h3>Preview</h3>
          <img src={previewUrl} alt="Preview" />
          </div>
        )}

        {/* Show error */}
        {errorMsg && <p className="error-text">{errorMsg}</p>}

        {/* Analyze Button moved inside upload card */}
        <div className="analyze-button-row">
          <AnalyzeButton
            disabled={!selectedFile || isLoading}
            label={isLoading ? "Analyzing..." : "Analyze Image"}
            onClick={handleAnalyze}
          />
        </div>

        <p className="disclaimer">
          Educational demo only — not a medical diagnosis tool.
        </p>
      </section>
    </div>
  );
}

export default AnalyzePage;