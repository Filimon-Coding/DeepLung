import { useNavigate } from "react-router-dom";

/**
 * AnalyzeButton navigerer brukeren til resultssiden (/results)
 * når knappen trykkes.
 */
function AnalyzeButton() {
  const navigate = useNavigate();

  return (
    <button
      className="analyze-button"
      onClick={() => navigate("/results")}
    >
      Analyze Image
    </button>
  );
}

export default AnalyzeButton;