import { NavLink } from "react-router-dom";
import "./WorkflowTimeline.css";

/**
 * WorkflowTimeline
 * - Viser en vertikal tidslinje for hvordan brukeren navigerer i appen
 * - Kan brukes på HomePage (forklaring) eller en egen "How it works"-side
 */
function WorkflowTimeline() {
  return (
    <section className="timeline">
      {/* Overskrift */}
      <header className="timeline-header">
        <h2>How to run the AI model</h2>
        <p>
          Follow these steps to upload an image and view analysis results.
        </p>
      </header>

      {/* Timeline items */}
      <ol className="timeline-list">
        {/* Step 1 */}
        <li className="timeline-item">
          <div className="timeline-dot" aria-hidden="true" />
          <div className="timeline-card">
            <h3>1) Start at Home</h3>
            <p>
              Read a short overview of the AI pipeline and what the demo is
              intended to show.
            </p>
            <div className="timeline-actions">
              <NavLink className="timeline-link" to="/">
                Go to Home
              </NavLink>
            </div>
          </div>
        </li>

        {/* Step 2 */}
        <li className="timeline-item">
          <div className="timeline-dot" aria-hidden="true" />
          <div className="timeline-card">
            <h3>2) Navigate to Analyze</h3>
            <p>
              Go to the Analyze page to provide an image for inference.
            </p>
            <div className="timeline-actions">
              <NavLink className="timeline-link" to="/analyze">
                Go to Analyze
              </NavLink>
            </div>
          </div>
        </li>

        {/* Step 3 */}
        <li className="timeline-item">
          <div className="timeline-dot" aria-hidden="true" />
          <div className="timeline-card">
            <h3>3) Upload via Drag &amp; Drop</h3>
            <p>
              Drag and drop an image into the upload area. Once a file is added,
              the <strong>Analyze Image</strong> button becomes available.
            </p>
            <p className="timeline-note">
              Tip: Use a supported format like JPG/PNG.
            </p>
          </div>
        </li>

        {/* Step 4 */}
        <li className="timeline-item">
          <div className="timeline-dot" aria-hidden="true" />
          <div className="timeline-card">
            <h3>4) Start inference</h3>
            <p>
              Click <strong>Analyze Image</strong>. The system will prepare the
              input and (later) send it to the backend model endpoint.
            </p>
          </div>
        </li>

        {/* Step 5 */}
        <li className="timeline-item">
          <div className="timeline-dot" aria-hidden="true" />
          <div className="timeline-card">
            <h3>5) View Results</h3>
            <p>
              You will be navigated to the Results page where the model output
              is displayed (prediction label, confidence score and—optionally—a
              heatmap/explainability view).
            </p>
            <div className="timeline-actions">
              <NavLink className="timeline-link" to="/results">
                Go to Results
              </NavLink>
            </div>
          </div>
        </li>

        {/* Step 6 */}
        <li className="timeline-item">
          <div className="timeline-dot" aria-hidden="true" />
          <div className="timeline-card">
            <h3>6) Analyze another image</h3>
            <p>
              Use the call-to-action on the Results page to return to Analyze
              and repeat the workflow.
            </p>
          </div>
        </li>
      </ol>

      {/* Disclaimer */}
      <p className="timeline-disclaimer">
        Educational demo only — not a medical diagnosis tool.
      </p>
    </section>
  );
}

export default WorkflowTimeline;