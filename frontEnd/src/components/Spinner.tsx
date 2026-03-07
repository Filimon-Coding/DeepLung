type SpinnerProps = {
  size?: number;
  label?: string;
};

function Spinner({ size = 18, label = "Loading" }: SpinnerProps) {
  return (
    <span
      className="spinner"
      role="status"
      aria-label={label}
      style={{
        width: size,
        height: size,
      }}
    />
  );
}

export default Spinner;