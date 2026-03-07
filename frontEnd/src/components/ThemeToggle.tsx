type ThemeToggleProps = {
  theme: "light" | "dark";
  onToggle: () => void;
};

function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  return (
    <button className="theme-toggle" type="button" onClick={onToggle}>
      {theme === "dark" ? "Light mode" : "Dark mode"}
    </button>
  );
}

export default ThemeToggle;