import { useEffect, useRef, useState } from "react";
import { NavLink, useLocation, useNavigate } from "react-router-dom";
import { clearAuth } from "../api/client";
import { useTheme } from "../hooks/useTheme";
import ThemeToggle from "./ThemeToggle";

function getUserDisplay(): string | null {
  return localStorage.getItem("userId") ?? null;
}

function isAdmin(): boolean {
  return localStorage.getItem("role") === "admin";
}

function Navbar() {
  const [userDisplay, setUserDisplay] = useState<string | null>(getUserDisplay());
  const [admin, setAdmin] = useState(isAdmin());
  const [profileOpen, setProfileOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  const profileRef = useRef<HTMLDivElement | null>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    const syncUser = () => {
      setUserDisplay(getUserDisplay());
      setAdmin(isAdmin());
    };

    syncUser();

    window.addEventListener("storage", syncUser);
    window.addEventListener("auth-changed", syncUser as EventListener);

    return () => {
      window.removeEventListener("storage", syncUser);
      window.removeEventListener("auth-changed", syncUser as EventListener);
    };
  }, []);

  useEffect(() => {
    setUserDisplay(getUserDisplay());
    setAdmin(isAdmin());
    setProfileOpen(false);
    setMenuOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    };

    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  function handleLogout() {
    clearAuth();
    window.dispatchEvent(new Event("auth-changed"));
    setUserDisplay(null);
    setProfileOpen(false);
    setMenuOpen(false);
    navigate("/");
  }

  const navClass = ({ isActive }: { isActive: boolean }) =>
    isActive ? "nav-link active" : "nav-link";

  return (
    <nav className="navbar">
      <NavLink to="/" className="logo">
        CRAI
      </NavLink>

      <div className="nav-links">
        <NavLink to="/" className={navClass}>Home</NavLink>
        <NavLink to="/analyze" className={navClass}>Analyze</NavLink>
        <NavLink to="/history" className={navClass}>History</NavLink>
        {admin && <NavLink to="/admin" className={navClass}>Dashboard</NavLink>}

        {!userDisplay && <NavLink to="/login" className={navClass}>Login</NavLink>}

        {userDisplay && (
          <div className="profile-menu" ref={profileRef}>
            <button
              type="button"
              className="profile-button"
              onClick={() => setProfileOpen((prev) => !prev)}
            >
              {userDisplay}
            </button>

            {profileOpen && (
              <div className="profile-dropdown">
                <NavLink
                  to="/change-password"
                  className="profile-dropdown-item"
                  onClick={() => setProfileOpen(false)}
                >
                  Change password
                </NavLink>
                <div className="profile-dropdown-divider" />
                <button
                  type="button"
                  className="profile-dropdown-item"
                  style={{ color: "var(--danger, #e05c5c)" }}
                  onClick={handleLogout}
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        )}

        <ThemeToggle theme={theme} onToggle={toggleTheme} />
      </div>

      <button
        type="button"
        className="burger"
        aria-label="Open navigation"
        onClick={() => setMenuOpen((prev) => !prev)}
      >
        <span className="burger-line" />
        <span className="burger-line" />
        <span className="burger-line" />
      </button>

      {menuOpen && (
        <div className="dropdown">
          <NavLink to="/" className="dropdown-link" onClick={() => setMenuOpen(false)}>Home</NavLink>
          <NavLink to="/analyze" className="dropdown-link" onClick={() => setMenuOpen(false)}>Analyze</NavLink>
          <NavLink to="/history" className="dropdown-link" onClick={() => setMenuOpen(false)}>History</NavLink>
          {admin && <NavLink to="/admin" className="dropdown-link" onClick={() => setMenuOpen(false)}>Dashboard</NavLink>}

          {!userDisplay && (
            <NavLink to="/login" className="dropdown-link" onClick={() => setMenuOpen(false)}>Login</NavLink>
          )}

          {userDisplay && (
            <>
              <NavLink to="/change-password" className="dropdown-link" onClick={() => setMenuOpen(false)}>
                Change password
              </NavLink>
              <button type="button" className="dropdown-logout" onClick={handleLogout}>
                Logout
              </button>
            </>
          )}

          <ThemeToggle theme={theme} onToggle={toggleTheme} />
        </div>
      )}
    </nav>
  );
}

export default Navbar;