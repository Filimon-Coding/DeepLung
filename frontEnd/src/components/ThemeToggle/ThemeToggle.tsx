type ThemeToggleProps = {
  theme: "light" | "dark";
  onToggle: () => void;
};

/**
 * ThemeToggle
 * - Small button for switching between light and dark theme
 */
function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  return (
    <button className="theme-toggle" type="button" onClick={onToggle}>
      {theme === "dark" ? "Light mode" : "Dark mode"}
    </button>
  );
}

export default ThemeToggle;