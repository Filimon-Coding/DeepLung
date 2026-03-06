import { useState } from "react";
import { useNavigate } from "react-router-dom";
import DragAndDrop from "../components/DragAndDrop/DragAndDrop";
import AnalyzeButton from "../components/AnalyzeButton/AnalyzeButton";
import { analyzeImage } from "../api/analyze";

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function AnalyzePage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!selectedFile) return;

    try {
      setIsLoading(true);
      setErrorMsg(null);

      const result = await analyzeImage(selectedFile);

      navigate("/results", { state: { result } });
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="analyze-page">
      <header className="analyze-header">
        <h1>Analyze</h1>
        <p className="analyze-subtitle">
          Upload a NIfTI file (.nii or .nii.gz) to run the model and view results.
        </p>
      </header>

      <section className="card">
        <h2 className="card-title">Upload NIfTI file</h2>
        <p className="card-hint">
          Drag & drop or click the area below to select a file.
        </p>

        <DragAndDrop
          onFileSelected={(file) => {
            setSelectedFile(file);
            setErrorMsg(null);
          }}
        />

        {/* File info panel — replaces image preview for NIfTI files */}
        {selectedFile && (
          <div
            style={{
              marginTop: "1.25rem",
              padding: "1rem 1.25rem",
              background: "var(--surface-2)",
              border: "1px solid var(--border)",
              borderRadius: "12px",
              display: "flex",
              flexDirection: "column",
              gap: "0.35rem",
            }}
          >
            <p style={{ margin: 0, fontWeight: 600, color: "var(--text)" }}>
              📄 {selectedFile.name}
            </p>
            <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Size: {formatBytes(selectedFile.size)}
            </p>
            <p style={{ margin: 0, color: "var(--text-secondary)", fontSize: "0.9rem" }}>
              Type: {selectedFile.type || "application/gzip"}
            </p>
          </div>
        )}

        {/* Backend / network error */}
        {errorMsg && <p className="error-text">{errorMsg}</p>}

        <div className="analyze-button-row">
          <AnalyzeButton
            disabled={!selectedFile}
            isLoading={isLoading}
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