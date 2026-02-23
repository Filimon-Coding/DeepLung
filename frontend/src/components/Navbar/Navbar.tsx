import { useState } from "react";
import { NavLink } from "react-router-dom";
import "./Navbar.css";
import { useTheme } from "../../hooks/useTheme";
import ThemeToggle from "../ThemeToggle/ThemeToggle";
import "../ThemeToggle/ThemeToggle.css";

/**
 * Navbar component
 *
 * - Large screens: show links inline.
 * - Smaller laptop screens: collapse links into a burger menu.
 */
function Navbar() {
  // Controls the dropdown menu visibility on smaller screens
  const [menuOpen, setMenuOpen] = useState<boolean>(false);

  // Theme state + toggler (light/dark)
  const { theme, toggleTheme } = useTheme();

  // Close dropdown when a navigation link is clicked
  const closeMenu = () => setMenuOpen(false);

  return (
    <nav className="navbar">
      {/* Logo navigates to Home */}
      <NavLink to="/" className="logo" onClick={closeMenu}>
        CRAI
      </NavLink>

      {/* Inline links (hidden on smaller screens via CSS) */}
      <div className="nav-links">
        <NavLink
          to="/"
          onClick={closeMenu}
          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          Home
        </NavLink>

        <NavLink
          to="/analyze"
          onClick={closeMenu}
          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          Analyze
        </NavLink>

        <NavLink
          to="/results"
          onClick={closeMenu}
          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          Results
        </NavLink>

        <NavLink
          to="/login"
          onClick={closeMenu}
          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          Login
        </NavLink>

        {/* Theme toggle button (desktop) */}
        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </div>

      {/* Burger button (shown on smaller screens via CSS) */}
      <button
        type="button"
        className="burger"
        aria-label="Open navigation menu"
        aria-expanded={menuOpen}
        onClick={() => setMenuOpen((prev) => !prev)}
      >
        <span className="burger-line" />
        <span className="burger-line" />
        <span className="burger-line" />
      </button>

      {/* Dropdown menu for smaller screens */}
      {menuOpen && (
        <div className="dropdown">
          <NavLink
            to="/"
            onClick={closeMenu}
            className={({ isActive }) =>
              isActive ? "dropdown-link active" : "dropdown-link"
            }
          >
            Home
          </NavLink>

          <NavLink
            to="/analyze"
            onClick={closeMenu}
            className={({ isActive }) =>
              isActive ? "dropdown-link active" : "dropdown-link"
            }
          >
            Analyze
          </NavLink>

          <NavLink
            to="/results"
            onClick={closeMenu}
            className={({ isActive }) =>
              isActive ? "dropdown-link active" : "dropdown-link"
            }
          >
            Results
          </NavLink>

          <NavLink
            to="/login"
            onClick={closeMenu}
            className={({ isActive }) =>
              isActive ? "dropdown-link active" : "dropdown-link"
            }
          >
            Login
          </NavLink>

          {/* Theme toggle button (dropdown) */}
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
      )}
    </nav>
  );
}

export default Navbar;