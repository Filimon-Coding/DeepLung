import { NavLink } from "react-router-dom";

export default function MyNavLink({ to, label }: { to: string; label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        [
          "text-sm font-semibold tracking-wide",
          isActive ? "underline underline-offset-8" : "hover:opacity-70",
        ].join(" ")
      }
    >
      {label}
    </NavLink>
  );
}