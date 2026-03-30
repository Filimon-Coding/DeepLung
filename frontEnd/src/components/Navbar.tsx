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
        <svg
          className="logo-icon"
          viewBox="0 0 32 32"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          aria-hidden="true"
        >
          {/* trachea */}
          <rect x="14" y="1" width="4" height="9" rx="2" fill="currentColor" />
          {/* left lung */}
          <path
            d="M14,9 C13,9 9,10 7,13 C5,16 4.5,20 5.5,23.5 C6.5,27 9,29 12,28.5 C14,28 14,26 14,24 L14,9 Z"
            fill="currentColor"
            opacity="0.85"
          />
          {/* right lung */}
          <path
            d="M18,9 C19,9 23,10 25,13 C27,16 27.5,20 26.5,23.5 C25.5,27 23,29 20,28.5 C18,28 18,26 18,24 L18,9 Z"
            fill="currentColor"
            opacity="0.85"
          />
          {/* inner vein hint — left */}
          <path
            d="M11,15 C10,17 9.5,20 10,23"
            stroke="white"
            strokeWidth="1.2"
            strokeLinecap="round"
            opacity="0.55"
          />
          {/* inner vein hint — right */}
          <path
            d="M21,15 C22,17 22.5,20 22,23"
            stroke="white"
            strokeWidth="1.2"
            strokeLinecap="round"
            opacity="0.55"
          />
        </svg>
        DeepLung
      </NavLink>

      <div className="nav-pill-bar">
        <NavLink to="/" className={navClass}>Home</NavLink>
        <NavLink to="/analyze" className={navClass}>Analyze</NavLink>
        <NavLink to="/history" className={navClass}>History</NavLink>
        {admin && <NavLink to="/admin" className={navClass}>Dashboard</NavLink>}
        {!userDisplay && <NavLink to="/login" className={navClass}>Login</NavLink>}
      </div>

      <div className="nav-right">
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