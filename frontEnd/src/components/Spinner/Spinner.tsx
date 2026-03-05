import "./Spinner.css";

type SpinnerProps = {
  /** Accessible label for screen readers */
  label?: string;
  /** Optional size in px (defaults to 18) */
  size?: number;
};

/**
 * Spinner
 * Small loading indicator (theme-friendly).
 */
function Spinner({ label = "Loading", size = 18 }: SpinnerProps) {
  return (
    <span className="spinner-wrap" aria-label={label} role="status">
      <span className="spinner" style={{ width: size, height: size }} />
    </span>
  );
}

export default Spinner;