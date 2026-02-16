import { Link } from "react-router-dom";

/**
 * HomePage: forklarer hvordan AI-modellen fungerer.
 * Ingen opplasting på denne siden.
 */
function HomePage() {
  return (
    <>
      <h1>AI Medical Imaging Demo</h1>

      <p>
        This application demonstrates a typical AI pipeline for medical imaging.
        A trained convolutional neural network (CNN) can be used to support
        detection of patterns in chest X-ray images.
      </p>

      <h2>How it works</h2>
      <ol>
        <li><strong>Input:</strong> An image is provided (uploaded or selected as a sample).</li>
        <li><strong>Preprocessing:</strong> Resize/normalize to match the model’s expected input.</li>
        <li><strong>Inference:</strong> The model computes a prediction score.</li>
        <li><strong>Output:</strong> The UI displays the predicted result (and later, explanations).</li>
      </ol>

      <p>
        <Link to="/analyze">Go to Analyze</Link>
      </p>
    </>
  );
}

export default HomePage;