import { Routes, Route } from "react-router-dom";
import DragAndDrop from "./components/DragAndDrop/DragAndDrop";
import ErrorBoundary from "./ErrorBoundary";
import AnalyzePage from "./pages/AnalyzePage";
import AnalyzeButton from "./components/AnalyzeButton/AnalyzeButton";
import "./App.css";

/**
 * App-komponenten fungerer som hovedcontainer
 * for frontend-applikasjonen.
 * Den styrer overordnet layout og routing mellom sider.
 */
function App() {
  return (
    <Routes>
      {/* Startside */}
      <Route
        path="/"
        element={
          <>
            <h1>AI Medical Imaging Demo</h1>

            {/* ErrorBoundary sørger for at UI ikke krasjer
                hvis DragAndDrop-komponenten får en runtime-feil */}
            <ErrorBoundary>
              <DragAndDrop />
            </ErrorBoundary>

            {/* Tekst over sample images */}
            <p className="description-text">
              Or select sample image:
            </p>

            {/* Container for sample images */}
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

            {/* Knapp som navigerer til analysesiden */}
            <AnalyzeButton />
          </>
        }
      />

      {/* Analyseside */}
      <Route path="/analyze" element={<AnalyzePage />} />
    </Routes>
  );
}

export default App;