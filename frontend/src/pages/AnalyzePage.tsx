import DragAndDrop from "../components/DragAndDrop/DragAndDrop";
import AnalyzeButton from "../components/AnalyzeButton/AnalyzeButton";
import ErrorBoundary from "../ErrorBoundary";
import "../App.css";

/**
 * AnalyzePage: siden der brukeren laster opp/velger bilde
 * og (senere) kjører AI-analyse.
 */
function AnalyzePage() {
  return (
    <>
      <h1>Analyze</h1>

      <ErrorBoundary>
        <DragAndDrop />
      </ErrorBoundary>

      <p className="description-text">Or select sample image:</p>

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

      <AnalyzeButton />
    </>
  );
}

export default AnalyzePage;