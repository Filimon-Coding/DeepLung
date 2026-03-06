import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useTheme } from "../../hooks/useTheme";
import ThemeToggle from "../ThemeToggle/ThemeToggle";

/**
 * Navbar component
 *
 * - Large screens: show links inline.
 * - Smaller laptop screens: collapse links into a burger menu.
 */
function Navbar() {
  // Controls the dropdown menu visibility on smaller screens
  const [menuOpen, setMenuOpen] = useState<boolean>(false);

  // Logged-in user display (email prefix)
  const [userDisplay, setUserDisplay] = useState<string | null>(null);

  // Theme state + toggler (light/dark)
  const { theme, toggleTheme } = useTheme();

  const navigate = useNavigate();

  // Close dropdown when a navigation link is clicked
  const closeMenu = () => setMenuOpen(false);

  // Read email from localStorage
  useEffect(() => {
    const email = localStorage.getItem("email");
    if (email) setUserDisplay(email.split("@")[0]);
    else setUserDisplay(null);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("email");
    localStorage.removeItem("role");
    setUserDisplay(null);
    closeMenu();
    navigate("/");
  };

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
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Home
        </NavLink>

        <NavLink
          to="/analyze"
          onClick={closeMenu}
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Analyze
        </NavLink>

        <NavLink
          to="/results"
          onClick={closeMenu}
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Results
        </NavLink>

        {/* Login vs user */}
        {userDisplay ? (
          <>
            <span className="nav-user">
              Signed in as <strong>{userDisplay}</strong>
            </span>
            <button type="button" className="logout-btn" onClick={handleLogout}>
              Logout
            </button>
          </>
        ) : (
          <NavLink
            to="/login"
            onClick={closeMenu}
            className={({ isActive }) =>
              isActive ? "nav-link active" : "nav-link"
            }
          >
            Login
          </NavLink>
        )}

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

          {/* Login vs user (dropdown) */}
          {userDisplay ? (
            <>
              <div className="dropdown-user">
                Signed in as <strong>{userDisplay}</strong>
              </div>
              <button
                type="button"
                className="dropdown-logout"
                onClick={handleLogout}
              >
                Logout
              </button>
            </>
          ) : (
            <NavLink
              to="/login"
              onClick={closeMenu}
              className={({ isActive }) =>
                isActive ? "dropdown-link active" : "dropdown-link"
              }
            >
              Login
            </NavLink>
          )}

          {/* Theme toggle button (dropdown) */}
          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
      )}
    </nav>
  );
}

export default Navbar;