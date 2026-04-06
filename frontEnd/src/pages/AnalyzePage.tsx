import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DragAndDrop from "../components/DragAndDrop";
import AnalyzeButton from "../components/AnalyzeButton";
import { analyzeImage } from "../api/analyze";

function formatBytes(b: number): string {
  if (b < 1024) return `${b} B`;
  if (b < 1024 * 1024) return `${(b / 1024).toFixed(1)} KB`;
  return `${(b / (1024 * 1024)).toFixed(1)} MB`;
}

function AnalyzePage() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const navigate = useNavigate();

  async function handleAnalyze() {
    if (!file) {
      setErrorMsg("Please choose a NIfTI file first.");
      return;
    }

    try {
      setLoading(true);
      setErrorMsg(null);

      const result = await analyzeImage(file);
      navigate("/results", { state: { result, file } });
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="analyze-page">
      <header className="analyze-header">
        <h1>Analyze</h1>
        <p className="analyze-subtitle">
          Upload a NIfTI (.nii / .nii.gz) chest CT scan to run inference.
        </p>
      </header>

      <section className="card">
        <h2 className="card-title">Upload NIfTI file</h2>
        <p className="card-hint">Drag and drop or click to browse.</p>

        <DragAndDrop
          onFileSelected={(selectedFile) => {
            setFile(selectedFile);
            setErrorMsg(null);
          }}
        />

        {file && (
          <div className="file-info">
            <p className="file-info-name">📄 {file.name}</p>
            <p className="file-info-meta">
              {formatBytes(file.size)} · {file.type || "application/gzip"}
            </p>
          </div>
        )}

        {errorMsg && <p className="error-text">{errorMsg}</p>}

        <div className="analyze-button-row">
          <AnalyzeButton
            disabled={!file}
            isLoading={loading}
            onClick={handleAnalyze}
            label="Run Analysis"
          />
        </div>

        <p className="disclaimer">
          Educational demo only not a certified medical diagnosis tool.
        </p>
      </section>
    </div>
  );
}

export default AnalyzePage;