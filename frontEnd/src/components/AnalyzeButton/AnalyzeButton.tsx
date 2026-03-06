import Spinner from "../Spinner/Spinner";

type AnalyzeButtonProps = {
  onClick: () => void;
  disabled?: boolean;
  label?: string;
  isLoading?: boolean;
};

/**
 * AnalyzeButton
 * Reusable button controlled by parent (AnalyzePage).
 */
function AnalyzeButton({
  onClick,
  disabled = false,
  label = "Analyze Image",
  isLoading = false,
}: AnalyzeButtonProps) {
  return (
    <button
      className="analyze-button"
      type="button"
      onClick={onClick}
      disabled={disabled || isLoading}
    >
      {isLoading ? (
        <span style={{ display: "inline-flex", gap: "0.5rem", alignItems: "center" }}>
          <Spinner label="Analyzing" size={18} />
          Analyzing...
        </span>
      ) : (
        label
      )}
    </button>
  );
}

export default AnalyzeButton;