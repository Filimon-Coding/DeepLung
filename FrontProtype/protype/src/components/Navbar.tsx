import { Link, NavLink } from "react-router-dom";
import MyNavLink from "./NavLink";

export default function Navbar() {
  return (
    <header className="w-full border-b border-slate-200 bg-white">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center gap-4">
          <div className="w-10 h-10 rounded-full bg-slate-800" />
        </Link>

        <nav className="flex items-center gap-10">
          <MyNavLink to="/" label="HOME" />
          <MyNavLink to="/analyze" label="ANALYZE" />
          <MyNavLink to="/results" label="RESULTS" />
        </nav>

        <div className="text-sm font-semibold tracking-wide">
          <NavLink to="/login" className="hover:opacity-70">
            LOGIN
          </NavLink>
        </div>
      </div>
    </header>
  );
}