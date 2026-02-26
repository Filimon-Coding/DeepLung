type AnalyzeButtonProps = {
  onClick: () => void;
  disabled?: boolean;
  label?: string;
};

/**
 * AnalyzeButton
 *
 * A reusable button component.
 * The parent component (AnalyzePage) controls:
 * - what happens on click
 * - whether it is disabled
 * - what label it shows
 */
function AnalyzeButton({
  onClick,
  disabled = false,
  label = "Analyze Image",
}: 
AnalyzeButtonProps) {
  return (
    <button
      className="analyze-button"
      type="button"
      onClick={onClick}
      disabled={disabled}
    >
      {label}
    </button>
  );
}

export default AnalyzeButton;