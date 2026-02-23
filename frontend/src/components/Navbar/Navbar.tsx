import { NavLink } from "react-router-dom";
import "./Navbar.css";

/**
 * Navbar component
 *
 * - Fixed at the top of the application
 * - Optimized for desktop and laptop screens
 * - Responsive for smaller laptop resolutions
 */
function Navbar() {
  return (
    <nav className="navbar">
      {/* Logo navigates to Home */}
      <NavLink to="/" className="logo">
        CRAI
      </NavLink>

      {/* Navigation links */}
      <div className="nav-links">
        <NavLink
          to="/"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Home
        </NavLink>

        <NavLink
          to="/analyze"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Analyze
        </NavLink>

        <NavLink
          to="/results"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Results
        </NavLink>

        <NavLink
          to="/login"
          className={({ isActive }) =>
            isActive ? "nav-link active" : "nav-link"
          }
        >
          Login
        </NavLink>
      </div>
    </nav>
  );
}

export default Navbar;