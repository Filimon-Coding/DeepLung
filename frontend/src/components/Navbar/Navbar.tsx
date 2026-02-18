import { NavLink } from "react-router-dom";
import "./Navbar.css";

/**
 * Navbar vises øverst på alle sider.
 * Bruker NavLink for å kunne style aktiv side.
 */
function Navbar() {
  return (
    <nav className="navbar">
      {/* Logo som leder til Home */}
      <NavLink to="/" className="logo">
        CRAI
      </NavLink>

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

        <NavLink to="/results" className={({isActive}) => isActive ? "nav-link active" : "nav-link"}>
        Results
        </NavLink>

        <NavLink to="/login" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
        Login
        </NavLink>
      </div>
    </nav>
  );
}

export default Navbar;