import DragAndDrop from "../components/DragAndDrop/DragAndDrop";
import AnalyzeButton from "../components/AnalyzeButton/AnalyzeButton";
import ErrorBoundary from "../ErrorBoundary";
import "./AnalyzePage.css";

/**
 * AnalyzePage
 * - Viser upload (Drag & Drop)
 * - Viser sample image 
 * - (senere) Kjører AI-analyse
 * - Viser Analyze-knapp som navigerer til Results
 */
function AnalyzePage() {
  return (
    <div className="analyze-page">
      {/* Tittel + kort forklaring */}
      <header className="analyze-header">
        <h1>Analyze</h1>
        <p className="analyze-subtitle">
          Upload an image or choose a sample to run the model.
        </p>
      </header>

      {/* Card: Upload */}
      <section className="card">
        <h2 className="card-title">Upload image</h2>
        <p className="card-hint">Drag & drop a file into the area below.</p>

        {/* ErrorBoundary sørger for at UI ikke krasjer ved runtime-feil */}
        <ErrorBoundary>
          <DragAndDrop />
        </ErrorBoundary>
      </section>

      {/* Card: Samples + button */}
      <section className="card">
        <h2 className="card-title">Or select sample image</h2>

        {/* Sample image source:
            https://www.hssib.org.uk/patient-safety-investigations/missed-detection-of-lung-cancer-on-chest-x-rays-of-patients-being-seen-in-primary-care/investigation-report/
        */}
        <div className="sample-images">
          <img
            src="/samples/sample1.jpg"
            alt="Sample chest X-ray"
            className="sample-image"
          />
        </div>

        {/* Knapp som navigerer videre (f.eks. til /results) */}
        <div className="analyze-button-row">
          <AnalyzeButton />
        </div>

        <p className="disclaimer">
          Educational demo only — not a medical diagnosis tool.
        </p>
      </section>
    </div>
  );
}

export default AnalyzePage;