import { useNavigate } from "react-router-dom";

/**
 * AnalyzeButton navigerer brukeren til analysesiden (/analyze)
 * når knappen trykkes.
 */
function AnalyzeButton() {
  const navigate = useNavigate();

  return (
    <button
      className="analyze-button"
      onClick={() => navigate("/analyze")}
    >
      Analyze Image
    </button>
  );
}

export default AnalyzeButton;