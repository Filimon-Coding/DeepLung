import { useEffect, useState } from "react";

export type Theme = "light" | "dark";

/**
 * useTheme
 * - Uses localStorage if user has chosen a theme before
 * - Otherwise falls back to OS preference (prefers-color-scheme)
 * - Sets data-theme attribute on <html> so CSS can react to it
 */
export function useTheme() {
  const [theme, setTheme] = useState<Theme>(() => {
    const saved = localStorage.getItem("theme");
    if (saved === "light" || saved === "dark") return saved;

    const prefersDark = window.matchMedia?.("(prefers-color-scheme: dark)").matches;
    return prefersDark ? "dark" : "light";
  });

  useEffect(() => {
    // Put theme on the root element so CSS can target it
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  };

  return { theme, setTheme, toggleTheme };
}